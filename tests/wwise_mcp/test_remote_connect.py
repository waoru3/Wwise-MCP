"""Tests for wwise_python_lib.remote_connect (TASK-81.11).

Pins URI, required "host" arg, optional appName/commandPort, the schema rule
that commandPort requires appName, uint16 bound on commandPort, the deliberate
absence of "notificationPort" (schema says "Unused"), response/None handling,
error wrap, shim forwarding, and COMMANDS doc (restriction + notificationPort note).
"""
from __future__ import annotations

import pytest

URI = "ak.wwise.core.remote.connect"


def test_uri_and_required_host_only(mock_waapi):
    import wwise_python_lib
    wwise_python_lib.remote_connect("127.0.0.1")
    call = mock_waapi.call_args
    assert call.args[0] == URI
    assert call.args[1] == {"host": "127.0.0.1"}


def test_app_name_and_command_port_included(mock_waapi):
    import wwise_python_lib
    wwise_python_lib.remote_connect("127.0.0.1", app_name="Unity", command_port=24024)
    assert mock_waapi.call_args.args[1] == {
        "host": "127.0.0.1", "appName": "Unity", "commandPort": 24024,
    }


def test_host_accepts_prof_path(mock_waapi):
    import wwise_python_lib
    wwise_python_lib.remote_connect(r"C:/captures/session.prof")
    assert mock_waapi.call_args.args[1] == {"host": r"C:/captures/session.prof"}


def test_notification_port_not_exposed():
    import inspect
    import wwise_python_lib
    sig = inspect.signature(wwise_python_lib.remote_connect)
    # Schema marks notificationPort "Unused"; the wrapper must not expose it.
    assert "notification_port" not in sig.parameters
    assert "notificationPort" not in sig.parameters


@pytest.mark.parametrize("bad", [None, "", "   ", 0, 1, [], {}, object()])
def test_invalid_host_rejected(mock_waapi, bad):
    import wwise_python_lib
    from wwise_python_lib import WwiseValidationError
    with pytest.raises(WwiseValidationError):
        wwise_python_lib.remote_connect(bad)
    mock_waapi.assert_not_called()


def test_command_port_requires_app_name(mock_waapi):
    import wwise_python_lib
    from wwise_python_lib import WwiseValidationError
    with pytest.raises(WwiseValidationError):
        wwise_python_lib.remote_connect("127.0.0.1", command_port=24024)
    mock_waapi.assert_not_called()


@pytest.mark.parametrize("bad", [-1, 65536, 70000, True, 1.5, "24024"])
def test_command_port_must_be_uint16(mock_waapi, bad):
    import wwise_python_lib
    from wwise_python_lib import WwiseValidationError
    with pytest.raises(WwiseValidationError):
        wwise_python_lib.remote_connect("127.0.0.1", app_name="Unity", command_port=bad)
    mock_waapi.assert_not_called()


def test_app_name_must_be_string(mock_waapi):
    import wwise_python_lib
    from wwise_python_lib import WwiseValidationError
    with pytest.raises(WwiseValidationError):
        wwise_python_lib.remote_connect("127.0.0.1", app_name=123)
    mock_waapi.assert_not_called()


def test_none_response_coerced_to_empty_dict(mock_waapi):
    import wwise_python_lib
    mock_waapi.return_value = None
    assert wwise_python_lib.remote_connect("127.0.0.1") == {}


def test_default_timeout_5_seconds(mock_waapi):
    import wwise_python_lib
    wwise_python_lib.remote_connect("127.0.0.1")
    assert mock_waapi.call_args.kwargs.get("timeout") == 5.0


def test_error_wrap_details(mock_waapi):
    import wwise_python_lib
    from wwise_python_lib import WwiseApiError
    mock_waapi.side_effect = RuntimeError("boom")
    with pytest.raises(WwiseApiError) as excinfo:
        wwise_python_lib.remote_connect("127.0.0.1", app_name="Unity", timeout=8.0)
    err = excinfo.value
    assert err.operation == URI
    assert err.details["error_type"] == "RuntimeError"
    assert err.details["host"] == "127.0.0.1"
    assert err.details["app_name"] == "Unity"
    assert err.details["command_port"] is None
    assert err.details["timeout"] == 8.0


def test_wwise_pylib_error_passthrough(mock_waapi):
    import wwise_python_lib
    from wwise_python_lib import WwisePyLibError
    sentinel = WwisePyLibError("inner")
    mock_waapi.side_effect = sentinel
    with pytest.raises(WwisePyLibError) as excinfo:
        wwise_python_lib.remote_connect("127.0.0.1")
    assert excinfo.value is sentinel


def test_library_docstring_restriction_note():
    import wwise_python_lib
    doc = wwise_python_lib.remote_connect.__doc__
    assert "userInterface" in doc
    assert "NOT commandLine" in doc


def test_shim_forwards_to_library(mock_waapi):
    import wwise_mcp
    wwise_mcp.remote_connect("127.0.0.1", app_name="Unity")
    call = mock_waapi.call_args
    assert call.args[0] == URI
    assert call.args[1] == {"host": "127.0.0.1", "appName": "Unity"}


def test_shim_forwards_custom_timeout(mock_waapi):
    import wwise_mcp
    wwise_mcp.remote_connect("127.0.0.1", app_name="Unity", command_port=24024, timeout=12.0)
    assert mock_waapi.call_args.kwargs.get("timeout") == 12.0
    assert mock_waapi.call_args.args[1] == {
        "host": "127.0.0.1", "appName": "Unity", "commandPort": 24024,
    }


def test_commands_entry_notes():
    import wwise_mcp
    entry = wwise_mcp.COMMANDS["remote_connect"]
    assert entry.func is wwise_mcp.remote_connect
    assert "connect" in entry.doc.lower()
    assert "userInterface" in entry.doc
    assert "NOT commandLine" in entry.doc
    assert "notificationPort" in entry.doc  # documents the deliberate omission

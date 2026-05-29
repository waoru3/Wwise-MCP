"""Tests for wwise_python_lib.remote_get_connection_status (TASK-81.11).

Pins the WAAPI URI, no-args call shape, response passthrough, None->{} coercion,
error wrapping, WwisePyLibError passthrough, the wwise_mcp shim forwarding, and
the COMMANDS docstring (incl. the userInterface-only restriction note).
"""
from __future__ import annotations

import pytest

URI = "ak.wwise.core.remote.getConnectionStatus"


def test_uri_and_empty_args(mock_waapi):
    import wwise_python_lib
    wwise_python_lib.remote_get_connection_status()
    assert mock_waapi.call_count == 1
    call = mock_waapi.call_args
    assert call.args[0] == URI
    assert call.args[1] == {}


def test_default_timeout_5_seconds(mock_waapi):
    import wwise_python_lib
    wwise_python_lib.remote_get_connection_status()
    assert mock_waapi.call_args.kwargs.get("timeout") == 5.0


def test_custom_timeout_forwarded(mock_waapi):
    import wwise_python_lib
    wwise_python_lib.remote_get_connection_status(timeout=12.0)
    assert mock_waapi.call_args.kwargs.get("timeout") == 12.0


def test_response_passthrough(mock_waapi):
    import wwise_python_lib
    payload = {
        "isConnected": True,
        "status": "Connected",
        "console": {
            "name": "Wwise",
            "platform": "Windows",
            "customPlatform": "Windows",
            "host": "127.0.0.1",
            "appName": "Unity",
        },
    }
    mock_waapi.return_value = payload
    assert wwise_python_lib.remote_get_connection_status() == payload


def test_none_response_raises(mock_waapi):
    """None is an anomaly -> raises WwiseApiError."""
    import wwise_python_lib
    from wwise_errors import WwiseApiError
    mock_waapi.return_value = None
    with pytest.raises(WwiseApiError):
        wwise_python_lib.remote_get_connection_status()


def test_error_wrap_details(mock_waapi):
    import wwise_python_lib
    from wwise_python_lib import WwiseApiError
    mock_waapi.side_effect = RuntimeError("boom")
    with pytest.raises(WwiseApiError) as excinfo:
        wwise_python_lib.remote_get_connection_status(timeout=7.5)
    err = excinfo.value
    assert err.operation == URI
    assert err.details["error_type"] == "RuntimeError"
    assert err.details["timeout"] == 7.5


def test_wwise_pylib_error_passthrough(mock_waapi):
    import wwise_python_lib
    from wwise_python_lib import WwisePyLibError
    sentinel = WwisePyLibError("inner")
    mock_waapi.side_effect = sentinel
    with pytest.raises(WwisePyLibError) as excinfo:
        wwise_python_lib.remote_get_connection_status()
    assert excinfo.value is sentinel


def test_shim_forwards_to_library(mock_waapi):
    import wwise_mcp
    mock_waapi.return_value = {}
    result = wwise_mcp.remote_get_connection_status()
    assert mock_waapi.call_args.args[0] == URI
    assert mock_waapi.call_args.args[1] == {}
    assert result == {}


def test_shim_forwards_custom_timeout(mock_waapi):
    import wwise_mcp
    wwise_mcp.remote_get_connection_status(timeout=12.0)
    assert mock_waapi.call_args.kwargs.get("timeout") == 12.0


def test_commands_entry_and_restriction_note():
    import wwise_mcp
    entry = wwise_mcp.COMMANDS["remote_get_connection_status"]
    assert entry.func is wwise_mcp.remote_get_connection_status
    assert "getConnectionStatus" in entry.doc
    # AC-NEW-1: the userInterface-only restriction is documented in both the
    # COMMANDS doc and the library docstring.
    assert "userInterface" in entry.doc
    assert "NOT commandLine" in entry.doc


def test_library_docstring_restriction_note():
    import wwise_python_lib
    doc = wwise_python_lib.remote_get_connection_status.__doc__
    assert doc is not None
    # AC-NEW-1: userInterface-only restriction is explicit in the lib docstring.
    assert "userInterface" in doc
    assert "NOT commandLine" in doc


@pytest.mark.parametrize("bad", [0, -1, float("nan"), float("inf"), True, "5"])
def test_invalid_timeout_rejected(mock_waapi, bad):
    import wwise_python_lib
    from wwise_python_lib import WwiseValidationError
    with pytest.raises(WwiseValidationError):
        wwise_python_lib.remote_get_connection_status(timeout=bad)
    mock_waapi.assert_not_called()

"""Tests for wwise_python_lib.remote_get_available_consoles (TASK-81.11)."""
from __future__ import annotations

import pytest

URI = "ak.wwise.core.remote.getAvailableConsoles"


def test_uri_and_empty_args(mock_waapi):
    import wwise_python_lib
    wwise_python_lib.remote_get_available_consoles()
    call = mock_waapi.call_args
    assert call.args[0] == URI
    assert call.args[1] == {}


def test_default_timeout_5_seconds(mock_waapi):
    import wwise_python_lib
    wwise_python_lib.remote_get_available_consoles()
    assert mock_waapi.call_args.kwargs.get("timeout") == 5.0


def test_custom_timeout_forwarded(mock_waapi):
    import wwise_python_lib
    wwise_python_lib.remote_get_available_consoles(timeout=12.0)
    assert mock_waapi.call_args.kwargs.get("timeout") == 12.0


def test_response_passthrough(mock_waapi):
    import wwise_python_lib
    payload = {"consoles": [{"name": "PC", "platform": "Windows", "host": "127.0.0.1",
                             "appName": "Unity", "customPlatform": "Windows", "commandPort": 24024}]}
    mock_waapi.return_value = payload
    assert wwise_python_lib.remote_get_available_consoles() == payload


def test_none_response_coerced_to_empty_consoles(mock_waapi):
    import wwise_python_lib
    mock_waapi.return_value = None
    # Array-shaped endpoint: coerce None to the empty-array container, not {}.
    assert wwise_python_lib.remote_get_available_consoles() == {"consoles": []}


def test_error_wrap_details(mock_waapi):
    import wwise_python_lib
    from wwise_python_lib import WwiseApiError
    mock_waapi.side_effect = RuntimeError("boom")
    with pytest.raises(WwiseApiError) as excinfo:
        wwise_python_lib.remote_get_available_consoles(timeout=9.0)
    assert excinfo.value.operation == URI
    assert excinfo.value.details["timeout"] == 9.0
    assert excinfo.value.details["error_type"] == "RuntimeError"


def test_wwise_pylib_error_passthrough(mock_waapi):
    import wwise_python_lib
    from wwise_python_lib import WwisePyLibError
    sentinel = WwisePyLibError("inner")
    mock_waapi.side_effect = sentinel
    with pytest.raises(WwisePyLibError) as excinfo:
        wwise_python_lib.remote_get_available_consoles()
    assert excinfo.value is sentinel


def test_library_docstring_restriction_note():
    import wwise_python_lib
    doc = wwise_python_lib.remote_get_available_consoles.__doc__
    assert "userInterface" in doc
    assert "NOT commandLine" in doc


def test_shim_forwards_to_library(mock_waapi):
    import wwise_mcp
    mock_waapi.return_value = {"consoles": []}
    result = wwise_mcp.remote_get_available_consoles()
    assert mock_waapi.call_args.args[0] == URI
    assert result == {"consoles": []}


def test_shim_forwards_custom_timeout(mock_waapi):
    import wwise_mcp
    wwise_mcp.remote_get_available_consoles(timeout=12.0)
    assert mock_waapi.call_args.kwargs.get("timeout") == 12.0


def test_commands_entry_and_restriction_note():
    import wwise_mcp
    entry = wwise_mcp.COMMANDS["remote_get_available_consoles"]
    assert entry.func is wwise_mcp.remote_get_available_consoles
    assert "getAvailableConsoles" in entry.doc
    assert "userInterface" in entry.doc
    assert "NOT commandLine" in entry.doc

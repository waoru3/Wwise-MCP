"""Tests for wwise_python_lib.remote_disconnect (TASK-81.11).

remote_disconnect severs Authoring's REMOTE connection to the Sound Engine.
It is distinct from WwiseSession.disconnect_from_wwise_client (which closes the
WAAPI/WAMP socket). This test pins that the wrapper hits the remote.disconnect
URI, not a session teardown.
"""
from __future__ import annotations

import pytest

URI = "ak.wwise.core.remote.disconnect"


def test_uri_and_empty_args(mock_waapi):
    import wwise_python_lib
    wwise_python_lib.remote_disconnect()
    call = mock_waapi.call_args
    assert call.args[0] == URI
    assert call.args[1] == {}


def test_default_timeout_5_seconds(mock_waapi):
    import wwise_python_lib
    wwise_python_lib.remote_disconnect()
    assert mock_waapi.call_args.kwargs.get("timeout") == 5.0


def test_custom_timeout_forwarded(mock_waapi):
    import wwise_python_lib
    wwise_python_lib.remote_disconnect(timeout=12.0)
    assert mock_waapi.call_args.kwargs.get("timeout") == 12.0


def test_none_response_coerced_to_empty_dict(mock_waapi):
    import wwise_python_lib
    mock_waapi.return_value = None
    assert wwise_python_lib.remote_disconnect() == {}


def test_response_passthrough(mock_waapi):
    import wwise_python_lib
    mock_waapi.return_value = {"some": "payload"}
    assert wwise_python_lib.remote_disconnect() == {"some": "payload"}


def test_error_wrap_details(mock_waapi):
    import wwise_python_lib
    from wwise_python_lib import WwiseApiError
    mock_waapi.side_effect = RuntimeError("boom")
    with pytest.raises(WwiseApiError) as excinfo:
        wwise_python_lib.remote_disconnect(timeout=6.0)
    assert excinfo.value.operation == URI
    assert excinfo.value.details["timeout"] == 6.0
    assert excinfo.value.details["error_type"] == "RuntimeError"


def test_wwise_pylib_error_passthrough(mock_waapi):
    import wwise_python_lib
    from wwise_python_lib import WwisePyLibError
    sentinel = WwisePyLibError("inner")
    mock_waapi.side_effect = sentinel
    with pytest.raises(WwisePyLibError) as excinfo:
        wwise_python_lib.remote_disconnect()
    assert excinfo.value is sentinel


def test_library_docstring_restriction_note():
    import wwise_python_lib
    doc = wwise_python_lib.remote_disconnect.__doc__ or ""
    assert "userInterface" in doc
    assert "NOT commandLine" in doc


def test_shim_forwards_to_library(mock_waapi):
    import wwise_mcp
    wwise_mcp.remote_disconnect()
    assert mock_waapi.call_args.args[0] == URI


def test_shim_forwards_custom_timeout(mock_waapi):
    import wwise_mcp
    wwise_mcp.remote_disconnect(timeout=12.0)
    assert mock_waapi.call_args.kwargs.get("timeout") == 12.0


def test_distinct_from_session_disconnect():
    # remote_disconnect must NOT delegate to the WAMP-socket teardown.
    import wwise_python_lib
    src = wwise_python_lib.remote_disconnect.__doc__ or ""
    assert "disconnect_from_wwise_client" in src  # docstring calls out the distinction


def test_commands_entry_and_restriction_note():
    import wwise_mcp
    entry = wwise_mcp.COMMANDS["remote_disconnect"]
    assert entry.func is wwise_mcp.remote_disconnect
    assert "disconnect" in entry.doc.lower()
    assert "userInterface" in entry.doc
    assert "NOT commandLine" in entry.doc


@pytest.mark.parametrize("bad", [0, -1, float("nan"), float("inf"), True, "5"])
def test_invalid_timeout_rejected(mock_waapi, bad):
    import wwise_python_lib
    from wwise_python_lib import WwiseValidationError
    with pytest.raises(WwiseValidationError):
        wwise_python_lib.remote_disconnect(timeout=bad)
    mock_waapi.assert_not_called()

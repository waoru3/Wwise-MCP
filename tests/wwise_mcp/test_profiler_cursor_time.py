"""Tests for profiler_get_cursor_time.

Covers SDD Task 2 of TASK-81.10. The wrapper is a thin pass-through to
ak.wwise.core.profiler.getCursorTime with inline cursor validation (not via
_validate_profiler_time, since the param is a `cursor` selector, not a `time`).
"""
from __future__ import annotations

import pytest


def _find_call(mock_waapi, uri):
    for call in mock_waapi.call_args_list:
        if call.args and call.args[0] == uri:
            return call
    raise AssertionError(
        f"{uri} not in call_args_list: "
        f"{[c.args for c in mock_waapi.call_args_list]}"
    )


# ---------------------------------------------------------------------------
# URI + args shape
# ---------------------------------------------------------------------------

def test_get_cursor_time_uses_correct_uri_and_args_capture(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_get_cursor_time("capture")

    call = _find_call(mock_waapi, "ak.wwise.core.profiler.getCursorTime")
    assert call.args[1] == {"cursor": "capture"}


def test_get_cursor_time_uses_correct_uri_and_args_user(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_get_cursor_time("user")

    call = _find_call(mock_waapi, "ak.wwise.core.profiler.getCursorTime")
    assert call.args[1] == {"cursor": "user"}


def test_get_cursor_time_defaults_to_capture(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_get_cursor_time()

    call = _find_call(mock_waapi, "ak.wwise.core.profiler.getCursorTime")
    assert call.args[1] == {"cursor": "capture"}


def test_get_cursor_time_no_options_kwarg(mock_waapi):
    """Reader endpoint takes no options dict."""
    import wwise_python_lib

    wwise_python_lib.profiler_get_cursor_time("capture")

    call = _find_call(mock_waapi, "ak.wwise.core.profiler.getCursorTime")
    assert call.kwargs == {}


# ---------------------------------------------------------------------------
# Validation (inline, not via _validate_profiler_time)
# ---------------------------------------------------------------------------

def test_get_cursor_time_rejects_invalid_cursor(mock_waapi):
    import pytest

    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="cursor must be one of"):
        wwise_python_lib.profiler_get_cursor_time("now")

    # WAAPI must not be called when validation fails.
    assert not any(
        c.args and c.args[0] == "ak.wwise.core.profiler.getCursorTime"
        for c in mock_waapi.call_args_list
    )


def test_get_cursor_time_rejects_empty_string(mock_waapi):
    import pytest

    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="cursor must be one of"):
        wwise_python_lib.profiler_get_cursor_time("")


@pytest.mark.parametrize("bad_cursor", [[], {}, None, 42, ["capture"]])
def test_get_cursor_time_rejects_unhashable_or_wrong_type(mock_waapi, bad_cursor):
    """Unhashable / non-str inputs must surface as WwiseValidationError, not TypeError."""
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="cursor must be one of"):
        wwise_python_lib.profiler_get_cursor_time(cursor=bad_cursor)


def test_get_cursor_time_wraps_waapi_failure_as_WwiseApiError(mocker):
    """Generic WAAPI exception must be wrapped as WwiseApiError with operation + details."""
    from wwise_errors import WwiseApiError
    import wwise_python_lib

    mocker.patch.object(
        wwise_python_lib,
        "waapi_call",
        side_effect=RuntimeError("boom"),
    )

    with pytest.raises(WwiseApiError) as exc_info:
        wwise_python_lib.profiler_get_cursor_time(cursor="capture")

    assert exc_info.value.operation == "ak.wwise.core.profiler.getCursorTime"
    assert exc_info.value.details["error_type"] == "RuntimeError"
    assert exc_info.value.details["cursor"] == "capture"


# ---------------------------------------------------------------------------
# Response handling
# ---------------------------------------------------------------------------

def test_get_cursor_time_returns_waapi_response(mock_waapi):
    import wwise_python_lib

    mock_waapi.return_value = {"return": 4321}

    result = wwise_python_lib.profiler_get_cursor_time("capture")

    assert result == {"return": 4321}


def test_get_cursor_time_normalizes_none_to_empty_dict(mock_waapi):
    """Defensive: WAAPI sometimes returns None; wrapper normalises to {}."""
    import wwise_python_lib

    mock_waapi.return_value = None

    assert wwise_python_lib.profiler_get_cursor_time("capture") == {}


# ---------------------------------------------------------------------------
# MCP shim delegates to library
# ---------------------------------------------------------------------------

def test_mcp_get_cursor_time_wrapper_delegates(mock_waapi):
    import wwise_mcp

    mock_waapi.return_value = {"return": 777}

    assert wwise_mcp.profiler_get_cursor_time("capture") == {"return": 777}
    _find_call(mock_waapi, "ak.wwise.core.profiler.getCursorTime")


def test_mcp_get_cursor_time_wrapper_defaults_to_capture(mock_waapi):
    import wwise_mcp

    mock_waapi.return_value = {"return": 0}

    wwise_mcp.profiler_get_cursor_time()

    call = _find_call(mock_waapi, "ak.wwise.core.profiler.getCursorTime")
    assert call.args[1] == {"cursor": "capture"}


def test_mcp_get_cursor_time_wrapper_passes_cursor_through(mock_waapi):
    """Regression: shim must forward cursor arg, not hardcode 'capture'."""
    import wwise_mcp

    mock_waapi.return_value = {"return": 99}

    wwise_mcp.profiler_get_cursor_time("user")

    call = _find_call(mock_waapi, "ak.wwise.core.profiler.getCursorTime")
    assert call.args[1] == {"cursor": "user"}


# ---------------------------------------------------------------------------
# COMMANDS registry
# ---------------------------------------------------------------------------

def test_get_cursor_time_registered_in_COMMANDS():
    import wwise_mcp

    assert "profiler_get_cursor_time" in wwise_mcp.COMMANDS
    entry = wwise_mcp.COMMANDS["profiler_get_cursor_time"]
    assert entry.func is wwise_mcp.profiler_get_cursor_time
    assert "cursor" in entry.doc
    assert "'capture'" in entry.doc
    assert "'user'" in entry.doc

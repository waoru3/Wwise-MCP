"""Tests for profiler_start_capture / profiler_stop_capture.

Covers SDD Task 1 of TASK-81.10. Both wrappers are thin pass-throughs to
ak.wwise.core.profiler.startCapture / stopCapture with no args, no options,
and no input validation (the `time` cursor / `_validate_profiler_time` helper
is for the reader endpoints landing in later tasks).
"""
from __future__ import annotations


def _find_call(mock_waapi, uri):
    for call in mock_waapi.call_args_list:
        if call.args and call.args[0] == uri:
            return call
    raise AssertionError(
        f"{uri} not in call_args_list: "
        f"{[c.args for c in mock_waapi.call_args_list]}"
    )


# ---------------------------------------------------------------------------
# profiler_start_capture
# ---------------------------------------------------------------------------

def test_start_capture_uses_correct_uri_and_empty_args(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_start_capture()

    call = _find_call(mock_waapi, "ak.wwise.core.profiler.startCapture")
    assert call.args[1] == {}


def test_start_capture_no_options_kwarg(mock_waapi):
    """Capture-control endpoints take no options dict (reader-only feature)."""
    import wwise_python_lib

    wwise_python_lib.profiler_start_capture()

    call = _find_call(mock_waapi, "ak.wwise.core.profiler.startCapture")
    assert call.kwargs == {}


def test_start_capture_returns_waapi_response(mock_waapi):
    import wwise_python_lib

    mock_waapi.return_value = {"return": 1234}

    result = wwise_python_lib.profiler_start_capture()

    assert result == {"return": 1234}


def test_start_capture_normalizes_none_to_empty_dict(mock_waapi):
    """Defensive: WAAPI sometimes returns None; wrapper normalises to {}."""
    import wwise_python_lib

    mock_waapi.return_value = None

    assert wwise_python_lib.profiler_start_capture() == {}


# ---------------------------------------------------------------------------
# profiler_stop_capture
# ---------------------------------------------------------------------------

def test_stop_capture_uses_correct_uri_and_empty_args(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_stop_capture()

    call = _find_call(mock_waapi, "ak.wwise.core.profiler.stopCapture")
    assert call.args[1] == {}


def test_stop_capture_no_options_kwarg(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_stop_capture()

    call = _find_call(mock_waapi, "ak.wwise.core.profiler.stopCapture")
    assert call.kwargs == {}


def test_stop_capture_returns_waapi_response(mock_waapi):
    import wwise_python_lib

    mock_waapi.return_value = {"return": 5678}

    result = wwise_python_lib.profiler_stop_capture()

    assert result == {"return": 5678}


def test_stop_capture_normalizes_none_to_empty_dict(mock_waapi):
    import wwise_python_lib

    mock_waapi.return_value = None

    assert wwise_python_lib.profiler_stop_capture() == {}


# ---------------------------------------------------------------------------
# MCP shim delegates to library
# ---------------------------------------------------------------------------

def test_mcp_start_wrapper_delegates(mock_waapi):
    import wwise_mcp

    mock_waapi.return_value = {"return": 42}

    assert wwise_mcp.profiler_start_capture() == {"return": 42}
    _find_call(mock_waapi, "ak.wwise.core.profiler.startCapture")


def test_mcp_stop_wrapper_delegates(mock_waapi):
    import wwise_mcp

    mock_waapi.return_value = {"return": 99}

    assert wwise_mcp.profiler_stop_capture() == {"return": 99}
    _find_call(mock_waapi, "ak.wwise.core.profiler.stopCapture")


# ---------------------------------------------------------------------------
# COMMANDS registry
# ---------------------------------------------------------------------------

def test_start_capture_registered_in_COMMANDS():
    import wwise_mcp

    assert "profiler_start_capture" in wwise_mcp.COMMANDS
    entry = wwise_mcp.COMMANDS["profiler_start_capture"]
    assert entry.func is wwise_mcp.profiler_start_capture
    assert "Wwise Profiler" in entry.doc
    assert "Args: None" in entry.doc


def test_stop_capture_registered_in_COMMANDS():
    import wwise_mcp

    assert "profiler_stop_capture" in wwise_mcp.COMMANDS
    entry = wwise_mcp.COMMANDS["profiler_stop_capture"]
    assert entry.func is wwise_mcp.profiler_stop_capture
    assert "Stop" in entry.doc
    assert "Args: None" in entry.doc


# ---------------------------------------------------------------------------
# Helper / cursor frozenset module-level definitions (Task 1 foundation
# for later reader tasks).
# ---------------------------------------------------------------------------

def test_profiler_cursors_frozenset_exact():
    import wwise_python_lib

    assert wwise_python_lib._PROFILER_CURSORS == frozenset({"user", "capture"})


def test_validate_profiler_time_accepts_non_negative_int():
    import wwise_python_lib

    wwise_python_lib._validate_profiler_time(0)
    wwise_python_lib._validate_profiler_time(1234)


def test_validate_profiler_time_accepts_cursor_strings():
    import wwise_python_lib

    wwise_python_lib._validate_profiler_time("user")
    wwise_python_lib._validate_profiler_time("capture")


def test_validate_profiler_time_rejects_negative_int():
    import pytest

    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match=">= 0"):
        wwise_python_lib._validate_profiler_time(-1)


def test_validate_profiler_time_rejects_bool():
    import pytest

    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="bool"):
        wwise_python_lib._validate_profiler_time(True)


def test_validate_profiler_time_rejects_unknown_string():
    import pytest

    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="time string"):
        wwise_python_lib._validate_profiler_time("now")


def test_validate_profiler_time_rejects_float():
    import pytest

    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="int"):
        wwise_python_lib._validate_profiler_time(1.5)

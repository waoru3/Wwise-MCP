"""Tests for wwise_python_lib.profiler_save_capture (TASK-81.10 Task 10).

Pins the WAAPI URI (saveCapture, NOT saveProfilerCapture - a common
mis-naming in older docs), the argument key ("file"), file_path validation,
response passthrough (None coerced to empty dict), error wrapping details,
WwisePyLibError passthrough, the wwise_mcp shim forwarding, and the
COMMANDS docstring URI correction.
"""
from __future__ import annotations

import pytest


URI = "ak.wwise.core.profiler.saveCapture"


def test_uri_is_save_capture_not_save_profiler_capture(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_save_capture(r"C:/tmp/capture.prof")

    assert mock_waapi.call_count == 1
    call = mock_waapi.call_args
    assert call.args[0] == URI
    assert call.args[0] != "ak.wwise.core.profiler.saveProfilerCapture"


def test_args_use_file_key(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_save_capture(r"C:/tmp/capture.prof")

    call = mock_waapi.call_args
    # WAAPI arg key is "file", NOT "file_path".
    assert call.args[1] == {"file": r"C:/tmp/capture.prof"}


def test_default_timeout_5_seconds(mock_waapi):
    """Default timeout must be 5.0s (NOT WwiseSession's 1.0s default) - saving
    a .prof capture is disk I/O that can realistically exceed 1s."""
    import wwise_python_lib

    wwise_python_lib.profiler_save_capture(r"C:/tmp/capture.prof")

    call = mock_waapi.call_args
    assert call.kwargs.get("timeout") == 5.0


def test_custom_timeout_forwarded(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_save_capture(r"C:/tmp/capture.prof", timeout=30.0)

    call = mock_waapi.call_args
    assert call.kwargs.get("timeout") == 30.0


@pytest.mark.parametrize("bad", [None, 0, 1, 1.5, [], {}, b"bytes", object()])
def test_non_string_file_path_rejected(mock_waapi, bad):
    import wwise_python_lib
    from wwise_python_lib import WwiseValidationError

    with pytest.raises(WwiseValidationError):
        wwise_python_lib.profiler_save_capture(bad)
    mock_waapi.assert_not_called()


def test_empty_string_rejected(mock_waapi):
    import wwise_python_lib
    from wwise_python_lib import WwiseValidationError

    with pytest.raises(WwiseValidationError):
        wwise_python_lib.profiler_save_capture("")
    mock_waapi.assert_not_called()


def test_whitespace_only_rejected(mock_waapi):
    import wwise_python_lib
    from wwise_python_lib import WwiseValidationError

    with pytest.raises(WwiseValidationError):
        wwise_python_lib.profiler_save_capture("   \t\n  ")
    mock_waapi.assert_not_called()


def test_response_passthrough(mock_waapi):
    import wwise_python_lib

    mock_waapi.return_value = {"some": "payload"}
    result = wwise_python_lib.profiler_save_capture(r"C:/tmp/capture.prof")
    assert result == {"some": "payload"}


def test_none_response_raises(mock_waapi):
    """None is an anomaly -> raises WwiseApiError."""
    import wwise_python_lib
    from wwise_errors import WwiseApiError

    mock_waapi.return_value = None
    with pytest.raises(WwiseApiError):
        wwise_python_lib.profiler_save_capture(r"C:/tmp/capture.prof")


def test_error_wrap_details(mock_waapi):
    import wwise_python_lib
    from wwise_python_lib import WwiseApiError

    mock_waapi.side_effect = RuntimeError("boom")
    with pytest.raises(WwiseApiError) as excinfo:
        wwise_python_lib.profiler_save_capture(r"C:/tmp/capture.prof", timeout=7.5)

    err = excinfo.value
    assert err.operation == URI
    assert err.details["error_type"] == "RuntimeError"
    assert err.details["file_path"] == r"C:/tmp/capture.prof"
    assert err.details["timeout"] == 7.5


def test_wwise_pylib_error_passthrough(mock_waapi):
    import wwise_python_lib
    from wwise_python_lib import WwisePyLibError

    sentinel = WwisePyLibError("inner pylib failure")
    mock_waapi.side_effect = sentinel
    with pytest.raises(WwisePyLibError) as excinfo:
        wwise_python_lib.profiler_save_capture(r"C:/tmp/capture.prof")
    # Must NOT be wrapped in WwiseApiError - already a WwisePyLibError.
    assert excinfo.value is sentinel


def test_shim_forwards_to_library(mock_waapi):
    import wwise_mcp

    result = wwise_mcp.profiler_save_capture(r"C:/tmp/capture.prof")
    assert mock_waapi.call_count == 1
    assert mock_waapi.call_args.args[0] == URI
    assert mock_waapi.call_args.args[1] == {"file": r"C:/tmp/capture.prof"}
    # Default timeout flows through the shim to the WAAPI call.
    assert mock_waapi.call_args.kwargs.get("timeout") == 5.0
    # Default mock_waapi returns {}, library coerces None->{} but {} stays {}.
    assert result == {}


def test_shim_forwards_custom_timeout(mock_waapi):
    """wwise_mcp.profiler_save_capture must forward timeout unchanged."""
    import wwise_mcp

    wwise_mcp.profiler_save_capture(r"C:/tmp/capture.prof", timeout=15.0)

    call = mock_waapi.call_args
    assert call.args[0] == URI
    assert call.kwargs["timeout"] == 15.0


@pytest.mark.parametrize("bad_timeout", [0, 0.0, -1, -0.5, float("inf"), float("-inf"), float("nan"), True, False, None, "5", []])
def test_invalid_timeout_rejected(mock_waapi, bad_timeout):
    """Per PR #10 review: zero / negative / non-finite / non-numeric timeout
    must raise WwiseValidationError before reaching WAAPI (which would either
    fail immediately or wait undefined). Booleans rejected even though
    isinstance(True, int) is True - bool is not a sensible timeout value."""
    import wwise_python_lib
    from wwise_python_lib import WwiseValidationError

    with pytest.raises(WwiseValidationError):
        wwise_python_lib.profiler_save_capture(r"C:/tmp/capture.prof", timeout=bad_timeout)
    mock_waapi.assert_not_called()


def test_relative_file_path_rejected(mock_waapi):
    """Per PR #10 review: Wwise Authoring's cwd is its own install dir, not the
    caller's; relative paths land in unexpected locations or fail silently. The
    wrapper docstring already required absolute; this enforces it programmatically."""
    import wwise_python_lib
    from wwise_python_lib import WwiseValidationError

    with pytest.raises(WwiseValidationError):
        wwise_python_lib.profiler_save_capture("tmp/relative/capture.prof")
    mock_waapi.assert_not_called()


def test_whitespace_padded_absolute_path_accepted(mock_waapi):
    """Leading/trailing whitespace is stripped before the absolute check, then
    passed to WAAPI in trimmed form. Validates the strip() ordering."""
    import wwise_python_lib

    wwise_python_lib.profiler_save_capture("  C:/tmp/capture.prof  ")
    call = mock_waapi.call_args
    assert call.args[1] == {"file": r"C:/tmp/capture.prof"}


def test_commands_entry_mentions_save_capture_uri():
    import wwise_mcp

    entry = wwise_mcp.COMMANDS["profiler_save_capture"]
    assert entry.func is wwise_mcp.profiler_save_capture
    assert "saveCapture" in entry.doc
    # The URI-correction note pins the common mis-naming explicitly.
    assert "saveProfilerCapture" in entry.doc
    # Timeout kwarg is documented (default 5.0s; WwiseSession's 1.0s is too short for disk I/O).
    assert "timeout" in entry.doc

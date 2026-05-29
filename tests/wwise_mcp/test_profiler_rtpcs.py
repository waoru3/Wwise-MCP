"""Tests for profiler_get_rtpcs - Task 9 of TASK-81.10.

Validates the WAAPI getRTPCs wrapper: URI, args shape (time only,
no options field), timeout passthrough, time validation, error-details
dict (incl timeout), None-response raising WwiseApiError, shim
delegation, and COMMANDS registration.
"""
from __future__ import annotations

import pytest


def _find_get_rtpcs_call(mock_waapi):
    for call in mock_waapi.call_args_list:
        if call.args and call.args[0] == "ak.wwise.core.profiler.getRTPCs":
            return call
    raise AssertionError(
        "ak.wwise.core.profiler.getRTPCs not in call_args_list: "
        f"{[c.args for c in mock_waapi.call_args_list]}"
    )


# ---------------------------------------------------------------------------
# URI + default args
# ---------------------------------------------------------------------------

def test_uri_is_exactly_getRTPCs(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_get_rtpcs()
    call = _find_get_rtpcs_call(mock_waapi)
    assert call.args[0] == "ak.wwise.core.profiler.getRTPCs"


def test_default_args_only_carry_time_capture(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_get_rtpcs()
    call = _find_get_rtpcs_call(mock_waapi)
    assert call.args[1] == {"time": "capture"}
    # Endpoint takes no return-field whitelist - no options kwarg sent.
    assert "options" not in call.kwargs or call.kwargs.get("options") is None
    assert call.kwargs.get("timeout") == 5.0


def test_no_options_field_ever_sent(mock_waapi):
    """Schema fixes the response shape - we must never send options."""
    import wwise_python_lib

    wwise_python_lib.profiler_get_rtpcs(time=500, timeout=2.0)
    call = _find_get_rtpcs_call(mock_waapi)
    assert "options" not in call.kwargs or call.kwargs.get("options") is None


def test_time_user_accepted(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_get_rtpcs(time="user")
    call = _find_get_rtpcs_call(mock_waapi)
    assert call.args[1] == {"time": "user"}


def test_time_int_accepted(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_get_rtpcs(time=12345)
    call = _find_get_rtpcs_call(mock_waapi)
    assert call.args[1] == {"time": 12345}


def test_time_invalid_string_rejected(mock_waapi):
    import wwise_python_lib
    from wwise_python_lib import WwiseValidationError

    with pytest.raises(WwiseValidationError):
        wwise_python_lib.profiler_get_rtpcs(time="bogus")
    assert mock_waapi.call_count == 0


def test_custom_timeout_forwarded(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_get_rtpcs(timeout=12.5)
    call = _find_get_rtpcs_call(mock_waapi)
    assert call.kwargs.get("timeout") == 12.5


# ---------------------------------------------------------------------------
# Error details / response shaping
# ---------------------------------------------------------------------------

def test_waapi_exception_wrapped_with_full_details(mock_waapi):
    import wwise_python_lib
    from wwise_python_lib import WwiseApiError

    mock_waapi.side_effect = RuntimeError("connection lost")

    with pytest.raises(WwiseApiError) as exc:
        wwise_python_lib.profiler_get_rtpcs(time=500, timeout=3.0)
    details = exc.value.details
    assert details["error_type"] == "RuntimeError"
    assert details["time"] == 500
    assert details["timeout"] == 3.0
    assert exc.value.operation == "ak.wwise.core.profiler.getRTPCs"


def test_none_response_raises(mock_waapi):
    """None is an anomaly -> raises WwiseApiError."""
    import wwise_python_lib
    from wwise_errors import WwiseApiError

    mock_waapi.return_value = None
    with pytest.raises(WwiseApiError):
        wwise_python_lib.profiler_get_rtpcs()


def test_response_passed_through(mock_waapi):
    import wwise_python_lib

    payload = {"return": [
        {"id": "{11111111-2222-3333-4444-555555555555}",
         "name": "Reflections_MixLevel",
         "gameObjectId": -1,
         "value": 0.0},
    ]}
    mock_waapi.return_value = payload
    assert wwise_python_lib.profiler_get_rtpcs() is payload


def test_existing_validation_error_passes_through(mock_waapi):
    """WwisePyLibError raised inside the try block must not be re-wrapped."""
    import wwise_python_lib
    from wwise_python_lib import WwiseValidationError, WwisePyLibError

    mock_waapi.side_effect = WwiseValidationError("inner")

    with pytest.raises(WwisePyLibError) as exc:
        wwise_python_lib.profiler_get_rtpcs()
    assert isinstance(exc.value, WwiseValidationError)
    assert str(exc.value) == "inner"


# ---------------------------------------------------------------------------
# Shim + COMMANDS registration
# ---------------------------------------------------------------------------

def test_shim_forwards_time_and_timeout(mock_waapi):
    """wwise_mcp.profiler_get_rtpcs must forward time + timeout unchanged."""
    import wwise_mcp

    wwise_mcp.profiler_get_rtpcs(time=200, timeout=4.5)
    call = _find_get_rtpcs_call(mock_waapi)
    assert call.args[0] == "ak.wwise.core.profiler.getRTPCs"
    assert call.args[1] == {"time": 200}
    assert call.kwargs["timeout"] == 4.5
    assert "options" not in call.kwargs or call.kwargs.get("options") is None


def test_command_registered_in_COMMANDS():
    import wwise_mcp

    assert "profiler_get_rtpcs" in wwise_mcp.COMMANDS
    cmd = wwise_mcp.COMMANDS["profiler_get_rtpcs"]
    assert cmd.func is wwise_mcp.profiler_get_rtpcs


def test_commands_doc_mentions_reflections_mixlevel_example():
    """COMMANDS doc should advertise Reflections_MixLevel as the
    per-feature mute use case (plan rationale)."""
    import wwise_mcp

    doc = wwise_mcp.COMMANDS["profiler_get_rtpcs"].doc
    assert "Reflections_MixLevel" in doc

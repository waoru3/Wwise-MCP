"""Tests for profiler_get_voices.

Covers SDD Task 4 of TASK-81.10. The wrapper is a reader endpoint that posts
to ak.wwise.core.profiler.getVoices with:
- args.time (int ms or 'user'/'capture'), optional args.voicePipelineID
- options.return = return_fields (whitelist subset) when provided
- timeout kwarg forwarded to waapi_call (default 5.0s, 5x global)

This is the first wrapper carrying a uint32 cap on a pipeline ID. Validation
is checked exhaustively to ensure TypeError can never leak for unhashable or
wrong-type inputs.
"""
from __future__ import annotations

import pytest


URI = "ak.wwise.core.profiler.getVoices"


def _find_call(mock_waapi, uri):
    for call in mock_waapi.call_args_list:
        if call.args and call.args[0] == uri:
            return call
    raise AssertionError(
        f"{uri} not in call_args_list: "
        f"{[c.args for c in mock_waapi.call_args_list]}"
    )


def _assert_not_called(mock_waapi):
    mock_waapi.assert_not_called()


# ---------------------------------------------------------------------------
# URI + args shape
# ---------------------------------------------------------------------------

def test_get_voices_uses_correct_uri(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_get_voices()

    call = _find_call(mock_waapi, URI)
    assert call.args[0] == URI


def test_get_voices_default_args_bare_time_capture(mock_waapi):
    """Default call: time='capture', no voicePipelineID, no options."""
    import wwise_python_lib

    wwise_python_lib.profiler_get_voices()

    call = _find_call(mock_waapi, URI)
    assert call.args[1] == {"time": "capture"}


def test_get_voices_time_user_string(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_get_voices(time="user")

    call = _find_call(mock_waapi, URI)
    assert call.args[1] == {"time": "user"}


def test_get_voices_time_int_ms(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_get_voices(time=12345)

    call = _find_call(mock_waapi, URI)
    assert call.args[1] == {"time": 12345}


def test_get_voices_with_voice_pipeline_id_emits_voicePipelineID(mock_waapi):
    """voice_pipeline_id maps to camelCase voicePipelineID in args."""
    import wwise_python_lib

    wwise_python_lib.profiler_get_voices(voice_pipeline_id=42)

    call = _find_call(mock_waapi, URI)
    assert call.args[1] == {"time": "capture", "voicePipelineID": 42}


def test_get_voices_with_return_fields_emits_options_return(mock_waapi):
    """return_fields populates options={'return': [...]}."""
    import wwise_python_lib

    wwise_python_lib.profiler_get_voices(
        return_fields=["pipelineID", "baseVolume"],
    )

    call = _find_call(mock_waapi, URI)
    assert call.args[1] == {"time": "capture"}
    assert call.kwargs["options"] == {"return": ["pipelineID", "baseVolume"]}


def test_get_voices_no_return_fields_omits_options(mock_waapi):
    """Default (no return_fields) must pass options=None to waapi_call."""
    import wwise_python_lib

    wwise_python_lib.profiler_get_voices()

    call = _find_call(mock_waapi, URI)
    assert call.kwargs.get("options") is None


def test_get_voices_timeout_kwarg_default_5_seconds(mock_waapi):
    """Default timeout is 5.0s (5x global default)."""
    import wwise_python_lib

    wwise_python_lib.profiler_get_voices()

    call = _find_call(mock_waapi, URI)
    assert call.kwargs["timeout"] == 5.0


def test_get_voices_timeout_kwarg_custom(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_get_voices(timeout=12.5)

    call = _find_call(mock_waapi, URI)
    assert call.kwargs["timeout"] == 12.5


def test_get_voices_combines_all_args(mock_waapi):
    """All non-default args together: time + voicePipelineID + options + timeout."""
    import wwise_python_lib

    wwise_python_lib.profiler_get_voices(
        time=999,
        voice_pipeline_id=7,
        return_fields=["pipelineID", "gameObjectName", "isVirtual"],
        timeout=10.0,
    )

    call = _find_call(mock_waapi, URI)
    assert call.args[1] == {"time": 999, "voicePipelineID": 7}
    assert call.kwargs["options"] == {
        "return": ["pipelineID", "gameObjectName", "isVirtual"]
    }
    assert call.kwargs["timeout"] == 10.0


# ---------------------------------------------------------------------------
# time validation (via _validate_profiler_time)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("good_time", [0, 1, 12345, "user", "capture"])
def test_get_voices_accepts_valid_times(mock_waapi, good_time):
    import wwise_python_lib

    wwise_python_lib.profiler_get_voices(time=good_time)
    _find_call(mock_waapi, URI)


def test_get_voices_rejects_bool_time(mock_waapi):
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="time must be"):
        wwise_python_lib.profiler_get_voices(time=True)
    _assert_not_called(mock_waapi)


def test_get_voices_rejects_negative_int_time(mock_waapi):
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="time must be >= 0"):
        wwise_python_lib.profiler_get_voices(time=-1)
    _assert_not_called(mock_waapi)


def test_get_voices_rejects_float_time(mock_waapi):
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="time must be"):
        wwise_python_lib.profiler_get_voices(time=1.5)
    _assert_not_called(mock_waapi)


def test_get_voices_rejects_unknown_string_time(mock_waapi):
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="time string must be one of"):
        wwise_python_lib.profiler_get_voices(time="now")
    _assert_not_called(mock_waapi)


@pytest.mark.parametrize("bad_time", [[], {}, None, (1,)])
def test_get_voices_rejects_unhashable_or_wrong_type_time(mock_waapi, bad_time):
    """Unhashable / wrong type must surface as WwiseValidationError, never TypeError."""
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="time must be"):
        wwise_python_lib.profiler_get_voices(time=bad_time)
    _assert_not_called(mock_waapi)


# ---------------------------------------------------------------------------
# voice_pipeline_id validation (uint32 boundary)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("good_id", [0, 1, 0xFFFFFFFF])
def test_get_voices_accepts_valid_pipeline_id_inclusive_bounds(mock_waapi, good_id):
    """Boundary: 0 and 0xFFFFFFFF inclusive must be accepted."""
    import wwise_python_lib

    wwise_python_lib.profiler_get_voices(voice_pipeline_id=good_id)

    call = _find_call(mock_waapi, URI)
    assert call.args[1]["voicePipelineID"] == good_id


def test_get_voices_rejects_pipeline_id_above_uint32(mock_waapi):
    """Boundary: 0x100000000 must be rejected (mandatory Style guardrail)."""
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="voice_pipeline_id"):
        wwise_python_lib.profiler_get_voices(voice_pipeline_id=0x100000000)
    _assert_not_called(mock_waapi)


def test_get_voices_rejects_negative_pipeline_id(mock_waapi):
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="voice_pipeline_id"):
        wwise_python_lib.profiler_get_voices(voice_pipeline_id=-1)
    _assert_not_called(mock_waapi)


def test_get_voices_rejects_bool_pipeline_id(mock_waapi):
    """bool isinstance(int) trap: True/False must NOT be accepted as a pipeline ID."""
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="voice_pipeline_id must be an int"):
        wwise_python_lib.profiler_get_voices(voice_pipeline_id=True)
    _assert_not_called(mock_waapi)


@pytest.mark.parametrize("bad", [1.5, "42", [], {}, (1,)])
def test_get_voices_rejects_wrong_type_pipeline_id(mock_waapi, bad):
    """Float / str / unhashable / tuple must surface as WwiseValidationError."""
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="voice_pipeline_id must be an int"):
        wwise_python_lib.profiler_get_voices(voice_pipeline_id=bad)
    _assert_not_called(mock_waapi)


# ---------------------------------------------------------------------------
# return_fields validation
# ---------------------------------------------------------------------------

def test_get_voices_accepts_single_return_field(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_get_voices(return_fields=["pipelineID"])

    call = _find_call(mock_waapi, URI)
    assert call.kwargs["options"] == {"return": ["pipelineID"]}


def test_get_voices_accepts_all_whitelisted_return_fields(mock_waapi):
    """Smoke: every member of _VOICE_RETURN_FIELDS must validate."""
    import wwise_python_lib

    all_fields = sorted(wwise_python_lib._VOICE_RETURN_FIELDS)
    wwise_python_lib.profiler_get_voices(return_fields=all_fields)

    call = _find_call(mock_waapi, URI)
    assert call.kwargs["options"] == {"return": all_fields}


def test_get_voices_rejects_empty_return_fields(mock_waapi):
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="non-empty list"):
        wwise_python_lib.profiler_get_voices(return_fields=[])
    _assert_not_called(mock_waapi)


@pytest.mark.parametrize("bad", ["pipelineID", {"pipelineID"}, ("pipelineID",), 42, {}])
def test_get_voices_rejects_non_list_return_fields(mock_waapi, bad):
    """Anything that's not a list must be rejected (string, set, tuple, dict, int)."""
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="non-empty list"):
        wwise_python_lib.profiler_get_voices(return_fields=bad)
    _assert_not_called(mock_waapi)


def test_get_voices_rejects_unknown_field(mock_waapi):
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="contains unknown values"):
        wwise_python_lib.profiler_get_voices(return_fields=["pipelineID", "badField"])
    _assert_not_called(mock_waapi)


@pytest.mark.parametrize("bad_elem", [[], {}, 42, None, ("x",)])
def test_get_voices_rejects_unhashable_or_non_str_field(mock_waapi, bad_elem):
    """Non-str element (incl. unhashable like []/{} ) must raise WwiseValidationError,
    NOT leak a raw TypeError from the `in _VOICE_RETURN_FIELDS` set-membership.
    """
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="contains unknown values"):
        wwise_python_lib.profiler_get_voices(return_fields=[bad_elem, "pipelineID"])
    _assert_not_called(mock_waapi)


def test_get_voices_validation_failure_aborts_before_waapi_call(mock_waapi):
    """Bad input must abort before any dispatch — no partial WAAPI call."""
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError):
        wwise_python_lib.profiler_get_voices(
            time="capture",
            voice_pipeline_id=5,
            return_fields=["pipelineID", "bogus"],
        )
    _assert_not_called(mock_waapi)


# ---------------------------------------------------------------------------
# Error wrapping
# ---------------------------------------------------------------------------

def test_get_voices_wraps_waapi_failure_as_WwiseApiError(mocker):
    from wwise_errors import WwiseApiError
    import wwise_python_lib

    mocker.patch.object(
        wwise_python_lib,
        "waapi_call",
        side_effect=RuntimeError("kaboom"),
    )

    with pytest.raises(WwiseApiError) as exc_info:
        wwise_python_lib.profiler_get_voices(
            time=100,
            voice_pipeline_id=11,
            return_fields=["pipelineID"],
            timeout=10.0,
        )

    assert exc_info.value.operation == URI
    assert exc_info.value.details["error_type"] == "RuntimeError"
    assert exc_info.value.details["time"] == 100
    assert exc_info.value.details["voice_pipeline_id"] == 11
    assert exc_info.value.details["return_fields"] == ["pipelineID"]
    assert exc_info.value.details["timeout"] == 10.0


def test_get_voices_does_not_double_wrap_pylib_errors(mocker):
    from wwise_errors import WwiseApiError
    import wwise_python_lib

    original = WwiseApiError(
        "already wrapped",
        operation="something.else",
        details={"reason": "test"},
    )
    mocker.patch.object(wwise_python_lib, "waapi_call", side_effect=original)

    with pytest.raises(WwiseApiError) as exc_info:
        wwise_python_lib.profiler_get_voices()

    assert exc_info.value is original


# ---------------------------------------------------------------------------
# Response handling
# ---------------------------------------------------------------------------

def test_get_voices_returns_waapi_response(mock_waapi):
    import wwise_python_lib

    mock_waapi.return_value = {"return": [{"pipelineID": 1}, {"pipelineID": 2}]}

    result = wwise_python_lib.profiler_get_voices()

    assert result == {"return": [{"pipelineID": 1}, {"pipelineID": 2}]}


def test_get_voices_raises_on_none(mock_waapi):
    """None is an anomaly -> raises WwiseApiError."""
    import wwise_python_lib
    from wwise_errors import WwiseApiError

    mock_waapi.return_value = None

    with pytest.raises(WwiseApiError):
        wwise_python_lib.profiler_get_voices()


# ---------------------------------------------------------------------------
# MCP shim delegation
# ---------------------------------------------------------------------------

def test_mcp_shim_delegates_default_args(mock_waapi):
    import wwise_mcp

    mock_waapi.return_value = {"return": []}
    result = wwise_mcp.profiler_get_voices()

    assert result == {"return": []}
    call = _find_call(mock_waapi, URI)
    assert call.args[1] == {"time": "capture"}
    assert call.kwargs.get("options") is None
    assert call.kwargs["timeout"] == 5.0


def test_mcp_shim_forwards_all_kwargs(mock_waapi):
    """Regression: shim must forward time / voice_pipeline_id / return_fields / timeout."""
    import wwise_mcp

    wwise_mcp.profiler_get_voices(
        time=4242,
        voice_pipeline_id=99,
        return_fields=["pipelineID", "baseVolume"],
        timeout=8.0,
    )

    call = _find_call(mock_waapi, URI)
    assert call.args[1] == {"time": 4242, "voicePipelineID": 99}
    assert call.kwargs["options"] == {"return": ["pipelineID", "baseVolume"]}
    assert call.kwargs["timeout"] == 8.0


# ---------------------------------------------------------------------------
# COMMANDS registry
# ---------------------------------------------------------------------------

def test_get_voices_registered_in_COMMANDS():
    import wwise_mcp

    assert "profiler_get_voices" in wwise_mcp.COMMANDS
    entry = wwise_mcp.COMMANDS["profiler_get_voices"]
    assert entry.func is wwise_mcp.profiler_get_voices
    # Docstring must surface the key arg names and the chain-verification guidance.
    assert "time" in entry.doc
    assert "voice_pipeline_id" in entry.doc
    assert "return_fields" in entry.doc
    assert "pipelineID" in entry.doc
    assert "baseVolume" in entry.doc

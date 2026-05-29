"""Tests for profiler_get_voice_contributions.

Covers SDD Task 5 of TASK-81.10. The wrapper posts to
ak.wwise.core.profiler.getVoiceContributions with:
- args.voicePipelineID (required uint32) + args.time (int ms or 'user'/'capture')
- optional args.bussesPipelineID (list[uint32]; [] = dry path; omit = absent)
- NO options field per schema (unlike getVoices)
- timeout kwarg forwarded to waapi_call (default 5.0s)

voiceInspector must have been enabled via profiler_enable_data; not enforceable
by the wrapper, but COMMANDS doc surfaces it. Validation tests are exhaustive
to keep TypeError out of the wire.
"""
from __future__ import annotations

import pytest


URI = "ak.wwise.core.profiler.getVoiceContributions"


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

def test_uri_is_get_voice_contributions(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_get_voice_contributions(42)

    call = _find_call(mock_waapi, URI)
    assert call.args[0] == URI


def test_default_args_voicePipelineID_and_time_capture(mock_waapi):
    """Default call: voicePipelineID=<arg>, time='capture', no bussesPipelineID, no options."""
    import wwise_python_lib

    wwise_python_lib.profiler_get_voice_contributions(42)

    call = _find_call(mock_waapi, URI)
    assert call.args[1] == {"voicePipelineID": 42, "time": "capture"}


def test_time_user_string(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_get_voice_contributions(42, time="user")

    call = _find_call(mock_waapi, URI)
    assert call.args[1] == {"voicePipelineID": 42, "time": "user"}


def test_time_int_ms(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_get_voice_contributions(42, time=12345)

    call = _find_call(mock_waapi, URI)
    assert call.args[1] == {"voicePipelineID": 42, "time": 12345}


def test_no_options_field_passed_to_waapi(mock_waapi):
    """getVoiceContributions has no options per schema; must not send options."""
    import wwise_python_lib

    wwise_python_lib.profiler_get_voice_contributions(42)

    call = _find_call(mock_waapi, URI)
    assert "options" not in call.kwargs or call.kwargs.get("options") is None


def test_busses_pipeline_id_none_omits_field(mock_waapi):
    """busses_pipeline_id=None -> bussesPipelineID absent from args."""
    import wwise_python_lib

    wwise_python_lib.profiler_get_voice_contributions(42)

    call = _find_call(mock_waapi, URI)
    assert "bussesPipelineID" not in call.args[1]


def test_busses_pipeline_id_empty_list_is_present_as_empty_array(mock_waapi):
    """Explicit [] = dry path; field MUST be present (not omitted)."""
    import wwise_python_lib

    wwise_python_lib.profiler_get_voice_contributions(42, busses_pipeline_id=[])

    call = _find_call(mock_waapi, URI)
    assert call.args[1] == {"voicePipelineID": 42, "time": "capture", "bussesPipelineID": []}


def test_busses_pipeline_id_wet_path_passed_through(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_get_voice_contributions(
        42, busses_pipeline_id=[100, 200, 300]
    )

    call = _find_call(mock_waapi, URI)
    assert call.args[1]["bussesPipelineID"] == [100, 200, 300]


def test_timeout_default_5_seconds(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_get_voice_contributions(42)

    call = _find_call(mock_waapi, URI)
    assert call.kwargs["timeout"] == 5.0


def test_timeout_custom(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_get_voice_contributions(42, timeout=12.5)

    call = _find_call(mock_waapi, URI)
    assert call.kwargs["timeout"] == 12.5


def test_combines_all_args(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_get_voice_contributions(
        7,
        time=999,
        busses_pipeline_id=[111, 222],
        timeout=10.0,
    )

    call = _find_call(mock_waapi, URI)
    assert call.args[1] == {
        "voicePipelineID": 7,
        "time": 999,
        "bussesPipelineID": [111, 222],
    }
    assert call.kwargs["timeout"] == 10.0


# ---------------------------------------------------------------------------
# voice_pipeline_id validation (REQUIRED, uint32 boundary)
# ---------------------------------------------------------------------------

def test_voice_pipeline_id_required_positional():
    """voice_pipeline_id has no default; missing must TypeError from Python signature."""
    import wwise_python_lib

    with pytest.raises(TypeError):
        wwise_python_lib.profiler_get_voice_contributions()  # type: ignore[call-arg]


@pytest.mark.parametrize("good_id", [0, 1, 0xFFFFFFFF])
def test_accepts_valid_pipeline_id_inclusive_bounds(mock_waapi, good_id):
    import wwise_python_lib

    wwise_python_lib.profiler_get_voice_contributions(good_id)

    call = _find_call(mock_waapi, URI)
    assert call.args[1]["voicePipelineID"] == good_id


def test_rejects_pipeline_id_above_uint32(mock_waapi):
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="voice_pipeline_id"):
        wwise_python_lib.profiler_get_voice_contributions(0x100000000)
    _assert_not_called(mock_waapi)


def test_rejects_negative_pipeline_id(mock_waapi):
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="voice_pipeline_id"):
        wwise_python_lib.profiler_get_voice_contributions(-1)
    _assert_not_called(mock_waapi)


def test_rejects_bool_pipeline_id(mock_waapi):
    """bool isinstance(int) trap: True/False must NOT be accepted."""
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="voice_pipeline_id must be an int"):
        wwise_python_lib.profiler_get_voice_contributions(True)
    _assert_not_called(mock_waapi)


@pytest.mark.parametrize("bad", [1.5, "42", [], {}, (1,), None])
def test_rejects_wrong_type_pipeline_id(mock_waapi, bad):
    """Float / str / unhashable / tuple / None must surface as WwiseValidationError."""
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="voice_pipeline_id must be an int"):
        wwise_python_lib.profiler_get_voice_contributions(bad)
    _assert_not_called(mock_waapi)


# ---------------------------------------------------------------------------
# time validation (via _validate_profiler_time)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("good_time", [0, 1, 12345, "user", "capture"])
def test_accepts_valid_times(mock_waapi, good_time):
    import wwise_python_lib

    wwise_python_lib.profiler_get_voice_contributions(42, time=good_time)
    _find_call(mock_waapi, URI)


def test_rejects_bool_time(mock_waapi):
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="time must be"):
        wwise_python_lib.profiler_get_voice_contributions(42, time=True)
    _assert_not_called(mock_waapi)


def test_rejects_negative_int_time(mock_waapi):
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="time must be >= 0"):
        wwise_python_lib.profiler_get_voice_contributions(42, time=-1)
    _assert_not_called(mock_waapi)


def test_rejects_float_time(mock_waapi):
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="time must be"):
        wwise_python_lib.profiler_get_voice_contributions(42, time=1.5)
    _assert_not_called(mock_waapi)


def test_rejects_unknown_string_time(mock_waapi):
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="time string must be one of"):
        wwise_python_lib.profiler_get_voice_contributions(42, time="now")
    _assert_not_called(mock_waapi)


@pytest.mark.parametrize("bad_time", [[], {}, None, (1,)])
def test_rejects_unhashable_or_wrong_type_time(mock_waapi, bad_time):
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="time must be"):
        wwise_python_lib.profiler_get_voice_contributions(42, time=bad_time)
    _assert_not_called(mock_waapi)


# ---------------------------------------------------------------------------
# busses_pipeline_id validation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("bad", ["abc", 42, {}, (1, 2), 1.5])
def test_rejects_non_list_busses_pipeline_id(mock_waapi, bad):
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="busses_pipeline_id must be a list"):
        wwise_python_lib.profiler_get_voice_contributions(42, busses_pipeline_id=bad)
    _assert_not_called(mock_waapi)


def test_rejects_bool_element_in_busses_pipeline_id(mock_waapi):
    """bool isinstance(int) trap inside the list elements."""
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match=r"busses_pipeline_id\[0\] must be int"):
        wwise_python_lib.profiler_get_voice_contributions(42, busses_pipeline_id=[True, 5])
    _assert_not_called(mock_waapi)


@pytest.mark.parametrize("bad_elem", [1.5, "5", None, [1], {"a": 1}, (1,)])
def test_rejects_non_int_element_in_busses_pipeline_id(mock_waapi, bad_elem):
    """Float / str / None / unhashable container must raise WwiseValidationError, not TypeError."""
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match=r"busses_pipeline_id\[1\] must be int"):
        wwise_python_lib.profiler_get_voice_contributions(
            42, busses_pipeline_id=[100, bad_elem]
        )
    _assert_not_called(mock_waapi)


def test_rejects_negative_element_in_busses_pipeline_id(mock_waapi):
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match=r"busses_pipeline_id\[0\]"):
        wwise_python_lib.profiler_get_voice_contributions(42, busses_pipeline_id=[-1])
    _assert_not_called(mock_waapi)


def test_rejects_above_uint32_element_in_busses_pipeline_id(mock_waapi):
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match=r"busses_pipeline_id\[1\]"):
        wwise_python_lib.profiler_get_voice_contributions(
            42, busses_pipeline_id=[100, 0x100000000]
        )
    _assert_not_called(mock_waapi)


@pytest.mark.parametrize("good_elem", [0, 1, 0xFFFFFFFF])
def test_accepts_uint32_boundary_elements_in_busses_pipeline_id(mock_waapi, good_elem):
    import wwise_python_lib

    wwise_python_lib.profiler_get_voice_contributions(
        42, busses_pipeline_id=[good_elem]
    )

    call = _find_call(mock_waapi, URI)
    assert call.args[1]["bussesPipelineID"] == [good_elem]


@pytest.mark.parametrize("size", [65, 100, 1000])
def test_busses_pipeline_id_rejects_oversized_list(mock_waapi, size):
    """Defensive cap: bus chains longer than 64 must be rejected before WAAPI dispatch."""
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="exceeds defensive cap"):
        wwise_python_lib.profiler_get_voice_contributions(
            42, busses_pipeline_id=[1] * size
        )
    _assert_not_called(mock_waapi)


def test_busses_pipeline_id_accepts_max_length(mock_waapi):
    """Length 64 (the cap) must pass validation and reach WAAPI."""
    import wwise_python_lib

    wwise_python_lib.profiler_get_voice_contributions(
        42, busses_pipeline_id=[1] * 64
    )
    call = _find_call(mock_waapi, URI)
    assert call.args[1]["bussesPipelineID"] == [1] * 64


def test_validation_failure_aborts_before_waapi_call(mock_waapi):
    """Bad input must abort before any dispatch — no partial WAAPI call."""
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError):
        wwise_python_lib.profiler_get_voice_contributions(
            42, time="capture", busses_pipeline_id=[100, "nope"]
        )
    _assert_not_called(mock_waapi)


# ---------------------------------------------------------------------------
# Error wrapping
# ---------------------------------------------------------------------------

def test_wraps_waapi_failure_as_WwiseApiError(mocker):
    from wwise_errors import WwiseApiError
    import wwise_python_lib

    mocker.patch.object(
        wwise_python_lib,
        "waapi_call",
        side_effect=RuntimeError("kaboom"),
    )

    with pytest.raises(WwiseApiError) as exc_info:
        wwise_python_lib.profiler_get_voice_contributions(
            11,
            time=100,
            busses_pipeline_id=[55, 66],
            timeout=10.0,
        )

    assert exc_info.value.operation == URI
    assert exc_info.value.details["error_type"] == "RuntimeError"
    assert exc_info.value.details["voice_pipeline_id"] == 11
    assert exc_info.value.details["time"] == 100
    assert exc_info.value.details["busses_pipeline_id"] == [55, 66]
    assert exc_info.value.details["timeout"] == 10.0


def test_does_not_double_wrap_pylib_errors(mocker):
    from wwise_errors import WwiseApiError
    import wwise_python_lib

    original = WwiseApiError(
        "already wrapped",
        operation="something.else",
        details={"reason": "test"},
    )
    mocker.patch.object(wwise_python_lib, "waapi_call", side_effect=original)

    with pytest.raises(WwiseApiError) as exc_info:
        wwise_python_lib.profiler_get_voice_contributions(42)

    assert exc_info.value is original


# ---------------------------------------------------------------------------
# Response handling
# ---------------------------------------------------------------------------

def test_returns_waapi_response_object_passthrough(mock_waapi):
    import wwise_python_lib

    payload = {
        "return": {
            "volume": -3.5,
            "LPF": 0,
            "HPF": 0,
            "objects": [{"name": "Bus_X", "volume": 0.0, "LPF": 0, "HPF": 0}],
        }
    }
    mock_waapi.return_value = payload

    result = wwise_python_lib.profiler_get_voice_contributions(42)
    assert result == payload


def test_normalises_none_to_empty_dict(mock_waapi):
    """Defensive: WAAPI sometimes returns None; wrapper normalises to {} (NOT {'return': []})."""
    import wwise_python_lib

    mock_waapi.return_value = None

    assert wwise_python_lib.profiler_get_voice_contributions(42) == {}


# ---------------------------------------------------------------------------
# MCP shim delegation
# ---------------------------------------------------------------------------

def test_mcp_shim_delegates_default_args(mock_waapi):
    import wwise_mcp

    mock_waapi.return_value = {"return": {"volume": 0.0, "LPF": 0, "HPF": 0, "objects": []}}
    result = wwise_mcp.profiler_get_voice_contributions(42)

    assert result == {"return": {"volume": 0.0, "LPF": 0, "HPF": 0, "objects": []}}
    call = _find_call(mock_waapi, URI)
    assert call.args[1] == {"voicePipelineID": 42, "time": "capture"}
    assert "options" not in call.kwargs or call.kwargs.get("options") is None
    assert call.kwargs["timeout"] == 5.0


def test_mcp_shim_forwards_all_kwargs(mock_waapi):
    """Regression: shim must forward voice_pipeline_id + time + busses_pipeline_id + timeout."""
    import wwise_mcp

    wwise_mcp.profiler_get_voice_contributions(
        99,
        time=4242,
        busses_pipeline_id=[7, 8, 9],
        timeout=8.0,
    )

    call = _find_call(mock_waapi, URI)
    assert call.args[1] == {
        "voicePipelineID": 99,
        "time": 4242,
        "bussesPipelineID": [7, 8, 9],
    }
    assert call.kwargs["timeout"] == 8.0


def test_mcp_shim_forwards_empty_busses_pipeline_id_for_dry_path(mock_waapi):
    """Shim must preserve the None vs [] distinction (dry-path signal)."""
    import wwise_mcp

    wwise_mcp.profiler_get_voice_contributions(99, busses_pipeline_id=[])

    call = _find_call(mock_waapi, URI)
    assert call.args[1] == {
        "voicePipelineID": 99,
        "time": "capture",
        "bussesPipelineID": [],
    }


# ---------------------------------------------------------------------------
# COMMANDS registry
# ---------------------------------------------------------------------------

def test_registered_in_COMMANDS():
    import wwise_mcp

    assert "profiler_get_voice_contributions" in wwise_mcp.COMMANDS
    entry = wwise_mcp.COMMANDS["profiler_get_voice_contributions"]
    assert entry.func is wwise_mcp.profiler_get_voice_contributions
    # Docstring must surface voiceInspector prerequisite + dry-path semantics + key args.
    assert "voiceInspector" in entry.doc
    assert "dry path" in entry.doc
    assert "voice_pipeline_id" in entry.doc
    assert "busses_pipeline_id" in entry.doc
    assert "time" in entry.doc

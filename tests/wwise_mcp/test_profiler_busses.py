"""Tests for profiler_get_busses - Task 8 of TASK-81.10.

Validates the WAAPI getBusses wrapper: URI, args/options shape,
return_fields whitelist (12 schema-exact fields), bus_pipeline_id bounds,
error-details dict (incl timeout), None-response coercion to
{"return": []}, shim delegation, and COMMANDS registration.
"""
from __future__ import annotations

import pytest


_ALL_FIELDS = sorted({
    "pipelineID", "mixBusID", "objectGUID", "objectName",
    "gameObjectID", "gameObjectName", "deviceID",
    "volume", "downstreamGain",
    "voiceCount", "effectCount", "depth",
})


def _find_get_busses_call(mock_waapi):
    for call in mock_waapi.call_args_list:
        if call.args and call.args[0] == "ak.wwise.core.profiler.getBusses":
            return call
    raise AssertionError(
        "ak.wwise.core.profiler.getBusses not in call_args_list: "
        f"{[c.args for c in mock_waapi.call_args_list]}"
    )


# ---------------------------------------------------------------------------
# URI + default args
# ---------------------------------------------------------------------------

def test_uri_is_exactly_getBusses(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_get_busses()
    call = _find_get_busses_call(mock_waapi)
    assert call.args[0] == "ak.wwise.core.profiler.getBusses"


def test_default_args_only_carry_time_capture(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_get_busses()
    call = _find_get_busses_call(mock_waapi)
    assert call.args[1] == {"time": "capture"}
    assert call.kwargs.get("options") is None
    assert call.kwargs.get("timeout") == 5.0


def test_time_user_accepted(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_get_busses(time="user")
    call = _find_get_busses_call(mock_waapi)
    assert call.args[1] == {"time": "user"}


def test_time_int_accepted(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_get_busses(time=12345)
    call = _find_get_busses_call(mock_waapi)
    assert call.args[1] == {"time": 12345}


def test_time_invalid_string_rejected(mock_waapi):
    import wwise_python_lib
    from wwise_python_lib import WwiseValidationError

    with pytest.raises(WwiseValidationError):
        wwise_python_lib.profiler_get_busses(time="bogus")
    assert mock_waapi.call_count == 0


def test_custom_timeout_forwarded(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_get_busses(timeout=12.5)
    call = _find_get_busses_call(mock_waapi)
    assert call.kwargs.get("timeout") == 12.5


# ---------------------------------------------------------------------------
# bus_pipeline_id validation
# ---------------------------------------------------------------------------

def test_bus_pipeline_id_added_to_args(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_get_busses(bus_pipeline_id=42)
    call = _find_get_busses_call(mock_waapi)
    assert call.args[1] == {"time": "capture", "busPipelineID": 42}


def test_bus_pipeline_id_zero_accepted(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_get_busses(bus_pipeline_id=0)
    call = _find_get_busses_call(mock_waapi)
    assert call.args[1]["busPipelineID"] == 0


def test_bus_pipeline_id_uint32_max_accepted(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_get_busses(bus_pipeline_id=0xFFFFFFFF)
    call = _find_get_busses_call(mock_waapi)
    assert call.args[1]["busPipelineID"] == 0xFFFFFFFF


def test_bus_pipeline_id_negative_rejected(mock_waapi):
    import wwise_python_lib
    from wwise_python_lib import WwiseValidationError

    with pytest.raises(WwiseValidationError):
        wwise_python_lib.profiler_get_busses(bus_pipeline_id=-1)
    assert mock_waapi.call_count == 0


def test_bus_pipeline_id_over_uint32_rejected(mock_waapi):
    import wwise_python_lib
    from wwise_python_lib import WwiseValidationError

    with pytest.raises(WwiseValidationError):
        wwise_python_lib.profiler_get_busses(bus_pipeline_id=0x100000000)
    assert mock_waapi.call_count == 0


def test_bus_pipeline_id_bool_rejected(mock_waapi):
    """bool is a subclass of int - must be rejected explicitly."""
    import wwise_python_lib
    from wwise_python_lib import WwiseValidationError

    with pytest.raises(WwiseValidationError):
        wwise_python_lib.profiler_get_busses(bus_pipeline_id=True)
    assert mock_waapi.call_count == 0


def test_bus_pipeline_id_str_rejected(mock_waapi):
    import wwise_python_lib
    from wwise_python_lib import WwiseValidationError

    with pytest.raises(WwiseValidationError):
        wwise_python_lib.profiler_get_busses(bus_pipeline_id="42")
    assert mock_waapi.call_count == 0


# ---------------------------------------------------------------------------
# return_fields whitelist (12 schema-exact fields)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("field", _ALL_FIELDS)
def test_all_12_schema_fields_accepted(mock_waapi, field):
    import wwise_python_lib

    wwise_python_lib.profiler_get_busses(return_fields=[field])
    call = _find_get_busses_call(mock_waapi)
    assert call.kwargs["options"] == {"return": [field]}


def test_return_fields_all_12_at_once(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_get_busses(return_fields=list(_ALL_FIELDS))
    call = _find_get_busses_call(mock_waapi)
    assert call.kwargs["options"] == {"return": list(_ALL_FIELDS)}


def test_return_fields_unknown_value_rejected(mock_waapi):
    import wwise_python_lib
    from wwise_python_lib import WwiseValidationError

    with pytest.raises(WwiseValidationError, match="unknown"):
        wwise_python_lib.profiler_get_busses(return_fields=["bogusField"])
    assert mock_waapi.call_count == 0


def test_return_fields_empty_list_rejected(mock_waapi):
    import wwise_python_lib
    from wwise_python_lib import WwiseValidationError

    with pytest.raises(WwiseValidationError):
        wwise_python_lib.profiler_get_busses(return_fields=[])
    assert mock_waapi.call_count == 0


def test_return_fields_non_list_rejected(mock_waapi):
    import wwise_python_lib
    from wwise_python_lib import WwiseValidationError

    with pytest.raises(WwiseValidationError):
        wwise_python_lib.profiler_get_busses(return_fields="objectName")
    assert mock_waapi.call_count == 0


def test_return_fields_non_string_element_rejected(mock_waapi):
    """Non-string element must not crash the membership check."""
    import wwise_python_lib
    from wwise_python_lib import WwiseValidationError

    with pytest.raises(WwiseValidationError):
        wwise_python_lib.profiler_get_busses(return_fields=[123])
    assert mock_waapi.call_count == 0


def test_return_fields_unhashable_element_rejected(mock_waapi):
    """Lists/dicts are unhashable - frozenset membership would TypeError.
    Pre-isinstance guard must short-circuit before the `in` check."""
    import wwise_python_lib
    from wwise_python_lib import WwiseValidationError

    with pytest.raises(WwiseValidationError):
        wwise_python_lib.profiler_get_busses(return_fields=[["nested"]])
    assert mock_waapi.call_count == 0


# ---------------------------------------------------------------------------
# Error details / response shaping
# ---------------------------------------------------------------------------

def test_waapi_exception_wrapped_with_full_details(mock_waapi):
    import wwise_python_lib
    from wwise_python_lib import WwiseApiError

    mock_waapi.side_effect = RuntimeError("connection lost")

    with pytest.raises(WwiseApiError) as exc:
        wwise_python_lib.profiler_get_busses(
            time=500,
            bus_pipeline_id=7,
            return_fields=["voiceCount"],
            timeout=3.0,
        )
    details = exc.value.details
    assert details["error_type"] == "RuntimeError"
    assert details["time"] == 500
    assert details["bus_pipeline_id"] == 7
    assert details["return_fields"] == ["voiceCount"]
    assert details["timeout"] == 3.0
    assert exc.value.operation == "ak.wwise.core.profiler.getBusses"


def test_none_response_coerced_to_return_empty_list(mock_waapi):
    """Schema returns a list - empty default must be {"return": []} not {}."""
    import wwise_python_lib

    mock_waapi.return_value = None
    result = wwise_python_lib.profiler_get_busses()
    assert result == {"return": []}


def test_existing_validation_error_passes_through(mock_waapi):
    """WwisePyLibError raised inside the try block must not be re-wrapped."""
    import wwise_python_lib
    from wwise_python_lib import WwiseValidationError, WwisePyLibError

    mock_waapi.side_effect = WwiseValidationError("inner")

    with pytest.raises(WwisePyLibError) as exc:
        wwise_python_lib.profiler_get_busses()
    assert isinstance(exc.value, WwiseValidationError)
    assert str(exc.value) == "inner"


# ---------------------------------------------------------------------------
# Shim + COMMANDS registration
# ---------------------------------------------------------------------------

def test_shim_forwards_all_kwargs(mock_waapi):
    """wwise_mcp.profiler_get_busses must forward time, bus_pipeline_id,
    return_fields, and timeout to the lib unchanged."""
    import wwise_mcp

    wwise_mcp.profiler_get_busses(
        time=200,
        bus_pipeline_id=11,
        return_fields=["voiceCount", "effectCount"],
        timeout=4.5,
    )
    call = _find_get_busses_call(mock_waapi)
    assert call.args[0] == "ak.wwise.core.profiler.getBusses"
    assert call.args[1] == {"time": 200, "busPipelineID": 11}
    assert call.kwargs["options"] == {"return": ["voiceCount", "effectCount"]}
    assert call.kwargs["timeout"] == 4.5


def test_command_registered_in_COMMANDS():
    import wwise_mcp

    assert "profiler_get_busses" in wwise_mcp.COMMANDS
    cmd = wwise_mcp.COMMANDS["profiler_get_busses"]
    assert cmd.func is wwise_mcp.profiler_get_busses


def test_commands_doc_mentions_voice_and_effect_counts():
    """COMMANDS doc should advertise voiceCount + effectCount as the
    bus-routing diagnostic angle (plan rationale)."""
    import wwise_mcp

    doc = wwise_mcp.COMMANDS["profiler_get_busses"].doc
    assert "voiceCount" in doc
    assert "effectCount" in doc

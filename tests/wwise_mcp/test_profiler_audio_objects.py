"""Tests for profiler_get_audio_objects - Task 6 of TASK-81.10.

Validates the WAAPI getAudioObjects wrapper: URI, args/options shape,
return_fields whitelist (22 schema-exact fields), bus_pipeline_id bounds,
error-details dict, None-response raising WwiseApiError, shim
delegation, and COMMANDS registration.
"""
from __future__ import annotations

import pytest


_ALL_FIELDS = sorted({
    "busName", "effectPluginName", "audioObjectID", "busPipelineID",
    "gameObjectID", "gameObjectName", "audioObjectName",
    "instigatorPipelineID", "busID", "busGUID",
    "spatializationMode", "x", "y", "z",
    "spread", "focus", "channelConfig",
    "effectClassID", "effectIndex", "metadata",
    "rmsMeter", "peakMeter",
})


def _find_get_audio_objects_call(mock_waapi):
    for call in mock_waapi.call_args_list:
        if call.args and call.args[0] == "ak.wwise.core.profiler.getAudioObjects":
            return call
    raise AssertionError(
        "ak.wwise.core.profiler.getAudioObjects not in call_args_list: "
        f"{[c.args for c in mock_waapi.call_args_list]}"
    )


# ---------------------------------------------------------------------------
# URI + default args
# ---------------------------------------------------------------------------

def test_uri_is_exactly_getAudioObjects(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_get_audio_objects()
    call = _find_get_audio_objects_call(mock_waapi)
    assert call.args[0] == "ak.wwise.core.profiler.getAudioObjects"


def test_default_args_only_carry_time_capture(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_get_audio_objects()
    call = _find_get_audio_objects_call(mock_waapi)
    assert call.args[1] == {"time": "capture"}
    # options absent (None) when no return_fields
    assert call.kwargs.get("options") is None
    assert call.kwargs.get("timeout") == 5.0


def test_time_user_accepted(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_get_audio_objects(time="user")
    call = _find_get_audio_objects_call(mock_waapi)
    assert call.args[1] == {"time": "user"}


def test_time_int_accepted(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_get_audio_objects(time=12345)
    call = _find_get_audio_objects_call(mock_waapi)
    assert call.args[1] == {"time": 12345}


def test_time_invalid_string_rejected(mock_waapi):
    import wwise_python_lib
    from wwise_python_lib import WwiseValidationError

    with pytest.raises(WwiseValidationError):
        wwise_python_lib.profiler_get_audio_objects(time="bogus")
    assert mock_waapi.call_count == 0


def test_custom_timeout_forwarded(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_get_audio_objects(timeout=12.5)
    call = _find_get_audio_objects_call(mock_waapi)
    assert call.kwargs.get("timeout") == 12.5


# ---------------------------------------------------------------------------
# bus_pipeline_id validation
# ---------------------------------------------------------------------------

def test_bus_pipeline_id_added_to_args(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_get_audio_objects(bus_pipeline_id=42)
    call = _find_get_audio_objects_call(mock_waapi)
    assert call.args[1] == {"time": "capture", "busPipelineID": 42}


def test_bus_pipeline_id_zero_accepted(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_get_audio_objects(bus_pipeline_id=0)
    call = _find_get_audio_objects_call(mock_waapi)
    assert call.args[1]["busPipelineID"] == 0


def test_bus_pipeline_id_uint32_max_accepted(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_get_audio_objects(bus_pipeline_id=0xFFFFFFFF)
    call = _find_get_audio_objects_call(mock_waapi)
    assert call.args[1]["busPipelineID"] == 0xFFFFFFFF


def test_bus_pipeline_id_negative_rejected(mock_waapi):
    import wwise_python_lib
    from wwise_python_lib import WwiseValidationError

    with pytest.raises(WwiseValidationError):
        wwise_python_lib.profiler_get_audio_objects(bus_pipeline_id=-1)
    assert mock_waapi.call_count == 0


def test_bus_pipeline_id_over_uint32_rejected(mock_waapi):
    import wwise_python_lib
    from wwise_python_lib import WwiseValidationError

    with pytest.raises(WwiseValidationError):
        wwise_python_lib.profiler_get_audio_objects(bus_pipeline_id=0x100000000)
    assert mock_waapi.call_count == 0


def test_bus_pipeline_id_bool_rejected(mock_waapi):
    """bool is a subclass of int - must be rejected explicitly."""
    import wwise_python_lib
    from wwise_python_lib import WwiseValidationError

    with pytest.raises(WwiseValidationError):
        wwise_python_lib.profiler_get_audio_objects(bus_pipeline_id=True)
    assert mock_waapi.call_count == 0


def test_bus_pipeline_id_str_rejected(mock_waapi):
    import wwise_python_lib
    from wwise_python_lib import WwiseValidationError

    with pytest.raises(WwiseValidationError):
        wwise_python_lib.profiler_get_audio_objects(bus_pipeline_id="42")
    assert mock_waapi.call_count == 0


# ---------------------------------------------------------------------------
# return_fields whitelist (22 schema-exact fields)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("field", _ALL_FIELDS)
def test_all_22_schema_fields_accepted(mock_waapi, field):
    import wwise_python_lib

    wwise_python_lib.profiler_get_audio_objects(return_fields=[field])
    call = _find_get_audio_objects_call(mock_waapi)
    assert call.kwargs["options"] == {"return": [field]}


def test_return_fields_all_22_at_once(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_get_audio_objects(return_fields=list(_ALL_FIELDS))
    call = _find_get_audio_objects_call(mock_waapi)
    assert call.kwargs["options"] == {"return": list(_ALL_FIELDS)}


def test_return_fields_unknown_value_rejected(mock_waapi):
    import wwise_python_lib
    from wwise_python_lib import WwiseValidationError

    with pytest.raises(WwiseValidationError, match="unknown"):
        wwise_python_lib.profiler_get_audio_objects(return_fields=["bogusField"])
    assert mock_waapi.call_count == 0


def test_return_fields_empty_list_rejected(mock_waapi):
    import wwise_python_lib
    from wwise_python_lib import WwiseValidationError

    with pytest.raises(WwiseValidationError):
        wwise_python_lib.profiler_get_audio_objects(return_fields=[])
    assert mock_waapi.call_count == 0


def test_return_fields_non_list_rejected(mock_waapi):
    import wwise_python_lib
    from wwise_python_lib import WwiseValidationError

    with pytest.raises(WwiseValidationError):
        wwise_python_lib.profiler_get_audio_objects(return_fields="effectPluginName")
    assert mock_waapi.call_count == 0


def test_return_fields_non_string_element_rejected(mock_waapi):
    """Non-string element must not crash the membership check."""
    import wwise_python_lib
    from wwise_python_lib import WwiseValidationError

    with pytest.raises(WwiseValidationError):
        wwise_python_lib.profiler_get_audio_objects(return_fields=[123])
    assert mock_waapi.call_count == 0


def test_return_fields_unhashable_element_rejected(mock_waapi):
    """Lists/dicts are unhashable - frozenset membership would TypeError.
    Pre-isinstance guard must short-circuit before the `in` check."""
    import wwise_python_lib
    from wwise_python_lib import WwiseValidationError

    with pytest.raises(WwiseValidationError):
        wwise_python_lib.profiler_get_audio_objects(return_fields=[["nested"]])
    assert mock_waapi.call_count == 0


# ---------------------------------------------------------------------------
# Error details / response shaping
# ---------------------------------------------------------------------------

def test_waapi_exception_wrapped_with_full_details(mock_waapi):
    import wwise_python_lib
    from wwise_python_lib import WwiseApiError

    mock_waapi.side_effect = RuntimeError("connection lost")

    with pytest.raises(WwiseApiError) as exc:
        wwise_python_lib.profiler_get_audio_objects(
            time=500,
            bus_pipeline_id=7,
            return_fields=["effectPluginName"],
            timeout=3.0,
        )
    details = exc.value.details
    assert details["error_type"] == "RuntimeError"
    assert details["time"] == 500
    assert details["bus_pipeline_id"] == 7
    assert details["return_fields"] == ["effectPluginName"]
    assert details["timeout"] == 3.0
    assert exc.value.operation == "ak.wwise.core.profiler.getAudioObjects"


def test_none_response_raises(mock_waapi):
    """None is an anomaly -> raises WwiseApiError."""
    import wwise_python_lib
    from wwise_errors import WwiseApiError

    mock_waapi.return_value = None
    with pytest.raises(WwiseApiError):
        wwise_python_lib.profiler_get_audio_objects()


def test_existing_validation_error_passes_through(mock_waapi):
    """WwisePyLibError raised inside the try block must not be re-wrapped."""
    import wwise_python_lib
    from wwise_python_lib import WwiseValidationError, WwisePyLibError

    mock_waapi.side_effect = WwiseValidationError("inner")

    with pytest.raises(WwisePyLibError) as exc:
        wwise_python_lib.profiler_get_audio_objects()
    # Should be the original WwiseValidationError, not a wrapped WwiseApiError
    assert isinstance(exc.value, WwiseValidationError)
    assert str(exc.value) == "inner"


# ---------------------------------------------------------------------------
# Shim + COMMANDS registration
# ---------------------------------------------------------------------------

def test_shim_forwards_all_kwargs(mock_waapi):
    """wwise_mcp.profiler_get_audio_objects must forward time, bus_pipeline_id,
    return_fields, and timeout to the lib unchanged."""
    import wwise_mcp

    wwise_mcp.profiler_get_audio_objects(
        time=200,
        bus_pipeline_id=11,
        return_fields=["rmsMeter", "peakMeter"],
        timeout=4.5,
    )
    call = _find_get_audio_objects_call(mock_waapi)
    assert call.args[0] == "ak.wwise.core.profiler.getAudioObjects"
    assert call.args[1] == {"time": 200, "busPipelineID": 11}
    assert call.kwargs["options"] == {"return": ["rmsMeter", "peakMeter"]}
    assert call.kwargs["timeout"] == 4.5


def test_command_registered_in_COMMANDS():
    import wwise_mcp

    assert "profiler_get_audio_objects" in wwise_mcp.COMMANDS
    cmd = wwise_mcp.COMMANDS["profiler_get_audio_objects"]
    assert cmd.func is wwise_mcp.profiler_get_audio_objects


def test_commands_doc_mentions_effectPluginName_for_reflect_pathing():
    """The COMMANDS doc should advertise effectPluginName as the
    Reflect/Pathing detection field - that's the whole point of this
    wrapper."""
    import wwise_mcp

    doc = wwise_mcp.COMMANDS["profiler_get_audio_objects"].doc
    assert "effectPluginName" in doc
    # Either Reflect or Pathing wording is fine; plan uses "Reflect/Pathing".
    assert "Reflect" in doc or "Pathing" in doc

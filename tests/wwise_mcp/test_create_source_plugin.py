"""Tests for create_source_plugin — creates a Source plug-in (Sine,
Tone Generator, Silence, SoundSeed Air, etc.) as a child of a Sound or
Voice object.

Covers backlog TASK-81.8. Sound parents get no 'language' field;
Voice parents get a 'language' field (English(US) / French / etc.).
"""
from __future__ import annotations

import pytest

from wwise_errors import WwiseValidationError


# Minimal WAAPI object.set response shape the create_source_plugin wrapper
# unwraps: response["objects"][0]["children"][0]. Tests that don't assert on
# return value still need this so the wrapper's post-call unwrap doesn't raise.
_CREATED_SOURCE_RESPONSE = {
    "objects": [
        {
            "id": "{00000000-0000-0000-0000-000000000001}",
            "children": [
                {
                    "id": "{22222222-2222-2222-2222-222222222222}",
                    "name": "Created",
                    "path": "\\Actor-Mixer Hierarchy\\Default Work Unit\\Created",
                    "type": "SourcePlugin",
                }
            ],
        }
    ]
}


def _find_set_call(mock_waapi):
    for call in mock_waapi.call_args_list:
        if call.args and call.args[0] == "ak.wwise.core.object.set":
            return call.args[1]
    raise AssertionError(
        "ak.wwise.core.object.set not called. Calls: "
        f"{[c.args for c in mock_waapi.call_args_list]}"
    )


def test_create_sine_source_under_sound(mock_waapi):
    """Sound parent: no language field; type=SourcePlugin per WAAPI schema."""
    import wwise_python_lib

    mock_waapi.return_value = _CREATED_SOURCE_RESPONSE
    wwise_python_lib.create_source_plugin(
        parent_path="\\Actor-Mixer Hierarchy\\Default Work Unit\\Test_Sine",
        name="Sine_440Hz_1s",
        class_id=46090754,  # placeholder Sine classId; verified via Wwise UI
    )

    args = _find_set_call(mock_waapi)
    assert args["objects"] == [
        {
            "object": "\\Actor-Mixer Hierarchy\\Default Work Unit\\Test_Sine",
            "children": [
                {
                    "type": "SourcePlugin",
                    "name": "Sine_440Hz_1s",
                    "classId": 46090754,
                }
            ],
        }
    ]
    assert args["onNameConflict"] == "rename"


def test_create_tone_generator_with_initial_properties(mock_waapi):
    import wwise_python_lib

    mock_waapi.return_value = _CREATED_SOURCE_RESPONSE
    wwise_python_lib.create_source_plugin(
        parent_path="\\Actor-Mixer Hierarchy\\Default Work Unit\\Test_Tone",
        name="ToneGen",
        class_id=10485762,
        properties={"Frequency": 1000.0, "Duration": 0.5},
    )

    args = _find_set_call(mock_waapi)
    child = args["objects"][0]["children"][0]
    assert child["type"] == "SourcePlugin"
    assert child["classId"] == 10485762
    assert child["@Frequency"] == 1000.0
    assert child["@Duration"] == 0.5


def test_voice_parent_uses_source_type_with_language(mock_waapi):
    """Voice parent: type=Source (not SourcePlugin) AND language field required."""
    import wwise_python_lib

    mock_waapi.return_value = _CREATED_SOURCE_RESPONSE
    wwise_python_lib.create_source_plugin(
        parent_path="\\Actor-Mixer Hierarchy\\Default Work Unit\\MyVoice",
        name="silence_jp",
        class_id=6619138,
        language="Japanese",
    )

    args = _find_set_call(mock_waapi)
    child = args["objects"][0]["children"][0]
    assert child["type"] == "Source"
    assert child["language"] == "Japanese"


def test_language_omitted_by_default(mock_waapi):
    import wwise_python_lib

    mock_waapi.return_value = _CREATED_SOURCE_RESPONSE
    wwise_python_lib.create_source_plugin(
        parent_path="\\Actor-Mixer Hierarchy\\Default Work Unit\\Test_Sine",
        name="Sine",
        class_id=46090754,
    )

    args = _find_set_call(mock_waapi)
    assert "language" not in args["objects"][0]["children"][0]


@pytest.mark.parametrize("bad_class_id", ["not-int", 1.5, True, False, None])
def test_invalid_class_id_type_raises(mock_waapi, bad_class_id):
    """Reject non-int. bool is int subclass so reject explicitly."""
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="class_id"):
        wwise_python_lib.create_source_plugin(
            parent_path="\\Actor-Mixer Hierarchy\\Default Work Unit\\Sound",
            name="x",
            class_id=bad_class_id,  # type: ignore[arg-type]
        )
    assert mock_waapi.call_count == 0


def test_empty_parent_path_raises(mock_waapi):
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="parent_path"):
        wwise_python_lib.create_source_plugin(
            parent_path="",
            name="x",
            class_id=1,
        )
    assert mock_waapi.call_count == 0


def test_empty_name_raises(mock_waapi):
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="name"):
        wwise_python_lib.create_source_plugin(
            parent_path="\\Actor-Mixer Hierarchy\\Default Work Unit\\Sound",
            name="",
            class_id=1,
        )
    assert mock_waapi.call_count == 0


def test_invalid_on_name_conflict_raises(mock_waapi):
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="on_name_conflict"):
        wwise_python_lib.create_source_plugin(
            parent_path="\\Actor-Mixer Hierarchy\\Default Work Unit\\Sound",
            name="x",
            class_id=1,
            on_name_conflict="garbage",
        )
    assert mock_waapi.call_count == 0


def test_mcp_wrapper_delegates(mock_waapi):
    import wwise_mcp

    mock_waapi.return_value = _CREATED_SOURCE_RESPONSE
    wwise_mcp.create_source_plugin(
        parent_path="\\Actor-Mixer Hierarchy\\Default Work Unit\\Test_Sine",
        name="Sine",
        class_id=46090754,
    )

    args = _find_set_call(mock_waapi)
    assert args["objects"][0]["children"][0]["classId"] == 46090754


def test_create_source_plugin_rejects_leading_at(mock_waapi):
    import wwise_python_lib

    with pytest.raises(WwiseValidationError):
        wwise_python_lib.create_source_plugin(
            parent_path="\\Actor-Mixer Hierarchy\\Default Work Unit\\Sound",
            name="x",
            class_id=1,
            properties={"@Foo": 1},
        )
    assert mock_waapi.call_count == 0


def test_command_registered_in_COMMANDS():
    """Wrapper must be registered in COMMANDS or MCP clients cannot call it."""
    import wwise_mcp

    assert "create_source_plugin" in wwise_mcp.COMMANDS
    assert wwise_mcp.COMMANDS["create_source_plugin"].func is wwise_mcp.create_source_plugin

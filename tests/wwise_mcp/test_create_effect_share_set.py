"""Tests for create_effect_share_set — creates a Custom Effect ShareSet
under \\Effects\\Default Work Unit with a given plug-in classId.

Covers backlog TASK-81.2 creation half. Insertion at a Bus/ActorMixer
Effects slot is the separate add_effect_to_object wrapper (Task 3).
"""
from __future__ import annotations

import pytest

from wwise_errors import WwiseValidationError


# Minimal WAAPI object.set response shape the create_effect_share_set wrapper
# unwraps: response["objects"][0]["children"][0]. Tests that don't assert on
# return value still need this so the wrapper's post-call unwrap doesn't raise.
_CREATED_SHARESET_RESPONSE = {
    "objects": [
        {
            "id": "{00000000-0000-0000-0000-000000000001}",
            "children": [
                {
                    "id": "{11111111-1111-1111-1111-111111111111}",
                    "name": "Created",
                    "path": "\\Effects\\Default Work Unit\\Created",
                    "type": "Effect",
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


def test_minimal_create(mock_waapi):
    """No initial properties: bare type/name/classId child entry."""
    import wwise_python_lib

    mock_waapi.return_value = _CREATED_SHARESET_RESPONSE
    wwise_python_lib.create_effect_share_set(
        parent_path="\\Effects\\Default Work Unit",
        name="SA_Spatializer_AB",
        class_id=12345678,
    )

    args = _find_set_call(mock_waapi)
    assert args["objects"] == [
        {
            "object": "\\Effects\\Default Work Unit",
            "children": [
                {
                    "type": "Effect",
                    "name": "SA_Spatializer_AB",
                    "classId": 12345678,
                }
            ],
        }
    ]
    assert args["onNameConflict"] == "rename"


def test_initial_properties_written_via_at_accessors(mock_waapi):
    import wwise_python_lib

    mock_waapi.return_value = _CREATED_SHARESET_RESPONSE
    wwise_python_lib.create_effect_share_set(
        parent_path="\\Effects\\Default Work Unit",
        name="SA_Spatializer_AB",
        class_id=12345678,
        properties={"Reflections": False, "Pathing": True},
    )

    args = _find_set_call(mock_waapi)
    child = args["objects"][0]["children"][0]
    assert child["type"] == "Effect"
    assert child["name"] == "SA_Spatializer_AB"
    assert child["classId"] == 12345678
    assert child["@Reflections"] is False
    assert child["@Pathing"] is True


def test_on_name_conflict_override(mock_waapi):
    import wwise_python_lib

    mock_waapi.return_value = _CREATED_SHARESET_RESPONSE
    wwise_python_lib.create_effect_share_set(
        parent_path="\\Effects\\Default Work Unit",
        name="ReverbA",
        class_id=7733251,
        on_name_conflict="merge",
    )

    args = _find_set_call(mock_waapi)
    assert args["onNameConflict"] == "merge"


def test_empty_parent_path_raises(mock_waapi):
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="parent_path"):
        wwise_python_lib.create_effect_share_set(
            parent_path="",
            name="X",
            class_id=1,
        )
    assert mock_waapi.call_count == 0


def test_empty_name_raises(mock_waapi):
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="name"):
        wwise_python_lib.create_effect_share_set(
            parent_path="\\Effects\\Default Work Unit",
            name="",
            class_id=1,
        )
    assert mock_waapi.call_count == 0


@pytest.mark.parametrize("bad_class_id", ["not-an-int", 1.5, True, False, None])
def test_invalid_class_id_type_raises(mock_waapi, bad_class_id):
    """Reject non-int. bool is an int subclass so reject explicitly."""
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="class_id"):
        wwise_python_lib.create_effect_share_set(
            parent_path="\\Effects\\Default Work Unit",
            name="X",
            class_id=bad_class_id,  # type: ignore[arg-type]
        )
    assert mock_waapi.call_count == 0


def test_invalid_on_name_conflict_raises(mock_waapi):
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="on_name_conflict"):
        wwise_python_lib.create_effect_share_set(
            parent_path="\\Effects\\Default Work Unit",
            name="X",
            class_id=1,
            on_name_conflict="invalid_mode",
        )
    assert mock_waapi.call_count == 0


def test_mcp_wrapper_delegates(mock_waapi):
    import wwise_mcp

    mock_waapi.return_value = _CREATED_SHARESET_RESPONSE
    wwise_mcp.create_effect_share_set(
        parent_path="\\Effects\\Default Work Unit",
        name="SA_Spatializer_AB",
        class_id=12345678,
    )

    args = _find_set_call(mock_waapi)
    assert args["objects"][0]["children"][0]["classId"] == 12345678


def test_command_registered_in_COMMANDS():
    """Wrapper must be registered in COMMANDS or MCP clients cannot call it."""
    import wwise_mcp

    assert "create_effect_share_set" in wwise_mcp.COMMANDS
    assert wwise_mcp.COMMANDS["create_effect_share_set"].func is wwise_mcp.create_effect_share_set

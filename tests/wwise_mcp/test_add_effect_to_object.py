"""Tests for add_effect_to_object — inserts an Effect/ShareSet reference
into the @Effects list of a Bus or ActorMixer.

Covers backlog TASK-81.2 insertion half. Listed-mode behavior:
- 'append' (default) adds a new EffectSlot at the end of @Effects.
- 'replaceAll' replaces the entire @Effects list with the new entry.

WAAPI does not support insert-at-index. To target a specific slot index,
call with listMode='replaceAll' and pass the full desired list.
"""
from __future__ import annotations

import pytest

from wwise_errors import WwiseValidationError


def _find_set_call(mock_waapi):
    for call in mock_waapi.call_args_list:
        if call.args and call.args[0] == "ak.wwise.core.object.set":
            return call.args[1]
    raise AssertionError(
        "ak.wwise.core.object.set not called. Calls: "
        f"{[c.args for c in mock_waapi.call_args_list]}"
    )


def test_append_existing_share_set_by_path(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.add_effect_to_object(
        object_path="\\Master-Mixer Hierarchy\\Default Work Unit\\Reverb_Aux_Bus",
        effect_ref="\\Effects\\Default Work Unit\\SA_Spatializer_AB",
    )

    args = _find_set_call(mock_waapi)
    assert args["objects"] == [
        {
            "object": "\\Master-Mixer Hierarchy\\Default Work Unit\\Reverb_Aux_Bus",
            "@Effects": [
                {
                    "type": "EffectSlot",
                    "name": "",
                    "@Effect": "\\Effects\\Default Work Unit\\SA_Spatializer_AB",
                }
            ],
        }
    ]
    assert args["onNameConflict"] == "merge"
    assert args["listMode"] == "append"


def test_replace_all_mode(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.add_effect_to_object(
        object_path="\\Master-Mixer Hierarchy\\Default Work Unit\\Reverb_Aux_Bus",
        effect_ref="{12345678-1234-1234-1234-123456789012}",
        list_mode="replaceAll",
    )

    args = _find_set_call(mock_waapi)
    assert args["listMode"] == "replaceAll"
    slot = args["objects"][0]["@Effects"][0]
    assert slot["@Effect"] == "{12345678-1234-1234-1234-123456789012}"


def test_empty_object_path_raises(mock_waapi):
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="object_path"):
        wwise_python_lib.add_effect_to_object(object_path="", effect_ref="x")
    assert mock_waapi.call_count == 0


def test_empty_effect_ref_raises(mock_waapi):
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="effect_ref"):
        wwise_python_lib.add_effect_to_object(
            object_path="\\Master-Mixer Hierarchy\\Default Work Unit\\Bus",
            effect_ref="",
        )
    assert mock_waapi.call_count == 0


def test_invalid_list_mode_raises(mock_waapi):
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="list_mode"):
        wwise_python_lib.add_effect_to_object(
            object_path="\\Master-Mixer Hierarchy\\Default Work Unit\\Bus",
            effect_ref="\\Effects\\Default Work Unit\\X",
            list_mode="prepend",
        )
    assert mock_waapi.call_count == 0


def test_mcp_wrapper_delegates(mock_waapi):
    import wwise_mcp

    wwise_mcp.add_effect_to_object(
        object_path="\\Master-Mixer Hierarchy\\Default Work Unit\\Reverb_Aux_Bus",
        effect_ref="\\Effects\\Default Work Unit\\SA_Spatializer_AB",
    )

    args = _find_set_call(mock_waapi)
    assert args["objects"][0]["@Effects"][0]["@Effect"] == (
        "\\Effects\\Default Work Unit\\SA_Spatializer_AB"
    )


def test_command_registered_in_COMMANDS():
    """Wrapper must be registered in COMMANDS or MCP clients cannot call it."""
    import wwise_mcp

    assert "add_effect_to_object" in wwise_mcp.COMMANDS
    assert wwise_mcp.COMMANDS["add_effect_to_object"].func is wwise_mcp.add_effect_to_object

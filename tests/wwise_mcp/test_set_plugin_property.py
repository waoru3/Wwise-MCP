"""Tests for set_plugin_property — writes plug-in / Bus properties via
ak.wwise.core.object.set with the @<PropertyName> accessor.

Covers backlog tasks TASK-81.1 (Effect plug-in property) and TASK-81.7
(Bus property persist). Both share the same root cause and the same fix.
"""
from __future__ import annotations

import pytest

from wwise_errors import WwiseValidationError


def _find_set_call(mock_waapi):
    """Return the args dict of the ak.wwise.core.object.set call.

    Filters out unrelated calls (e.g. introspection helpers) by URI.
    """
    for call in mock_waapi.call_args_list:
        if call.args and call.args[0] == "ak.wwise.core.object.set":
            return call.args[1]
    raise AssertionError(
        "ak.wwise.core.object.set not in call_args_list: "
        f"{[c.args for c in mock_waapi.call_args_list]}"
    )


def test_writes_plugin_property_via_object_set(mock_waapi):
    """Effect plug-in property (e.g. Steam Audio Spatializer Reflections)
    is routed through ak.wwise.core.object.set, not setProperty."""
    import wwise_python_lib

    wwise_python_lib.set_plugin_property(
        object_path="\\Effects\\Default Work Unit\\SA_Spatializer",
        property_name="Reflections",
        value=False,
    )

    args = _find_set_call(mock_waapi)
    assert args["objects"] == [
        {
            "object": "\\Effects\\Default Work Unit\\SA_Spatializer",
            "@Reflections": False,
        }
    ]
    assert args["onNameConflict"] == "merge"


def test_writes_bus_property_via_object_set(mock_waapi):
    """Bus property write also routes through object.set, fixing the
    silent-reject bug in setProperty for Bus Volume etc."""
    import wwise_python_lib

    wwise_python_lib.set_plugin_property(
        object_path="\\Master-Mixer Hierarchy\\Default Work Unit\\Reverb_Aux_Bus",
        property_name="Volume",
        value=-96.0,
    )

    args = _find_set_call(mock_waapi)
    assert args["objects"] == [
        {
            "object": "\\Master-Mixer Hierarchy\\Default Work Unit\\Reverb_Aux_Bus",
            "@Volume": -96.0,
        }
    ]


def test_platform_kwarg_added_when_supplied(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.set_plugin_property(
        object_path="\\Effects\\Default Work Unit\\SA_Spatializer",
        property_name="Reflections",
        value=True,
        platform="Windows",
    )

    args = _find_set_call(mock_waapi)
    assert args["objects"][0] == {
        "object": "\\Effects\\Default Work Unit\\SA_Spatializer",
        "platform": "Windows",
        "@Reflections": True,
    }


def test_platform_omitted_by_default(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.set_plugin_property(
        object_path="\\Effects\\Default Work Unit\\SA_Spatializer",
        property_name="Reflections",
        value=True,
    )

    args = _find_set_call(mock_waapi)
    assert "platform" not in args["objects"][0]


def test_empty_object_path_raises(mock_waapi):
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="object_path"):
        wwise_python_lib.set_plugin_property(
            object_path="",
            property_name="Reflections",
            value=False,
        )

    assert mock_waapi.call_count == 0


def test_empty_property_name_raises(mock_waapi):
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="property_name"):
        wwise_python_lib.set_plugin_property(
            object_path="\\Effects\\Default Work Unit\\SA_Spatializer",
            property_name="",
            value=False,
        )

    assert mock_waapi.call_count == 0


def test_none_value_raises(mock_waapi):
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="value"):
        wwise_python_lib.set_plugin_property(
            object_path="\\Effects\\Default Work Unit\\SA_Spatializer",
            property_name="Reflections",
            value=None,
        )

    assert mock_waapi.call_count == 0


def test_mcp_wrapper_delegates(mock_waapi):
    """The public mcp wrapper logs on exception but otherwise just delegates."""
    import wwise_mcp

    wwise_mcp.set_plugin_property(
        object_path="\\Effects\\Default Work Unit\\SA_Spatializer",
        property_name="Reflections",
        value=False,
    )

    args = _find_set_call(mock_waapi)
    assert args["objects"][0]["@Reflections"] is False


def test_command_registered_in_COMMANDS():
    """Wrapper must be registered in COMMANDS or MCP clients cannot call it."""
    import wwise_mcp

    assert "set_plugin_property" in wwise_mcp.COMMANDS
    assert wwise_mcp.COMMANDS["set_plugin_property"].func is wwise_mcp.set_plugin_property

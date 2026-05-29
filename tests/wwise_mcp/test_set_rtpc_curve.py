"""Tests for set_rtpc_curve — binds a ControlInput (Game Parameter / Modulator
/ MIDI) to a target property on an object via the @RTPC list, with a curve
defined by breakpoint array.

Covers backlog TASK-81.3. Critically: the target property can be an Effect
plug-in property (e.g. Steam Audio Spatializer Reflections Mix Level), which
is the entire reason the existing set_attenuation_curve is insufficient.
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


def test_linear_two_point_curve(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.set_rtpc_curve(
        object_path="\\Effects\\Default Work Unit\\SA_Spatializer_AB",
        property_name="ReflectionsMixLevel",
        control_input_ref="\\Game Parameters\\Default Work Unit\\Reflections_AB",
        points=[
            {"x": 0.0, "y": -96.0, "shape": "Linear"},
            {"x": 1.0, "y": 0.0, "shape": "Linear"},
        ],
    )

    args = _find_set_call(mock_waapi)
    assert args["objects"] == [
        {
            "object": "\\Effects\\Default Work Unit\\SA_Spatializer_AB",
            "@RTPC": [
                {
                    "type": "RTPC",
                    "name": "",
                    "@PropertyName": "ReflectionsMixLevel",
                    "@ControlInput": "\\Game Parameters\\Default Work Unit\\Reflections_AB",
                    "@Curve": {
                        "type": "Curve",
                        "points": [
                            {"x": 0.0, "y": -96.0, "shape": "Linear"},
                            {"x": 1.0, "y": 0.0, "shape": "Linear"},
                        ],
                    },
                }
            ],
        }
    ]
    assert args["onNameConflict"] == "merge"
    # @RTPC list has SupportListOperations="false"; listMode must NOT be sent.
    assert "listMode" not in args


def test_mixed_curve_shapes(mock_waapi):
    """Each breakpoint can carry its own shape."""
    import wwise_python_lib

    wwise_python_lib.set_rtpc_curve(
        object_path="\\Effects\\Default Work Unit\\SA_Spatializer_AB",
        property_name="ReflectionsMixLevel",
        control_input_ref="{ABCDEF01-2345-6789-ABCD-EF0123456789}",
        points=[
            {"x": 0.0, "y": -96.0, "shape": "Constant"},
            {"x": 0.5, "y": -24.0, "shape": "Exp3"},
            {"x": 1.0, "y": 0.0, "shape": "Linear"},
        ],
    )

    args = _find_set_call(mock_waapi)
    curve_points = args["objects"][0]["@RTPC"][0]["@Curve"]["points"]
    assert [p["shape"] for p in curve_points] == ["Constant", "Exp3", "Linear"]


def test_empty_points_raises(mock_waapi):
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="points"):
        wwise_python_lib.set_rtpc_curve(
            object_path="\\Effects\\Default Work Unit\\X",
            property_name="ReflectionsMixLevel",
            control_input_ref="\\Game Parameters\\Default Work Unit\\GP",
            points=[],
        )
    assert mock_waapi.call_count == 0


def test_empty_property_name_raises(mock_waapi):
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="property_name"):
        wwise_python_lib.set_rtpc_curve(
            object_path="\\Effects\\Default Work Unit\\X",
            property_name="",
            control_input_ref="\\Game Parameters\\Default Work Unit\\GP",
            points=[{"x": 0.0, "y": 0.0, "shape": "Linear"}],
        )
    assert mock_waapi.call_count == 0


def test_empty_control_input_raises(mock_waapi):
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="control_input"):
        wwise_python_lib.set_rtpc_curve(
            object_path="\\Effects\\Default Work Unit\\X",
            property_name="ReflectionsMixLevel",
            control_input_ref="",
            points=[{"x": 0.0, "y": 0.0, "shape": "Linear"}],
        )
    assert mock_waapi.call_count == 0


def test_invalid_point_shape_raises(mock_waapi):
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="shape"):
        wwise_python_lib.set_rtpc_curve(
            object_path="\\Effects\\Default Work Unit\\X",
            property_name="ReflectionsMixLevel",
            control_input_ref="\\Game Parameters\\Default Work Unit\\GP",
            points=[{"x": 0.0, "y": 0.0, "shape": "Cubic"}],  # invalid shape
        )
    assert mock_waapi.call_count == 0


def test_missing_point_xy_raises(mock_waapi):
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="point"):
        wwise_python_lib.set_rtpc_curve(
            object_path="\\Effects\\Default Work Unit\\X",
            property_name="ReflectionsMixLevel",
            control_input_ref="\\Game Parameters\\Default Work Unit\\GP",
            points=[{"x": 0.0, "shape": "Linear"}],  # missing y
        )
    assert mock_waapi.call_count == 0


def test_mcp_wrapper_delegates(mock_waapi):
    import wwise_mcp

    wwise_mcp.set_rtpc_curve(
        object_path="\\Effects\\Default Work Unit\\SA_Spatializer_AB",
        property_name="ReflectionsMixLevel",
        control_input_ref="\\Game Parameters\\Default Work Unit\\Reflections_AB",
        points=[
            {"x": 0.0, "y": -96.0, "shape": "Linear"},
            {"x": 1.0, "y": 0.0, "shape": "Linear"},
        ],
    )

    args = _find_set_call(mock_waapi)
    assert args["objects"][0]["@RTPC"][0]["@PropertyName"] == "ReflectionsMixLevel"


def test_command_registered_in_COMMANDS():
    """Wrapper must be registered in COMMANDS or MCP clients cannot call it."""
    import wwise_mcp

    assert "set_rtpc_curve" in wwise_mcp.COMMANDS
    assert wwise_mcp.COMMANDS["set_rtpc_curve"].func is wwise_mcp.set_rtpc_curve

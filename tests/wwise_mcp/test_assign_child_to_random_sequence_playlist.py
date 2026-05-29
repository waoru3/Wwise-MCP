"""Tests for wwise_python_lib.assign_child_to_random_sequence_playlist list_mode.

WAAPI ak.wwise.core.object.set accepts listMode in {replaceAll, append}
(schema: C:/Audiokinetic/Wwise_2024.1.13.9056/Authoring/Data/Schemas/WAAPI/
ak.wwise.core.object.set.json:149-155).

These tests pin:
  - default (no list_mode) preserves the pre-change replaceAll behavior
  - list_mode="append" is forwarded to WAAPI
  - invalid list_mode raises before WAAPI call
"""
from __future__ import annotations

import pytest


def test_default_list_mode_is_replaceall(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.assign_child_to_random_sequence_playlist(
        container_path=r"\Actor-Mixer Hierarchy\Default Work Unit\Random_Footsteps",
        child_paths=[r"\Actor-Mixer Hierarchy\Default Work Unit\Footstep_01"],
    )

    args = mock_waapi.call_args.args[1]
    assert args["listMode"] == "replaceAll"


def test_list_mode_append_forwarded(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.assign_child_to_random_sequence_playlist(
        container_path=r"\Actor-Mixer Hierarchy\Default Work Unit\Random_Footsteps",
        child_paths=[r"\Actor-Mixer Hierarchy\Default Work Unit\Footstep_02"],
        list_mode="append",
    )

    args = mock_waapi.call_args.args[1]
    assert args["listMode"] == "append"


def test_invalid_list_mode_rejected(mock_waapi):
    import wwise_python_lib

    with pytest.raises(ValueError, match="list_mode"):
        wwise_python_lib.assign_child_to_random_sequence_playlist(
            container_path=r"\Actor-Mixer Hierarchy\Default Work Unit\Random_Footsteps",
            child_paths=[r"\Actor-Mixer Hierarchy\Default Work Unit\Footstep_02"],
            list_mode="removeAll",
        )

    mock_waapi.assert_not_called()

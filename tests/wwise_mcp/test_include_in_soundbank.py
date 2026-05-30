"""Tests for wwise_python_lib.include_in_soundbank filter parameterization.

WAAPI ak.wwise.core.soundbank.setInclusions accepts a filter list of
events|structures|media (schema:
C:/Audiokinetic/Wwise_2024.1.13.9056/Authoring/Data/Schemas/WAAPI/
ak.wwise.core.soundbank.setInclusions.json:41-52).

These tests pin three behaviors:
  - default filter (None) preserves the pre-change events+structures behavior
  - explicit filter is forwarded verbatim to WAAPI
  - invalid filter values raise before WAAPI is called
"""
from __future__ import annotations

import pytest


def test_default_filter_preserves_events_structures(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.include_in_soundbank(
        include_paths=[r"\Events\Default Work Unit\Play_Footstep"],
        soundbank_path=r"\SoundBanks\Default Work Unit\Level1",
    )

    mock_waapi.assert_called_once()
    uri, args = mock_waapi.call_args.args[0], mock_waapi.call_args.args[1]
    assert uri == "ak.wwise.core.soundbank.setInclusions"
    assert args["inclusions"][0]["filter"] == ["events", "structures"]


def test_explicit_filter_with_media(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.include_in_soundbank(
        include_paths=[r"\Events\Default Work Unit\Play_Footstep"],
        soundbank_path=r"\SoundBanks\Default Work Unit\Level1",
        filter=["events", "structures", "media"],
    )

    args = mock_waapi.call_args.args[1]
    assert args["inclusions"][0]["filter"] == ["events", "structures", "media"]


def test_invalid_filter_value_rejected_before_waapi_call(mock_waapi):
    import wwise_python_lib
    from wwise_errors import WwiseValidationError

    with pytest.raises(WwiseValidationError, match="filter"):
        wwise_python_lib.include_in_soundbank(
            include_paths=[r"\Events\Default Work Unit\Play_Footstep"],
            soundbank_path=r"\SoundBanks\Default Work Unit\Level1",
            filter=["events", "media", "garbage"],
        )

    mock_waapi.assert_not_called()


def test_include_in_soundbank_rejects_non_list_filter(mock_waapi):
    import wwise_python_lib
    from wwise_errors import WwiseValidationError

    with pytest.raises(WwiseValidationError):
        wwise_python_lib.include_in_soundbank(
            [r"\Events\Default Work Unit\Play_Footstep"],
            r"\SoundBanks\Default Work Unit\Level1",
            filter={"events"},
        )

    mock_waapi.assert_not_called()


def test_include_in_soundbank_rejects_non_str_filter_element(mock_waapi):
    import wwise_python_lib
    from wwise_errors import WwiseValidationError

    with pytest.raises(WwiseValidationError):
        wwise_python_lib.include_in_soundbank(
            [r"\Events\Default Work Unit\Play_Footstep"],
            r"\SoundBanks\Default Work Unit\Level1",
            filter=[["events"]],
        )

    mock_waapi.assert_not_called()

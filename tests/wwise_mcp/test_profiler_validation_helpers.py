import pytest
import wwise_python_lib
from wwise_errors import WwiseValidationError


def test_validate_uint32_accepts_zero_and_max():
    wwise_python_lib._validate_uint32(0, "x")
    wwise_python_lib._validate_uint32(0xFFFFFFFF, "x")


@pytest.mark.parametrize("bad", [-1, 0x1_0000_0000, True, 1.5, "3", None])
def test_validate_uint32_rejects(bad):
    with pytest.raises(WwiseValidationError):
        wwise_python_lib._validate_uint32(bad, "voice_pipeline_id")


def test_validate_return_fields_accepts_subset():
    wwise_python_lib._validate_return_fields(["pipelineID"], wwise_python_lib._VOICE_RETURN_FIELDS)


@pytest.mark.parametrize("bad", [[], "pipelineID", ["nope"], [123]])
def test_validate_return_fields_rejects(bad):
    with pytest.raises(WwiseValidationError):
        wwise_python_lib._validate_return_fields(bad, wwise_python_lib._VOICE_RETURN_FIELDS)

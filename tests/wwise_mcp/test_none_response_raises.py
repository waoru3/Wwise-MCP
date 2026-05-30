import pytest
import wwise_python_lib
from wwise_errors import WwiseApiError


def test_require_non_none_passes_through_dict():
    assert wwise_python_lib._require_non_none({"a": 1}, "op") == {"a": 1}
    assert wwise_python_lib._require_non_none({}, "op") == {}  # empty dict is a valid success


def test_require_non_none_raises_on_none():
    with pytest.raises(WwiseApiError):
        wwise_python_lib._require_non_none(None, "ak.wwise.core.profiler.startCapture")


def test_start_capture_raises_when_client_returns_none(mock_waapi):
    mock_waapi.return_value = None
    with pytest.raises(WwiseApiError):
        wwise_python_lib.profiler_start_capture()

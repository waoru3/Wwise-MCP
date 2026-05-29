"""Smoke test: prove the harness can import wwise-mcp source and mock waapi_call.

This test does NOT exercise any feature. It only verifies the conftest sys.path
injection works and pytest-mock can patch the dispatch function. If this fails,
nothing else in this test suite will work.
"""
from __future__ import annotations


def test_can_import_wwise_python_lib():
    import wwise_python_lib  # noqa: WPS433

    assert hasattr(wwise_python_lib, "waapi_call")
    assert hasattr(wwise_python_lib, "include_in_soundbank")


def test_mock_waapi_intercepts_dispatch(mock_waapi):
    import wwise_python_lib  # noqa: WPS433

    wwise_python_lib.waapi_call("ak.wwise.core.getProjectInfo", {})

    mock_waapi.assert_called_once_with("ak.wwise.core.getProjectInfo", {})

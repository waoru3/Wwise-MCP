"""Pytest harness for the Wwise-MCP server scripts.

The server ships as bare scripts under app/scripts/ with no installable
package, so we add that directory to sys.path here, resolved relative to this
repo (NOT a hardcoded absolute path). Tests import wwise_python_lib and
wwise_mcp directly and mock the WAAPI dispatch function (`waapi_call`) to verify
call shaping without a live Wwise Authoring instance.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# tests/wwise_mcp/conftest.py -> parents[2] is the repo root, app/scripts beneath it.
WWISE_MCP_SCRIPTS = Path(__file__).resolve().parents[2] / "app" / "scripts"


def _inject_path() -> None:
    p = str(WWISE_MCP_SCRIPTS)
    if p not in sys.path:
        sys.path.insert(0, p)


_inject_path()


@pytest.fixture
def mock_waapi(mocker):
    """Patch the single WAAPI dispatch function used by wwise_python_lib.

    Returns the mock so tests can assert on call args. Default return is an
    empty dict; tests can override per-call via `mock_waapi.return_value = ...`.
    """
    import wwise_python_lib  # noqa: WPS433 -- import after sys.path injection
    return mocker.patch.object(
        wwise_python_lib,
        "waapi_call",
        return_value={},
    )

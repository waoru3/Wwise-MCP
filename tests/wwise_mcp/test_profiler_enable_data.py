"""Tests for profiler_enable_data.

Covers SDD Task 3 of TASK-81.10. The wrapper builds a payload of
{dataType, enable?} entries and posts to ak.wwise.core.profiler.enableProfilerData.

Critical contract: voiceInspector must be acceptable as a dataType because
getVoiceContributions depends on it.
"""
from __future__ import annotations

import pytest


URI = "ak.wwise.core.profiler.enableProfilerData"


def _find_call(mock_waapi, uri):
    for call in mock_waapi.call_args_list:
        if call.args and call.args[0] == uri:
            return call
    raise AssertionError(
        f"{uri} not in call_args_list: "
        f"{[c.args for c in mock_waapi.call_args_list]}"
    )


def _assert_not_called(mock_waapi):
    mock_waapi.assert_not_called()


# ---------------------------------------------------------------------------
# URI + payload shaping
# ---------------------------------------------------------------------------

def test_enable_data_uses_correct_uri(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_enable_data(["voices"])

    call = _find_call(mock_waapi, URI)
    assert call.args[0] == URI


def test_enable_data_bare_string_omits_enable_key(mock_waapi):
    """Bare string item must NOT inject `enable` (WAAPI defaults to True)."""
    import wwise_python_lib

    wwise_python_lib.profiler_enable_data(["voices"])

    call = _find_call(mock_waapi, URI)
    assert call.args[1] == {"dataTypes": [{"dataType": "voices"}]}


def test_enable_data_tuple_item_carries_enable(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.profiler_enable_data([("voiceInspector", True)])

    call = _find_call(mock_waapi, URI)
    assert call.args[1] == {
        "dataTypes": [{"dataType": "voiceInspector", "enable": True}]
    }


def test_enable_data_list_item_carries_enable_false(mock_waapi):
    """List-of-2 must work identically to tuple, and enable=False round-trips."""
    import wwise_python_lib

    wwise_python_lib.profiler_enable_data([["audioObjects", False]])

    call = _find_call(mock_waapi, URI)
    assert call.args[1] == {
        "dataTypes": [{"dataType": "audioObjects", "enable": False}]
    }


def test_enable_data_mixed_items_preserves_order(mock_waapi):
    """Real-world usage mixes bare strings and pairs in one call."""
    import wwise_python_lib

    wwise_python_lib.profiler_enable_data([
        "voices",
        ("voiceInspector", True),
        ["audioObjects", False],
    ])

    call = _find_call(mock_waapi, URI)
    assert call.args[1] == {
        "dataTypes": [
            {"dataType": "voices"},
            {"dataType": "voiceInspector", "enable": True},
            {"dataType": "audioObjects", "enable": False},
        ]
    }


def test_enable_data_accepts_all_known_data_types(mock_waapi):
    """Smoke: every member of _PROFILER_DATA_TYPES must pass validation.

    Guards against typos drifting between the enum and validation logic.
    """
    import wwise_python_lib

    types_list = sorted(wwise_python_lib._PROFILER_DATA_TYPES)
    wwise_python_lib.profiler_enable_data(types_list)

    call = _find_call(mock_waapi, URI)
    payload = call.args[1]["dataTypes"]
    assert [e["dataType"] for e in payload] == types_list
    assert all("enable" not in e for e in payload)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def test_enable_data_rejects_empty_list(mock_waapi):
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="non-empty list"):
        wwise_python_lib.profiler_enable_data([])
    _assert_not_called(mock_waapi)


@pytest.mark.parametrize("bad", [None, "voices", {"dataType": "voices"}, 42, ()])
def test_enable_data_rejects_non_list(mock_waapi, bad):
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="non-empty list"):
        wwise_python_lib.profiler_enable_data(bad)
    _assert_not_called(mock_waapi)


def test_enable_data_rejects_short_tuple(mock_waapi):
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="str or .str, bool. pair"):
        wwise_python_lib.profiler_enable_data([("voices",)])
    _assert_not_called(mock_waapi)


def test_enable_data_rejects_long_tuple(mock_waapi):
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="str or .str, bool. pair"):
        wwise_python_lib.profiler_enable_data([("voices", True, "extra")])
    _assert_not_called(mock_waapi)


@pytest.mark.parametrize("bad_enable", [1, 0, "true", None, [], {}])
def test_enable_data_rejects_non_bool_enable(mock_waapi, bad_enable):
    """`enable` must be a real bool (int 1/0 must NOT silently pass)."""
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="second element must be bool"):
        wwise_python_lib.profiler_enable_data([("voices", bad_enable)])
    _assert_not_called(mock_waapi)


def test_enable_data_rejects_unknown_string_dataType(mock_waapi):
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="unknown dataType"):
        wwise_python_lib.profiler_enable_data(["badType"])
    _assert_not_called(mock_waapi)


def test_enable_data_rejects_unknown_pair_dataType(mock_waapi):
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="unknown dataType"):
        wwise_python_lib.profiler_enable_data([("badType", True)])
    _assert_not_called(mock_waapi)


@pytest.mark.parametrize("bad_item", [None, 42, {"dataType": "voices"}, b"voices"])
def test_enable_data_rejects_wrong_item_type(mock_waapi, bad_item):
    """Non-str / non-pair items must raise before hitting WAAPI."""
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="str or .str, bool. pair"):
        wwise_python_lib.profiler_enable_data([bad_item])
    _assert_not_called(mock_waapi)


@pytest.mark.parametrize("bad_dt", [[], {}, 42, None, ("voices",)])
def test_enable_data_rejects_unhashable_pair_first_element(mock_waapi, bad_dt):
    """Pair with non-str first element must raise WwiseValidationError, not
    leak a TypeError from the `in _PROFILER_DATA_TYPES` set-membership check.

    Regression: `[]` / `{}` are unhashable; without an explicit isinstance
    guard, `dt not in _PROFILER_DATA_TYPES` raises raw `TypeError`.
    """
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="first element must be str"):
        wwise_python_lib.profiler_enable_data([(bad_dt, True)])
    _assert_not_called(mock_waapi)


def test_enable_data_validation_failure_aborts_before_waapi_call(mock_waapi):
    """Bad item later in list must abort the whole call — no partial dispatch."""
    from wwise_errors import WwiseValidationError
    import wwise_python_lib

    with pytest.raises(WwiseValidationError, match="unknown dataType"):
        wwise_python_lib.profiler_enable_data(["voices", "badType"])
    _assert_not_called(mock_waapi)


# ---------------------------------------------------------------------------
# Error wrapping
# ---------------------------------------------------------------------------

def test_enable_data_wraps_waapi_failure_as_WwiseApiError(mocker):
    from wwise_errors import WwiseApiError
    import wwise_python_lib

    mocker.patch.object(
        wwise_python_lib,
        "waapi_call",
        side_effect=RuntimeError("kaboom"),
    )

    with pytest.raises(WwiseApiError) as exc_info:
        wwise_python_lib.profiler_enable_data([("voiceInspector", True)])

    assert exc_info.value.operation == URI
    assert exc_info.value.details["error_type"] == "RuntimeError"
    assert exc_info.value.details["data_types"] == [
        {"dataType": "voiceInspector", "enable": True}
    ]


def test_enable_data_does_not_double_wrap_pylib_errors(mocker):
    """A WwisePyLibError raised inside waapi_call must propagate unchanged."""
    from wwise_errors import WwiseApiError
    import wwise_python_lib

    original = WwiseApiError(
        "already wrapped",
        operation="something.else",
        details={"reason": "test"},
    )
    mocker.patch.object(wwise_python_lib, "waapi_call", side_effect=original)

    with pytest.raises(WwiseApiError) as exc_info:
        wwise_python_lib.profiler_enable_data(["voices"])

    assert exc_info.value is original


# ---------------------------------------------------------------------------
# Response handling
# ---------------------------------------------------------------------------

def test_enable_data_returns_waapi_response(mock_waapi):
    import wwise_python_lib

    mock_waapi.return_value = {"some": "payload"}
    assert wwise_python_lib.profiler_enable_data(["voices"]) == {"some": "payload"}


def test_enable_data_normalises_none_to_empty_dict(mock_waapi):
    import wwise_python_lib

    mock_waapi.return_value = None
    assert wwise_python_lib.profiler_enable_data(["voices"]) == {}


# ---------------------------------------------------------------------------
# MCP shim delegation
# ---------------------------------------------------------------------------

def test_mcp_shim_delegates_to_library_bare_string(mock_waapi):
    import wwise_mcp

    mock_waapi.return_value = {}
    result = wwise_mcp.profiler_enable_data(["voices"])

    assert result == {}
    call = _find_call(mock_waapi, URI)
    assert call.args[1] == {"dataTypes": [{"dataType": "voices"}]}


def test_mcp_shim_forwards_pair_items_without_hardcoding(mock_waapi):
    """Regression: shim must NOT hardcode a single dataType (e.g. 'voices').

    We pass a varied input (voiceInspector + False enable + list form) and
    require the recorded payload to match exactly.
    """
    import wwise_mcp

    wwise_mcp.profiler_enable_data([("voiceInspector", True), ["audioObjects", False]])

    call = _find_call(mock_waapi, URI)
    assert call.args[1] == {
        "dataTypes": [
            {"dataType": "voiceInspector", "enable": True},
            {"dataType": "audioObjects", "enable": False},
        ]
    }


# ---------------------------------------------------------------------------
# COMMANDS registry
# ---------------------------------------------------------------------------

def test_enable_data_task12_cleanup_baseline_payload(mock_waapi):
    """Task 12 E2E smoke pins this exact disable-list at the end of capture.

    Pinning the payload shape protects the cleanup contract: voiceInspector
    and audioObjects must be flipped off (in that order) so a subsequent
    profiler session starts from a known-clean state.
    """
    import wwise_python_lib

    wwise_python_lib.profiler_enable_data([
        ("voiceInspector", False),
        ("audioObjects", False),
    ])

    call = _find_call(mock_waapi, URI)
    assert call.args[1] == {
        "dataTypes": [
            {"dataType": "voiceInspector", "enable": False},
            {"dataType": "audioObjects", "enable": False},
        ]
    }


def test_enable_data_registered_in_COMMANDS():
    import wwise_mcp

    assert "profiler_enable_data" in wwise_mcp.COMMANDS
    entry = wwise_mcp.COMMANDS["profiler_enable_data"]
    assert entry.func is wwise_mcp.profiler_enable_data
    # Docstring must surface the voiceInspector dependency + the arg name.
    assert "voiceInspector" in entry.doc
    assert "data_types" in entry.doc

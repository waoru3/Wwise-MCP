"""Tests for wwise_python_lib.post_event wait parameterization.

Wwise-MCP's local waapi_call dispatcher (wwise_session.py:49-126) accepts a
keyword-only `wait` flag. When wait=False the call is enqueued fire-and-forget
and the dispatcher returns None immediately; when wait=True the call blocks
on the dispatcher reply queue until the WAAPI side completes. post_event has
historically hard-coded wait=False; this test pins the new opt-in synchronous
path while preserving the default fire-and-forget behavior.
"""
from __future__ import annotations


def _find_post_event_call(mock_waapi):
    """post_event invokes ensure_game_obj, which performs its own waapi_call
    invocations BEFORE the ak.soundengine.postEvent dispatch. Pick out the
    postEvent call explicitly instead of assuming it is the only one."""
    matches = [
        c for c in mock_waapi.call_args_list
        if c.args and c.args[0] == "ak.soundengine.postEvent"
    ]
    assert matches, (
        "ak.soundengine.postEvent was not dispatched; "
        f"observed URIs: {[c.args[0] for c in mock_waapi.call_args_list if c.args]}"
    )
    assert len(matches) == 1, (
        f"expected exactly one ak.soundengine.postEvent dispatch, got {len(matches)}"
    )
    return matches[0]


def test_default_wait_is_false(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.post_event(
        event_name="Play_Footstep",
        game_obj="TestEmitter",
        delay_ms=0,
    )

    post_call = _find_post_event_call(mock_waapi)
    assert post_call.kwargs.get("wait") is False


def test_wait_true_forwarded(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.post_event(
        event_name="Play_Footstep",
        game_obj="TestEmitter",
        delay_ms=0,
        wait=True,
    )

    post_call = _find_post_event_call(mock_waapi)
    assert post_call.kwargs.get("wait") is True


def test_due_in_translated_from_delay_ms(mock_waapi):
    import wwise_python_lib

    wwise_python_lib.post_event(
        event_name="Play_Footstep",
        game_obj="TestEmitter",
        delay_ms=250,
    )

    # delay_ms=250 -> due_in=0.25s. Pin the conversion so a future
    # refactor doesn't silently drift the unit.
    post_call = _find_post_event_call(mock_waapi)
    assert post_call.kwargs.get("due_in") == 0.25

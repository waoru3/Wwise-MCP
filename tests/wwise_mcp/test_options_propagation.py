"""Regression tests for WwiseSession WAAPI options propagation."""
from __future__ import annotations


class _RecordingClient:
    def __init__(self):
        self.calls = []
        self.disconnected = False

    def call(self, uri, *args, **kwargs):
        self.calls.append((uri, args, kwargs))
        return {"ok": True}

    def disconnect(self):
        self.disconnected = True


def test_dispatcher_forwards_options_to_waapi_client_as_named_argument():
    """waapi-client only honors options when passed as the named options arg."""
    import wwise_session

    client = _RecordingClient()
    dispatcher = wwise_session.WaapiDispatcher(client=client)
    dispatcher.start()

    try:
        req = dispatcher.enqueue(
            "ak.wwise.core.profiler.getVoices",
            {"time": 12345},
            {"return": ["pipelineID", "gameObjectName"]},
            want_reply=True,
        )
        status, data = req["reply_q"].get(timeout=1.0)
    finally:
        dispatcher.stop()

    assert status == "ok"
    assert data == {"ok": True}
    assert client.calls == [
        (
            "ak.wwise.core.profiler.getVoices",
            ({"time": 12345},),
            {"options": {"return": ["pipelineID", "gameObjectName"]}},
        )
    ]

"""Tests for media streaming and auth service."""

import respx

from jiocloud import JioCloudClient


@respx.mock
def test_media_get_stream_url() -> None:
    respx.put("https://jaws-api.jioaicloud.com/nms/metadata/accessdate/obj123").respond(
        200, json={}
    )
    respx.get("https://www.jioaicloud.com/jaws/nms/media/auth").respond(
        200,
        json={"url": "https://jaws-stream.jioaicloud.com/media/hls/test.m3u8?token=abc"},
    )

    client = JioCloudClient()
    stream_url = client.media.get_stream_url("obj123")
    assert "test.m3u8" in stream_url
    assert "token=abc" in stream_url

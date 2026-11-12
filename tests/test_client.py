"""Tests for JioCloudClient and service modules."""

import os
import tempfile

import respx

from jiocloud import JioCloudClient


@respx.mock
def test_auth_services() -> None:
    respx.post("https://api.jioaicloud.com/account/jioid/sendotp").respond(204)
    respx.post("https://api.jioaicloud.com/account/jioid/verifyotp").respond(
        200, json={"userId": "test_user_123"}
    )

    client = JioCloudClient()
    client.auth.send_otp(mobile_number="+910000000000")
    res = client.auth.verify_otp(mobile_number="+910000000000", otp="123456")
    assert res["userId"] == "test_user_123"


@respx.mock
def test_email_auth_services() -> None:
    respx.post("https://api.jioaicloud.com/account/login/otp/send").respond(204)
    respx.post("https://api.jioaicloud.com/account/otp/login").respond(
        200, json={"userId": "email_user_456"}
    )

    client = JioCloudClient()
    client.auth.send_otp(email_id="user@example.com")
    res = client.auth.verify_otp(email_id="user@example.com", otp="123456")
    assert res["userId"] == "email_user_456"


@respx.mock
def test_file_services() -> None:
    respx.get("https://jaws-api.jioaicloud.com/nms/metadata").respond(
        200, json={"files": [{"fileId": "f1", "name": "doc.txt", "size": 1024}]}
    )
    respx.get("https://jaws-api.jioaicloud.com/nms/metadata/version/f1").respond(
        200, json={"fileId": "f1", "name": "doc.txt", "size": 1024}
    )
    respx.put("https://jaws-api.jioaicloud.com/nms/metadata/1.0").respond(200, json={})
    respx.delete("https://jaws-api.jioaicloud.com/nms/metadata/1.0").respond(200, json={})

    client = JioCloudClient(user_id="u1", device_key="d1")
    files = client.files.list()
    assert len(files) == 1
    assert files[0].name == "doc.txt"
    assert files[0].size == 1024

    f_meta = client.files.get("f1")
    assert f_meta.id == "f1"

    client.files.rename("f1", "new.txt")
    client.files.move("f1", "folder_id")
    client.files.delete("f1")


@respx.mock
def test_folder_services() -> None:
    respx.get("https://jaws-api.jioaicloud.com/nms/folders").respond(
        200, json={"folders": [{"folderId": "fold1", "name": "Photos"}]}
    )
    respx.post("https://jaws-api.jioaicloud.com/nms/folders").respond(
        200, json={"folderId": "fold2", "name": "Documents"}
    )

    client = JioCloudClient()
    folders = client.folders.list()
    assert len(folders) == 1
    assert folders[0].name == "Photos"

    new_fold = client.folders.create("Documents")
    assert new_fold.name == "Documents"


@respx.mock
def test_file_and_folder_unexpected_schema() -> None:
    respx.get("https://jaws-api.jioaicloud.com/nms/metadata").respond(
        200, json={"files": "not_a_list"}
    )
    respx.get("https://jaws-api.jioaicloud.com/nms/folders").respond(200, json={"folders": 12345})
    client = JioCloudClient()
    assert client.files.list() == []
    assert client.folders.list() == []


@respx.mock
def test_transfer_services() -> None:
    respx.get("https://jaws-dl.jioaicloud.com/download/files/f1").respond(
        200, content=b"hello jiocloud"
    )
    respx.post("https://jaws-upload.jioaicloud.com/upload/files").respond(
        200, json={"fileId": "f2", "name": "test.txt"}
    )

    client = JioCloudClient()

    with tempfile.TemporaryDirectory() as tmpdir:
        dest = os.path.join(tmpdir, "downloaded.txt")
        progress_called = []
        client.transfer.download(
            "f1",
            dest,
            progress_callback=lambda d, t: progress_called.append(d),
        )
        assert os.path.exists(dest)
        with open(dest, "rb") as f:
            assert f.read() == b"hello jiocloud"
        assert len(progress_called) > 0

        src = os.path.join(tmpdir, "upload.txt")
        with open(src, "wb") as f:
            f.write(b"upload content")

        upload_res = client.transfer.upload(src, parent_id="fold1")
        assert upload_res["fileId"] == "f2"

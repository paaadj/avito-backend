import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    "tag_id, feature_id, content",
    [
        (1, 1, {"title": "some_title", "text": "some_text", "url": "some_url"}),
        (3, 1, {"title": "some_title", "text": "some_text", "url": "some_url"}),
        (2, 2, {"title": "some_title1", "text": "some_text1", "url": "some_url1"}),
        (3, 2, {"title": "some_title1", "text": "some_text1", "url": "some_url1"}),
    ],
)
def test_get_user_banner_by_user(
    client: TestClient, user_token, tag_id, feature_id, content
):
    response = client.get(
        f"/user_banner?tag_id={tag_id}&feature_id={feature_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.json()["content"] == content


@pytest.mark.parametrize(
    "tag_id, feature_id, content",
    [
        (1, 1, {"title": "some_title", "text": "some_text", "url": "some_url"}),
        (3, 1, {"title": "some_title", "text": "some_text", "url": "some_url"}),
        (2, 2, {"title": "some_title1", "text": "some_text1", "url": "some_url1"}),
        (3, 2, {"title": "some_title1", "text": "some_text1", "url": "some_url1"}),
    ],
)
def test_get_user_banner_by_admin(
    client: TestClient, admin_token, tag_id, feature_id, content
):
    response = client.get(
        f"/user_banner?tag_id={tag_id}&feature_id={feature_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.json()["content"] == content


def test_without_token(client):
    response = client.get("/user_banner?tag_id=1&feature_id=1")
    assert response.status_code == 401


def test_get_non_existing_banner(
    client: TestClient,
    user_token,
):
    response = client.get(
        "/user_banner?tag_id=2&feature_id=1",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 404


def test_get_non_active_banner(
    client: TestClient,
    user_token,
):
    response = client.get(
        "/user_banner?tag_id=2&feature_id=3",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403


def test_incorrect_tag(
    client: TestClient,
    user_token,
):
    response = client.get(
        "/user_banner?tag_id=123&feature_id=3",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 400


def test_incorrect_feature(
    client: TestClient,
    user_token,
):
    response = client.get(
        "/user_banner?tag_id=3&feature_id=123",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 400


def test_cache(client: TestClient, user_token, admin_token, resetup):
    feature_id = 1
    tag_id = 1
    content = {"title": "some_title", "text": "some_text", "url": "some_url"}
    response = client.get(
        f"/user_banner?tag_id={tag_id}&feature_id={feature_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.json()["content"] == content
    new_content = {
        "content": {
            "title": "some_title123",
            "text": "some_text123",
            "url": "some_url123"
        }
    }
    response = client.patch(
        "/banner/1",
        json=new_content,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    response = client.get(
        f"/user_banner?tag_id={tag_id}&feature_id={feature_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.json()["content"] == content
    response = client.get(
        f"/user_banner?tag_id={tag_id}&feature_id={feature_id}&use_last_revision=true",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.json()["content"] == new_content["content"]


def test_non_active_banner(client: TestClient, user_token, admin_token):
    feature_id = 3
    tag_id = 2
    content = {"title": "some_title1", "text": "some_text1", "url": "some_url1"}
    user_response = client.get(
        f"/user_banner?tag_id={tag_id}&feature_id={feature_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert user_response.status_code == 403
    admin_response = client.get(
        f"/user_banner?tag_id={tag_id}&feature_id={feature_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    #  Проверка, что закешированное значение тоже не передается
    user_response = client.get(
        f"/user_banner?tag_id={tag_id}&feature_id={feature_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert user_response.status_code == 403
    assert admin_response.json()["content"] == content

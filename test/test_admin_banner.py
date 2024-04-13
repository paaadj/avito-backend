from fastapi.testclient import TestClient


def test_create_banner_by_user(client: TestClient, user_token):
    new_banner = {
        "tag_ids": [2],
        "feature_id": 1,
        "content": {"title": "some_title", "text": "some_text", "url": "some_url"},
        "is_active": True
    }
    response = client.post(
        "/banner",
        headers={"Authorization": f"Bearer {user_token}"},
        json=new_banner
    )
    assert response.status_code == 403


def test_create_banner(client: TestClient, admin_token, resetup):
    new_banner = {
        "tag_ids": [2],
        "feature_id": 1,
        "content": {"title": "some_title", "text": "some_text", "url": "some_url"},
        "is_active": True
    }
    response = client.post(
        "/banner",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=new_banner
    )
    assert response.status_code == 201
    assert response.json().get("banner_id") is not None


def test_get_banners(client: TestClient, admin_token, user_token):
    response = client.get(
        "/banner",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content) > 0
    response = client.get(
        "/banner",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403


def test_create_banner_with_non_existing_tag(client: TestClient, admin_token):
    new_banner = {
        "tag_ids": [1, 2, 4],
        "feature_id": 2,
        "content": {"title": "some_title", "text": "some_text", "url": "some_url"},
        "is_active": True
    }
    response = client.post(
        "/banner",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=new_banner
    )
    assert response.status_code == 400


def test_create_banner_with_non_existing_feature(client: TestClient, admin_token):
    new_banner = {
        "tag_ids": [1, 2],
        "feature_id": 4,
        "content": {"title": 1213},
        "is_active": True
    }
    response = client.post(
        "/banner",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=new_banner
    )
    assert response.status_code == 400


def test_update_banner(client: TestClient, admin_token, resetup):
    old_banner_response = client.get(
        "/user_banner?tag_id=1&feature_id=1&use_last_revision=true",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert old_banner_response.status_code == 200
    new_banner = {
        "tag_ids": [2,],
        "content": {"title": 1213}
    }
    patch_response = client.patch(
        "/banner/1",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=new_banner
    )
    assert patch_response.status_code == 200
    new_banner_response = client.get(
        "/user_banner?tag_id=1&feature_id=1&use_last_revision=true",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert new_banner_response.status_code == 404

    new_banner_response = client.get(
        "/user_banner?tag_id=2&feature_id=1&use_last_revision=true",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert new_banner_response.status_code == 200


def test_delete_banner(client: TestClient, admin_token, resetup):
    old_banner_response = client.get(
        "/user_banner?tag_id=1&feature_id=1&use_last_revision=true",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert old_banner_response.status_code == 200
    delete_response = client.delete(
        "/banner/1",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert delete_response.status_code == 204
    old_banner_response = client.get(
        "/user_banner?tag_id=1&feature_id=1&use_last_revision=true",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert old_banner_response.status_code == 404


def test_delete_banner_by_user(client: TestClient, user_token):
    old_banner_response = client.get(
        "/user_banner?tag_id=1&feature_id=1&use_last_revision=true",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert old_banner_response.status_code == 200
    delete_response = client.delete(
        "/banner/1",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert delete_response.status_code == 403
    old_banner_response = client.get(
        "/user_banner?tag_id=1&feature_id=1&use_last_revision=true",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert old_banner_response.status_code == 200


def test_update_banner_by_user(client: TestClient, user_token):
    old_banner_response = client.get(
        "/user_banner?tag_id=1&feature_id=1&use_last_revision=true",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert old_banner_response.status_code == 200
    new_banner = {
        "tag_ids": [2,],
        "content": {"title": 1213}
    }
    patch_response = client.patch(
        "/banner/1",
        headers={"Authorization": f"Bearer {user_token}"},
        json=new_banner
    )
    assert patch_response.status_code == 403
    new_banner_response = client.get(
        "/user_banner?tag_id=1&feature_id=1&use_last_revision=true",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert new_banner_response.status_code == 200

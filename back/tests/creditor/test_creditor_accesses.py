from django.test import Client


def test_human_cant_list_creditors(user_client: Client):
    response = user_client.get('/api/creditor/')
    response_data = response.json()
    assert response.status_code == 403, response_data


def test_human_cant_view_creditor(user_client: Client):
    response = user_client.get("/api/creditor/1")
    response_data = response.json()
    assert response.status_code == 403, response_data


def test_human_cant_create_creditor(user_client: Client):
    response = user_client.post('/api/creditor/', data={})
    response_data = response.json()
    assert response.status_code == 403, response_data


def test_human_cant_delete_creditor(user_client: Client):
    response = user_client.delete("/api/creditor/1")
    response_data = response.json()
    assert response.status_code == 403, response_data


def test_human_cant_edit_creditor(user_client: Client):
    response = user_client.patch("/api/creditor/1", data={})
    response_data = response.json()
    assert response.status_code == 403, response_data

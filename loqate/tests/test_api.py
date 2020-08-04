def test_health_check_get_method(client):
    response = client.get('/health')
    assert response.status_code == 200


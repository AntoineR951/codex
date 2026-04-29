from fastapi.testclient import TestClient

from app import CHATBOTS, app


client = TestClient(app)


def test_health():
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json()['status'] == 'ok'


def test_run_flow():
    created = client.post('/runs', json={'company_name': 'ACME'})
    assert created.status_code == 200
    run = created.json()
    assert run['company_name'] == 'ACME'
    assert len(run['queries']) >= 4

    executed = client.post(f"/runs/{run['id']}/execute")
    assert executed.status_code == 200
    data = executed.json()
    assert len(data['results']) == len(data['queries']) * len(CHATBOTS)

    report = client.get(f"/runs/{run['id']}/report")
    assert report.status_code == 200
    payload = report.json()
    assert payload['row_count'] == len(data['queries'])
    assert len(payload['rows']) == len(data['queries'])


def test_home_page():
    r = client.get("/")
    assert r.status_code == 200
    assert "AIRepute" in r.text

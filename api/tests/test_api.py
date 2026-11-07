from fastapi.testclient import TestClient

from app.main import app
from app.schemas import DataStatus

client = TestClient(app)
SITE = "/api/sites/demo-brahmaputra"


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert "demo-brahmaputra" in r.json()["sites"]


def test_list_sites_marks_synthetic():
    sites = client.get("/api/sites").json()
    assert sites and all(s["data_status"] == DataStatus.synthetic.value for s in sites)
    assert all(s["verified"] is False for s in sites)


def test_site_endpoints():
    for path in ["", "/scenes", "/summary", "/timeseries", "/evidence"]:
        assert client.get(SITE + path).status_code == 200, path


def test_unknown_site_404():
    assert client.get("/api/sites/nope/summary").status_code == 404


def test_path_traversal_rejected():
    assert client.get("/api/sites/..%2F..%2Fapp/summary").status_code == 404


def test_passport_labels_and_values():
    r = client.get(SITE + "/passport", params={"lon": 94.0, "lat": 26.9})
    assert r.status_code == 200
    p = r.json()
    assert p["change_class"] == "water_gained"
    labels = [e["label"] for e in p["evidence"]]
    assert labels[0] == "Observed" and labels[1] == "Derived"
    assert "Context" in labels and labels[-1] == "Hypothesis"
    assert p["evidence"][0]["values"]["delta_hh_db"] == -12.0


def test_passport_flags_steep_terrain():
    p = client.get(SITE + "/passport", params={"lon": 94.1, "lat": 27.08}).json()
    assert any("Steep terrain" in lim for lim in p["limitations"])


def test_passport_outside_site():
    assert client.get(SITE + "/passport", params={"lon": 80.0, "lat": 20.0}).status_code == 422

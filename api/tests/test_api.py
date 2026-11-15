from pathlib import Path

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


def test_layers_rewrites_urls_and_serves_png():
    m = client.get(SITE + "/layers").json()
    url = m["layers"][0]["png"]
    assert url.startswith("http") and url.endswith("/files/web/change_class.png")
    r = client.get(url)
    assert r.status_code == 200 and r.content.startswith(b"\x89PNG")


def test_assets_reject_json_and_traversal():
    assert client.get(SITE + "/files/site.json").status_code == 404
    assert client.get(SITE + "/files/..%2F..%2Fapp%2Fmain.py").status_code == 404


def test_pipeline_output_without_context(tmp_path):
    """science/analysis writes no context.json; evidence and passport must still work,
    and extra analysis fields must pass through."""
    import json
    import shutil

    from app.store import Store, get_store

    src = Path(__file__).resolve().parent.parent / "fixtures" / "demo-brahmaputra"
    dst = tmp_path / "demo-brahmaputra"
    shutil.copytree(src, dst)
    (dst / "context.json").unlink()
    a = json.loads((dst / "analysis.json").read_text(encoding="utf-8"))
    a["area_ranges_km2"] = {"water_gained": [8.0, 12.0]}
    (dst / "analysis.json").write_text(json.dumps(a), encoding="utf-8")

    app.dependency_overrides[get_store] = lambda: Store(tmp_path)
    try:
        assert client.get(SITE + "/evidence").json() == []
        assert client.get(SITE + "/summary").json()["area_ranges_km2"]["water_gained"] == [8.0, 12.0]
        p = client.get(SITE + "/passport", params={"lon": 94.0, "lat": 26.9})
        assert p.status_code == 200
        assert "Context" not in [e["label"] for e in p.json()["evidence"]]
    finally:
        app.dependency_overrides.clear()


def test_evidence_unknown_site_404():
    assert client.get("/api/sites/nope/evidence").status_code == 404

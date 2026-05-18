from __future__ import annotations

from fastapi.testclient import TestClient

from app import app
from pressure_skill.analyzer.profile import CommunicationProfile, RelationRole
from pressure_skill.counterparty_store import save_counterparty


def test_counterparty_api_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv("PRESSURE_DATA_DIR", str(tmp_path / "cp"))
    save_counterparty(
        tmp_path / "cp",
        "boss",
        CommunicationProfile(relation=RelationRole.MANAGER),
        display_name="Boss",
        merge=False,
    )
    client = TestClient(app)
    r = client.get("/api/v1/counterparties")
    assert r.status_code == 200
    assert any(x["slug"] == "boss" for x in r.json()["items"])
    r2 = client.get("/api/v1/counterparties/boss")
    assert r2.status_code == 200
    assert r2.json()["profile"]["relation"] == "manager"

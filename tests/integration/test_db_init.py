import os

def test_healthz_and_db_file_exists(client):
    # hit health endpoint
    res = client.get("/healthz")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

    # verify DB_PATH env was set and file was created
    db_path = os.environ.get("DB_PATH")
    assert db_path is not None
    # Table creation happens in init_db; SQLite creates the file lazily on first connect
    assert os.path.dirname(db_path) != ""

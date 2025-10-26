def _fake_review():
    return {
        "summary": "Stubbed review",
        "suggestions": ["Do X", "Consider Y"],
        "findings": [{"type": "style", "detail": "nit", "line": 1}],
        "rating": 6,
    }

def test_create_and_get_snippet_with_stubbed_llm(monkeypatch, client):
    # Stub LLM before calling endpoints
    import app.llm as llm
    monkeypatch.setattr(llm, "review_code", lambda language, code, lines: _fake_review())

    payload = {
        "language": "python",
        "code": "def add(a,b):return a+b\n",
        "lines": "56-57",
    }

    # POST /snippets
    res = client.post("/snippets", json=payload)
    assert res.status_code == 201, res.text
    body = res.json()
    assert "id" in body and body["review"]["rating"] == 6

    snippet_id = body["id"]

    # GET /snippets/{id}
    res2 = client.get(f"/snippets/{snippet_id}")
    assert res2.status_code == 200, res2.text
    body2 = res2.json()
    assert body2["language"] == "python"
    assert body2["review"]["summary"] == "Stubbed review"

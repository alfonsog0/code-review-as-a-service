from pydantic import ValidationError
from app.schemas import ReviewPayload, SnippetCreate, SnippetOut, CreateResponse

def test_reviewpayload_valid():
    rp = ReviewPayload(
        summary="Good base, missing docs",
        suggestions=["Add docstrings", "Use logging"],
        findings=[{"type": "style", "detail": "PEP8 spacing", "line": 1}],
        rating=7,
    )
    assert rp.rating == 7
    assert isinstance(rp.suggestions, list)
    assert isinstance(rp.findings, list)

def test_reviewpayload_missing_summary_raises():
    try:
        ReviewPayload(suggestions=[], findings=[], rating=5)
        assert False, "Expected ValidationError"
    except ValidationError:
        pass

def test_reviewpayload_rating_bounds():
    for bad in (-1, 11):
        try:
            ReviewPayload(summary="x", suggestions=[], findings=[], rating=bad)
            assert False, "Expected ValidationError"
        except ValidationError:
            pass

def test_snippetcreate_minimal():
    sc = SnippetCreate(language="python", code="print('hi')\n")
    assert sc.language == "python"
    assert sc.lines is None

def test_snippetout_and_createresponse_shapes():
    rp = ReviewPayload(summary="ok", suggestions=[], findings=[], rating=5)
    out = SnippetOut(id="123", language="python", code="print()", lines=None, review=rp)
    cr = CreateResponse(id="123", review=rp)
    assert out.id == "123"
    assert cr.review.rating == 5

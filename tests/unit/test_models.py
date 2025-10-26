from app.models import Snippet

def test_snippet_model_autogenerates_uuid():
    s = Snippet(language="python", code="print('hi')")
    assert s.id is not None
    assert len(s.id) > 10
    assert s.language == "python"
    assert s.review is None

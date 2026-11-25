from app.sentiment import analyze


def test_positive():
    score, label = analyze("I absolutely love this, it's wonderful and great!")
    assert label == "positive"
    assert score > 0


def test_negative():
    score, label = analyze("This is terrible, awful and I hate it.")
    assert label == "negative"
    assert score < 0


def test_neutral_empty():
    score, label = analyze("")
    assert label == "neutral"
    assert score == 0.0

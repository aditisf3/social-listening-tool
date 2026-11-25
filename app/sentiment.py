"""Basic sentiment analysis using VADER (lexicon-based, no model download)."""
from __future__ import annotations

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()


def analyze(text: str) -> tuple[float, str]:
    """Return (compound_score, label) for a piece of text.

    label is one of: positive, neutral, negative.
    """
    if not text:
        return 0.0, "neutral"
    score = _analyzer.polarity_scores(text)["compound"]
    if score >= 0.05:
        label = "positive"
    elif score <= -0.05:
        label = "negative"
    else:
        label = "neutral"
    return round(score, 4), label

"""Tests for sentiment scanner composite scoring and reddit analysis."""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "market_intel"))

from sentiment_scanner import (
    compute_composite_sentiment,
    _analyze_reddit_posts,
    get_tv_consensus,
)


class TestCompositeSentiment:
    def test_all_components_present(self):
        result = compute_composite_sentiment(
            naaim={"exposure": 80},
            fear_greed={"score": 60},
            vix={"current": 18},
            reddit={"wsb": {"bull_ratio": 0.7}},
            tv_consensus={"total": 10, "buy_pct": 70},
        )
        assert "composite" in result
        assert "label" in result
        assert "components" in result
        assert 0 <= result["composite"] <= 100

    def test_extreme_greed_label(self):
        result = compute_composite_sentiment(
            naaim={"exposure": 180},
            fear_greed={"score": 90},
            vix={"current": 10},
            reddit={"wsb": {"bull_ratio": 0.95}},
            tv_consensus={"total": 10, "buy_pct": 95},
        )
        assert result["label"] == "EXTREME GREED"

    def test_extreme_fear_label(self):
        result = compute_composite_sentiment(
            naaim={"exposure": 10},
            fear_greed={"score": 5},
            vix={"current": 45},
            reddit={"wsb": {"bull_ratio": 0.1}},
            tv_consensus={"total": 10, "buy_pct": 5},
        )
        assert result["label"] == "EXTREME FEAR"

    def test_missing_components(self):
        result = compute_composite_sentiment(
            naaim=None, fear_greed={"score": 50},
            vix=None, reddit=None, tv_consensus=None,
        )
        assert result["composite"] == 50.0  # Only fear_greed at 50

    def test_all_none_returns_neutral(self):
        result = compute_composite_sentiment(None, None, None, None, None)
        assert result["composite"] == 50
        assert result["label"] == "N/A"

    def test_weight_normalization(self):
        # Only 2 components, weights should renormalize
        result = compute_composite_sentiment(
            naaim={"exposure": 100},  # score 50
            fear_greed={"score": 50},  # score 50
            vix=None, reddit=None, tv_consensus=None,
        )
        assert 45 <= result["composite"] <= 55


class TestRedditAnalysis:
    def test_bullish_sentiment(self):
        posts = [
            {"title": "AAPL to the moon! Buy buy buy!", "selftext": "bullish breakout calls", "score": 100},
            {"title": "Rocket to $300 bullish moon", "selftext": "long calls upside", "score": 200},
        ]
        result = _analyze_reddit_posts(posts, "wsb")
        assert result["sentiment"] == "bullish"
        assert result["bull_ratio"] > 0.5

    def test_bearish_sentiment(self):
        posts = [
            {"title": "Market crash incoming puts", "selftext": "bear recession dump sell", "score": 100},
            {"title": "Short everything bearish crash", "selftext": "bubble correction", "score": 200},
        ]
        result = _analyze_reddit_posts(posts, "wsb")
        assert result["sentiment"] == "bearish"
        assert result["bull_ratio"] < 0.5

    def test_empty_posts(self):
        result = _analyze_reddit_posts([], "wsb")
        assert result["posts_analyzed"] == 0
        assert result["bull_ratio"] == 0.5  # neutral default

    def test_ticker_extraction(self):
        posts = [
            {"title": "$NVDA is going up $AAPL too", "selftext": "", "score": 10},
        ]
        result = _analyze_reddit_posts(posts, "stocks")
        tickers = [t for t, _ in result["hot_tickers"]]
        assert "NVDA" in tickers or "AAPL" in tickers

    def test_common_words_excluded(self):
        posts = [
            {"title": "THE CEO AND CFO ARE NOT", "selftext": "", "score": 1},
        ]
        result = _analyze_reddit_posts(posts, "stocks")
        ticker_names = [t for t, _ in result["hot_tickers"]]
        assert "THE" not in ticker_names
        assert "CEO" not in ticker_names
        assert "AND" not in ticker_names


class TestTVConsensus:
    def test_bullish_consensus(self):
        tv_data = {
            "AAPL": {"recommendation": "STRONG_BUY"},
            "NVDA": {"recommendation": "BUY"},
            "TSLA": {"recommendation": "BUY"},
        }
        result = get_tv_consensus(tv_data)
        assert result["consensus"] == "BULLISH"
        assert result["buys"] == 3

    def test_mixed_consensus(self):
        tv_data = {
            "AAPL": {"recommendation": "BUY"},
            "NVDA": {"recommendation": "SELL"},
            "TSLA": {"recommendation": "NEUTRAL"},
        }
        result = get_tv_consensus(tv_data)
        assert result["consensus"] == "MIXED"

    def test_empty_data(self):
        result = get_tv_consensus({})
        assert result["consensus"] == "N/A"

    def test_none_entries_skipped(self):
        tv_data = {"AAPL": None, "NVDA": {"recommendation": "BUY"}}
        result = get_tv_consensus(tv_data)
        assert result["total"] == 1

"""Tests for macro_monitor — risk assessment logic without live API calls."""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "market_intel"))

from unittest.mock import patch
import pandas as pd


class TestAssessLiquidityRisk:
    """Test the risk scoring engine with mock data (no API calls)."""

    def _make_data(self, **overrides):
        """Build a baseline macro data dict."""
        data = {
            "liquidity": {
                "fed_assets": 7_500_000,
                "tga_balance": 700_000,
                "rrp": 500_000,
                "net_liquidity": 6_300_000,
                "sofr": 4.3,
            },
            "yields": {"us2y": 4.0, "us10y": 4.3, "spread_2s10s": 0.3},
            "usdjpy": {"current": 150.0, "week_change_pct": 0.5},
            "sp500": {"current": 500.0, "week_change_pct": 1.0},
            "fear_greed": {"score": 50, "rating": "Neutral"},
            "move": {"current": 85, "week_change_pct": -2.0},
            "tga_direct": None,
        }
        for key, val in overrides.items():
            if "." in key:
                parts = key.split(".")
                data[parts[0]][parts[1]] = val
            else:
                data[key] = val
        return data

    @patch("macro_monitor.fetch_net_liquidity_history")
    def test_green_when_all_normal(self, mock_hist):
        from macro_monitor import assess_liquidity_risk
        mock_hist.return_value = pd.DataFrame()  # no history = skip trend check
        data = self._make_data()
        result = assess_liquidity_risk(data)
        assert result["risk_level"] == "GREEN"
        assert result["score"] < 3

    @patch("macro_monitor.fetch_net_liquidity_history")
    def test_red_when_sofr_high(self, mock_hist):
        from macro_monitor import assess_liquidity_risk
        mock_hist.return_value = pd.DataFrame()
        data = self._make_data(**{"liquidity.sofr": 6.0})
        result = assess_liquidity_risk(data)
        assert result["score"] >= 3
        assert any("SOFR" in a for a in result["alerts"])

    @patch("macro_monitor.fetch_net_liquidity_history")
    def test_red_when_move_above_stop_loss(self, mock_hist):
        from macro_monitor import assess_liquidity_risk
        mock_hist.return_value = pd.DataFrame()
        data = self._make_data()
        data["move"]["current"] = 140
        result = assess_liquidity_risk(data)
        assert any("MOVE" in a and "STOP LOSS" in a for a in result["alerts"])

    @patch("macro_monitor.fetch_net_liquidity_history")
    def test_yellow_when_move_warning(self, mock_hist):
        from macro_monitor import assess_liquidity_risk
        mock_hist.return_value = pd.DataFrame()
        data = self._make_data()
        data["move"]["current"] = 115
        result = assess_liquidity_risk(data)
        assert any("MOVE" in a and "ELEVATED" in a for a in result["alerts"])

    @patch("macro_monitor.fetch_net_liquidity_history")
    def test_yen_carry_unwind_alert(self, mock_hist):
        from macro_monitor import assess_liquidity_risk
        mock_hist.return_value = pd.DataFrame()
        data = self._make_data()
        data["usdjpy"]["week_change_pct"] = -3.0
        result = assess_liquidity_risk(data)
        assert any("yen carry" in a.lower() for a in result["alerts"])

    @patch("macro_monitor.fetch_net_liquidity_history")
    def test_yield_curve_inversion(self, mock_hist):
        from macro_monitor import assess_liquidity_risk
        mock_hist.return_value = pd.DataFrame()
        data = self._make_data()
        data["yields"]["spread_2s10s"] = -0.2
        result = assess_liquidity_risk(data)
        assert any("inverted" in w.lower() for w in result["warnings"])

    @patch("macro_monitor.fetch_net_liquidity_history")
    def test_extreme_greed_warning(self, mock_hist):
        from macro_monitor import assess_liquidity_risk
        mock_hist.return_value = pd.DataFrame()
        data = self._make_data()
        data["fear_greed"]["score"] = 90
        data["fear_greed"]["rating"] = "Extreme Greed"
        result = assess_liquidity_risk(data)
        assert any("GREED" in w for w in result["warnings"])

    @patch("macro_monitor.fetch_net_liquidity_history")
    def test_handles_missing_data(self, mock_hist):
        from macro_monitor import assess_liquidity_risk
        mock_hist.return_value = pd.DataFrame()
        # All None — should not crash
        data = {
            "liquidity": {"sofr": None, "net_liquidity": None},
            "yields": {},
            "usdjpy": None,
            "sp500": None,
            "fear_greed": None,
            "move": None,
        }
        result = assess_liquidity_risk(data)
        assert result["risk_level"] in ("GREEN", "YELLOW", "RED")
        assert isinstance(result["score"], int)


class TestFormatRiskReport:
    @patch("macro_monitor.fetch_net_liquidity_history")
    def test_report_is_string(self, mock_hist):
        from macro_monitor import assess_liquidity_risk, format_risk_report
        mock_hist.return_value = pd.DataFrame()
        data = {
            "liquidity": {"sofr": 4.3, "net_liquidity": 6_300_000,
                          "fed_assets": 7_500_000, "tga_balance": 700_000, "rrp": 500_000},
            "yields": {"us2y": 4.0, "us10y": 4.3, "spread_2s10s": 0.3},
            "usdjpy": {"current": 150.0, "week_change_pct": 0.5},
            "fear_greed": {"score": 50, "rating": "Neutral"},
            "move": {"current": 85, "week_change_pct": -1.0},
            "sp500": {"current": 500.0, "week_change_pct": 1.0},
        }
        result = assess_liquidity_risk(data)
        report = format_risk_report(result)
        assert isinstance(report, str)
        assert "MACRO RISK LEVEL" in report
        assert "ACTION" in report

    @patch("macro_monitor.fetch_net_liquidity_history")
    def test_fmt_trillions_edge_cases(self, mock_hist):
        from macro_monitor import _fmt_trillions, _fmt_pct
        assert _fmt_trillions(None) == "N/A"
        assert "T" in _fmt_trillions(7_500_000)
        assert "B" in _fmt_trillions(7_000)  # 7000M = $7.0B
        assert "M" in _fmt_trillions(50)
        assert _fmt_pct(None) == "N/A"
        assert "%" in _fmt_pct(4.3)

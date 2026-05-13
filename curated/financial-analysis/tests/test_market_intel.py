"""Tests for market_intel/ — config loading, data source helpers."""
import os
import pytest


class TestConfig:
    def test_config_imports(self):
        from market_intel.config import FRED_SERIES, TRIGGERS, SENTIMENT
        assert isinstance(FRED_SERIES, dict)
        assert "fed_assets" in FRED_SERIES
        assert isinstance(TRIGGERS, dict)
        assert isinstance(SENTIMENT, dict)

    def test_fred_series_keys(self):
        from market_intel.config import FRED_SERIES
        expected = {"fed_assets", "tga_balance", "rrp", "sofr", "cpi", "nfp", "us2y", "us10y", "fed_funds", "vix"}
        assert expected == set(FRED_SERIES.keys())

    def test_trigger_thresholds(self):
        from market_intel.config import TRIGGERS
        assert TRIGGERS["move_stop_loss"] > TRIGGERS["move_warning"]
        assert TRIGGERS["sofr_reduce_threshold"] > 0

    def test_sentiment_thresholds(self):
        from market_intel.config import SENTIMENT
        assert SENTIMENT["fear_greed_extreme_greed"] > SENTIMENT["fear_greed_extreme_fear"]
        assert SENTIMENT["naaim_overbought"] > 0
        assert SENTIMENT["aaii_bull_extreme"] > 0


class TestStrategyRegistry:
    def test_registry_loads(self, project_root):
        import json
        path = os.path.join(project_root, "strategy_lab", "strategy_registry.json")
        with open(path) as f:
            registry = json.load(f)
        assert "AU" in registry
        au = registry["AU"]
        assert "strategies" in au
        assert "regime_mapping" in au
        assert len(au["strategies"]) > 0

    def test_regime_mapping_values(self, project_root):
        import json
        path = os.path.join(project_root, "strategy_lab", "strategy_registry.json")
        with open(path) as f:
            registry = json.load(f)
        mapping = registry["AU"]["regime_mapping"]
        strategies = registry["AU"]["strategies"]
        for regime, strategy_key in mapping.items():
            assert strategy_key in strategies, f"Regime {regime} maps to unknown strategy {strategy_key}"

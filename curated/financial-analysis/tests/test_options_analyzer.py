"""Tests for Black-Scholes greeks and options analytics."""
import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "market_intel"))

from options_analyzer import (
    black_scholes_greeks,
    compute_put_call_ratio,
    compute_iv_skew,
)


class TestBlackScholesGreeks:
    def test_call_delta_is_positive(self):
        g = black_scholes_greeks(S=100, K=100, T=0.25, r=0.05, sigma=0.3, option_type="call")
        assert g["delta"] > 0

    def test_put_delta_is_negative(self):
        g = black_scholes_greeks(S=100, K=100, T=0.25, r=0.05, sigma=0.3, option_type="put")
        assert g["delta"] < 0

    def test_gamma_is_positive(self):
        g = black_scholes_greeks(S=100, K=100, T=0.25, r=0.05, sigma=0.3)
        assert g["gamma"] > 0

    def test_theta_is_negative_for_call(self):
        g = black_scholes_greeks(S=100, K=100, T=0.25, r=0.05, sigma=0.3, option_type="call")
        assert g["theta"] < 0

    def test_atm_call_delta_near_half(self):
        g = black_scholes_greeks(S=100, K=100, T=0.25, r=0.05, sigma=0.3, option_type="call")
        assert 0.45 < g["delta"] < 0.65

    def test_deep_itm_call_delta_near_one(self):
        g = black_scholes_greeks(S=200, K=100, T=0.25, r=0.05, sigma=0.3, option_type="call")
        assert g["delta"] > 0.95

    def test_zero_inputs_return_zeros(self):
        g = black_scholes_greeks(S=0, K=100, T=0.25, r=0.05, sigma=0.3)
        assert g == {"delta": 0, "gamma": 0, "theta": 0, "vega": 0}

    def test_expired_option_returns_zeros(self):
        g = black_scholes_greeks(S=100, K=100, T=0, r=0.05, sigma=0.3)
        assert g == {"delta": 0, "gamma": 0, "theta": 0, "vega": 0}

    def test_zero_vol_returns_zeros(self):
        g = black_scholes_greeks(S=100, K=100, T=0.25, r=0.05, sigma=0)
        assert g == {"delta": 0, "gamma": 0, "theta": 0, "vega": 0}


class TestPutCallRatio:
    def test_basic_ratio(self, sample_option_chain):
        calls, puts = sample_option_chain
        result = compute_put_call_ratio(calls, puts)
        assert result["volume_ratio"] is not None
        assert result["oi_ratio"] is not None
        assert result["call_volume"] == 3400
        assert result["put_volume"] == 3600

    def test_interpretation_bearish(self, sample_option_chain):
        calls, puts = sample_option_chain
        # Make puts heavily dominate
        puts_heavy = puts.copy()
        puts_heavy["volume"] = [5000, 6000, 9000, 11000, 7000]
        result = compute_put_call_ratio(calls, puts_heavy)
        assert result["volume_ratio"] > 1.0

    def test_zero_call_volume(self, sample_option_chain):
        calls, puts = sample_option_chain
        calls_zero = calls.copy()
        calls_zero["volume"] = 0
        result = compute_put_call_ratio(calls_zero, puts)
        assert result["volume_ratio"] is None
        assert result["interpretation"] == "INSUFFICIENT DATA"


class TestIVSkew:
    def test_skew_calculation(self, sample_option_chain):
        calls, puts = sample_option_chain
        result = compute_iv_skew(calls, puts, spot=100.0)
        assert "skew" in result
        assert "put_iv_avg" in result
        assert "call_iv_avg" in result
        assert "interpretation" in result

    def test_positive_skew_means_puts_expensive(self, sample_option_chain):
        calls, puts = sample_option_chain
        result = compute_iv_skew(calls, puts, spot=100.0)
        # Puts in our fixture have higher IV than calls on average
        assert result["skew"] > 0

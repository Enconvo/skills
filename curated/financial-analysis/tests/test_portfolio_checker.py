"""Tests for portfolio_checker — validation, FCN status, observation dates, autocall proximity."""
import json
import pytest
from datetime import datetime
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "market_intel"))


class TestPortfolioValidation:
    """Test the _validate_fcn_note function."""

    def test_valid_note_passes(self):
        from portfolio_checker import _validate_fcn_note
        note = {
            "isin": "XS1234567890",
            "product": "Test FCN",
            "amount": 100000,
            "coupon": 8.0,
            "expiry": "2027-01-01",
            "underlyings": [
                {"ticker": "AAPL", "strike": 150.0, "call_price": 200.0, "initial": 200.0}
            ]
        }
        errors = _validate_fcn_note(note, 0)
        assert errors == []

    def test_missing_required_fields(self):
        from portfolio_checker import _validate_fcn_note
        note = {"isin": "XS123"}
        errors = _validate_fcn_note(note, 0)
        assert len(errors) >= 4  # missing product, amount, coupon, expiry, underlyings

    def test_empty_underlyings(self):
        from portfolio_checker import _validate_fcn_note
        note = {
            "isin": "XS123", "product": "Test", "amount": 100000,
            "coupon": 8.0, "expiry": "2027-01-01", "underlyings": []
        }
        errors = _validate_fcn_note(note, 0)
        assert any("non-empty list" in e for e in errors)

    def test_missing_underlying_fields(self):
        from portfolio_checker import _validate_fcn_note
        note = {
            "isin": "XS123", "product": "Test", "amount": 100000,
            "coupon": 8.0, "expiry": "2027-01-01",
            "underlyings": [{"ticker": "AAPL"}]  # missing strike, call_price
        }
        errors = _validate_fcn_note(note, 0)
        assert any("strike" in e for e in errors)
        assert any("call_price" in e for e in errors)

    def test_zero_strike_rejected(self):
        from portfolio_checker import _validate_fcn_note
        note = {
            "isin": "XS123", "product": "Test", "amount": 100000,
            "coupon": 8.0, "expiry": "2027-01-01",
            "underlyings": [{"ticker": "AAPL", "strike": 0, "call_price": 200.0}]
        }
        errors = _validate_fcn_note(note, 0)
        assert any("positive" in e for e in errors)

    def test_negative_strike_rejected(self):
        from portfolio_checker import _validate_fcn_note
        note = {
            "isin": "XS123", "product": "Test", "amount": 100000,
            "coupon": 8.0, "expiry": "2027-01-01",
            "underlyings": [{"ticker": "AAPL", "strike": -10, "call_price": 200.0}]
        }
        errors = _validate_fcn_note(note, 0)
        assert any("positive" in e for e in errors)


class TestObservationDates:
    """Test observation date calculation logic."""

    def test_next_observation_basic(self):
        from portfolio_checker import next_observation_date
        today = datetime(2026, 3, 1)
        next_obs, days = next_observation_date(today, "2027-07-15", "2025-07-15")
        assert next_obs is not None
        assert days >= 0

    def test_next_observation_past_expiry(self):
        from portfolio_checker import next_observation_date
        today = datetime(2028, 1, 1)
        next_obs, days = next_observation_date(today, "2027-07-15", "2025-07-15")
        assert next_obs is None
        assert days is None

    def test_all_observation_dates(self):
        from portfolio_checker import all_observation_dates
        dates = all_observation_dates("2027-07-15", "2025-07-15")
        assert len(dates) > 0
        # All dates should be before expiry
        expiry = datetime(2027, 7, 15)
        for d in dates:
            assert d <= expiry

    def test_obs_date_weekend_shift(self):
        from portfolio_checker import _obs_date_for_month
        # A known Saturday: 2026-01-03 is a Saturday
        dt = _obs_date_for_month(2026, 1, 3)
        assert dt.weekday() < 5  # Must be a weekday (Mon-Fri)

    def test_obs_date_clamped_to_month_end(self):
        from portfolio_checker import _obs_date_for_month
        # February doesn't have 31 days
        dt = _obs_date_for_month(2026, 2, 31)
        assert dt.month == 2 or dt.month == 3  # Feb 28 or shifted to March if weekend


class TestRedaction:
    """Test the redaction helpers."""

    def test_amt_normal(self):
        from portfolio_checker import _amt, REDACT
        # Force non-redact mode for testing
        import portfolio_checker
        old = portfolio_checker.REDACT
        portfolio_checker.REDACT = False
        assert _amt(500000) == "$500,000"
        portfolio_checker.REDACT = old

    def test_amt_redacted(self):
        from portfolio_checker import _amt
        import portfolio_checker
        old = portfolio_checker.REDACT
        portfolio_checker.REDACT = True
        assert _amt(500000) == "***"
        portfolio_checker.REDACT = old

    def test_isin_normal(self):
        from portfolio_checker import _isin
        import portfolio_checker
        old = portfolio_checker.REDACT
        portfolio_checker.REDACT = False
        assert _isin("XS3111495985") == "XS3111495985"
        portfolio_checker.REDACT = old

    def test_isin_redacted(self):
        from portfolio_checker import _isin
        import portfolio_checker
        old = portfolio_checker.REDACT
        portfolio_checker.REDACT = True
        result = _isin("XS3111495985")
        assert result.startswith("XS31")
        assert result.endswith("5985")
        assert "****" in result
        portfolio_checker.REDACT = old

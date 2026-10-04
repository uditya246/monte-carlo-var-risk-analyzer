import pytest
import numpy as np
import pandas as pd
from risk_model import (
    calculate_log_returns,
    calculate_statistics,
    calculate_historical_var,
    run_monte_carlo_simulation,
    calculate_monte_carlo_var
)
from data_loader import fetch_data

def test_calculate_log_returns():
    prices = pd.Series([100, 105, 102, 110])
    returns = calculate_log_returns(prices)
    assert len(returns) == 3
    assert np.isclose(returns.iloc[0], np.log(105/100))

def test_calculate_statistics():
    returns = pd.Series([0.01, -0.02, 0.03, 0.00, -0.01])
    stats = calculate_statistics(returns)
    assert 'mean' in stats
    assert 'volatility' in stats
    assert 'annualized_return' in stats
    assert 'annualized_volatility' in stats
    assert np.isclose(stats['mean'], returns.mean())
    assert np.isclose(stats['volatility'], returns.std(ddof=1)) # pandas std uses ddof=1 by default

def test_run_monte_carlo_simulation():
    # Test reproducibility
    sim1 = run_monte_carlo_simulation(0.001, 0.02, 1000, seed=42)
    sim2 = run_monte_carlo_simulation(0.001, 0.02, 1000, seed=42)
    np.testing.assert_array_equal(sim1, sim2)
    
    assert len(sim1) == 1000

def test_calculate_historical_var():
    returns = pd.Series([-0.05, -0.01, 0.00, 0.02, 0.03])
    var = calculate_historical_var(returns, 100000, 0.95)
    assert var < 0
    assert np.isclose(var, 100000 * np.percentile(returns, 5))

def test_calculate_monte_carlo_var():
    sim_returns = np.array([-0.05, -0.01, 0.00, 0.02, 0.03])
    var = calculate_monte_carlo_var(sim_returns, 100000, 0.99)
    assert var < 0
    assert np.isclose(var, 100000 * np.percentile(sim_returns, 1))

def test_fetch_data_invalid_ticker():
    prices, error = fetch_data("INVALID_TICKER_XYZ", "1Y")
    assert error is not None
    assert prices is None

import numpy as np
import pandas as pd
import scipy.stats as stats

def calculate_log_returns(prices: pd.Series):
    """Calculate daily logarithmic returns."""
    # log_return = ln(P_t / P_(t-1))
    log_returns = np.log(prices / prices.shift(1)).dropna()
    return log_returns

def calculate_statistics(log_returns: pd.Series):
    """Calculate mean and volatility of returns."""
    mean_return = log_returns.mean()
    daily_volatility = log_returns.std()
    
    # Annualized metrics assuming 252 trading days
    annualized_return = mean_return * 252
    annualized_volatility = daily_volatility * np.sqrt(252)
    
    return {
        'mean': mean_return,
        'volatility': daily_volatility,
        'annualized_return': annualized_return,
        'annualized_volatility': annualized_volatility
    }

def run_monte_carlo_simulation(mean_return, volatility, num_simulations=10000, seed=42):
    """Generate simulated returns using a normal distribution."""
    # Set seed for reproducibility
    if seed is not None:
        np.random.seed(seed)
        
    # simulated_return = mean_return + volatility * random_normal()
    # Using numpy's normal distribution generator
    simulated_returns = np.random.normal(mean_return, volatility, num_simulations)
    return simulated_returns

def calculate_historical_var(log_returns: pd.Series, investment_amount: float, confidence_level: float):
    """Calculate Value-at-Risk using historical method."""
    percentile = (1 - confidence_level) * 100
    var_return = np.percentile(log_returns, percentile)
    var_amount = investment_amount * var_return
    return var_amount

def calculate_monte_carlo_var(simulated_returns: np.ndarray, investment_amount: float, confidence_level: float):
    """Calculate Value-at-Risk using Monte Carlo simulation."""
    percentile = (1 - confidence_level) * 100
    var_return = np.percentile(simulated_returns, percentile)
    var_amount = investment_amount * var_return
    return var_amount

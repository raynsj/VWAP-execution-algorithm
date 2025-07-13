import pandas as pd
import numpy as np
import keras
from collections import defaultdict

# -------------------------------------------------------------------------------------
# ---------- Function to create sequences of data for training the TLN model ----------
# -------------------------------------------------------------------------------------
def create_tln_sequences(df, lookback_window, horizon):
    """
    Creates sequences of data for training the TLN model.
    X: Input features (lookback_window minutes of price and volume).
    y: Target data (horizon minutes of price and market volume for loss calculation).
    """

    features = ['avg_price', 'volume']
    X, y = [], []

    # Group by day to create sequences within each trading day
    daily_groups = df.groupby(df.index.date)
    
    for date, group in daily_groups:
        feature_data = group[features].values
        price_volume_data = group[['avg_price', 'volume']].values
        
        if len(feature_data) < lookback_window + horizon:
            continue
            
        for i in range(len(feature_data) - lookback_window - horizon + 1):
            X.append(feature_data[i : i + lookback_window])
            y.append(price_volume_data[i + lookback_window : i + lookback_window + horizon])
            
    return np.array(X), np.array(y)


# ------------------------------------------------------------
# ---------- Custom loss function for the TLN model ----------
# ------------------------------------------------------------
def vwap_loss(y_true, y_pred):
    """
    Custom Keras loss function to minimize the quadratic VWAP slippage.
    The model predicts the allocation schedule (y_pred).
    y_true contains the actual market prices and volumes needed to calculate the benchmark.
    """
    
    # Extract future prices and market volumes from y_true
    future_prices = y_true[:, :, 0]
    market_volumes = y_true[:, :, 1]

    # Calculate the VWAP achieved by the model's predicted schedule
    model_trade_value = keras.ops.sum(y_pred * future_prices, axis=1)
    model_total_shares = keras.ops.sum(y_pred, axis=1)
    model_vwap = model_trade_value / (model_total_shares + 1e-8) # Add epsilon for stability

    # Calculate the benchmark VWAP using market volumes
    benchmark_trade_value = keras.ops.sum(market_volumes * future_prices, axis=1)
    benchmark_total_volume = keras.ops.sum(market_volumes, axis=1)
    benchmark_vwap = benchmark_trade_value / (benchmark_total_volume + 1e-8)

    # The loss is the squared difference between the two VWAPs (slippage)
    slippage = model_vwap - benchmark_vwap
    return keras.ops.square(slippage)


# ----------------------------------------
# ---------- Evaluate functions ----------
# ----------------------------------------
def calculate_benchmark_vwap(daily_df):
    """Calculates the true market VWAP for a given day."""
    if daily_df.empty or daily_df['volume'].sum() == 0:
        return np.nan
    return (daily_df['avg_price'] * daily_df['volume']).sum() / daily_df['volume'].sum()


def evaluate_tln_strategy(test_df, model, total_shares_to_trade, LOOKBACK, HORIZON, FEATURES):
    """
    Backtests the trained TLN model on the test data.
    """
    daily_groups = test_df.groupby(test_df.index.date)
    results = []

    for date, day_data in daily_groups:
        if len(day_data) < LOOKBACK + HORIZON:
            continue

        benchmark_vwap = calculate_benchmark_vwap(day_data)
        if pd.isna(benchmark_vwap):
            continue

        # Simulate trading for the day
        total_value_of_trades = 0
        total_shares_traded = 0
        
        # We trade from the first possible moment until the end of the day
        for i in range(len(day_data) - LOOKBACK):
            # Prepare the input sequence for the model
            input_sequence = day_data[i : i + LOOKBACK][FEATURES].values
            input_sequence = np.expand_dims(input_sequence, axis=0) # Add batch dimension

            # Predict the allocation schedule for the next HORIZON minutes
            predicted_schedule = model.predict(input_sequence, verbose=0)[0]
            
            # Determine shares to trade in the next minute based on the schedule
            # We only execute the first step of the horizon prediction
            shares_to_trade_next_minute = predicted_schedule[0] * total_shares_to_trade
            
            # Get the price for the trade
            execution_price = day_data.iloc[i + LOOKBACK]['avg_price']
            
            # Accumulate trade value and shares
            total_value_of_trades += shares_to_trade_next_minute * execution_price
            total_shares_traded += shares_to_trade_next_minute

        if total_shares_traded == 0:
            continue

        model_vwap = total_value_of_trades / total_shares_traded
        
        # Calculate slippage
        slippage = model_vwap - benchmark_vwap
        slippage_bps = (slippage / benchmark_vwap) * 10000  # in basis points

        results.append({
            'date': date,
            'benchmark_vwap': benchmark_vwap,
            'model_vwap': model_vwap,
            'slippage': slippage,
            'slippage_bps': slippage_bps
        })
        
    return pd.DataFrame(results)
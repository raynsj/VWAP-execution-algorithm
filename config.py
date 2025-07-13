# --- Data Configuration ---
DATA_FILE_PATH = 'META_1min_firstratedata.csv'

# --- Model & Sequence Configuration ---
LOOKBACK = 120  # Use the past 120 minutes of data to make a prediction
HORIZON = 30    # Predict the execution schedule for the next 30 minutes
FEATURES = ['avg_price', 'volume']
NUM_FEATURES = len(FEATURES)

# --- Model Training Parameters ---
EPOCHS = 20
BATCH_SIZE = 64
VALIDATION_SPLIT = 0.2
LEARNING_RATE = 0.001

# --- Backtesting Configuration ---
TOTAL_SHARES_TO_TRADE = 1_000_000
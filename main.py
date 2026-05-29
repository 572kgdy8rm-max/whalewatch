import json
from pathlib import Path

# Load pre-calculated data (updated daily by GitHub Action)
DATA_FILE = Path(__file__).parent / "data" / "signals.json"

def load_signal_data():
    if DATA_FILE.exists():
        with open(DATA_FILE) as f:
            data = json.load(f)
            # Convert list to dict for easy lookup
            signals = {}
            for s in data.get('all_signals', []):
                signals[s['ticker']] = s
            return signals
    return {}

@app.get("/v1/top10")
def get_top10():
    """Get top 10 ranked signals"""
    if DATA_FILE.exists():
        with open(DATA_FILE) as f:
            data = json.load(f)
            return {
                "top_10": data.get('top_10', []),
                "last_updated": data.get('last_updated'),
                "total_tickers": data.get('total_tickers', 0)
            }
    return {"top_10": [], "message": "Data loading, check back soon"}

@app.get("/v1/signal/{ticker}")
def get_signal(ticker):
    ticker = ticker.upper()
    signals = load_signal_data()
    
    if ticker in signals:
        return signals[ticker]
    
    # Fallback to real-time calculation if not in cache
    # ... existing code ...
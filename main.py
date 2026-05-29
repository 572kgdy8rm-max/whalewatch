from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

@app.get("/")
def root():
    return {"message": "WhaleWatch API Live", "time": datetime.now().isoformat()}

@app.get("/v1/signal/{ticker}")
def get_signal(ticker):
    return {
        "ticker": ticker.upper(),
        "genius_rating": "🔥 TOP",
        "position_pct": 5,
        "win_rate": 100,
        "total_trades": 4,
        "excess_vs_spy": 35,
        "timestamp": datetime.now().isoformat()
    }
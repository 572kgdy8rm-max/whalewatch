from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI()

# THIS FIXES THE CORS ERROR
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all frontends (including GitHub Pages)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "WhaleWatch API Live", "time": datetime.now().isoformat()}

@app.get("/v1/signal/{ticker}")
def get_signal(ticker):
    # Hardcoded data for now
    data = {
        "NVDA": {"wins": 4, "total": 4, "excess": 35},
        "TSM": {"wins": 2, "total": 3, "excess": 18},
        "LMT": {"wins": 6, "total": 6, "excess": 22},
        "BABA": {"wins": 3, "total": 4, "excess": 19},
    }
    ticker = ticker.upper()
    stats = data.get(ticker, {"wins": 0, "total": 0, "excess": 0})
    
    win_rate = (stats["wins"] / stats["total"]) * 100 if stats["total"] > 0 else 0
    
    # Simple rating logic
    if win_rate >= 75:
        rating = "🔥 TOP"
        position = 5
    elif win_rate >= 60:
        rating = "✅ GOOD"
        position = 2.5
    elif win_rate >= 50:
        rating = "⚠️ SMALL"
        position = 1
    else:
        rating = "❌ AVOID"
        position = 0
    
    return {
        "ticker": ticker,
        "genius_rating": rating,
        "position_pct": position,
        "win_rate": round(win_rate, 1),
        "total_trades": stats["total"],
        "excess_vs_spy": stats["excess"],
        "timestamp": datetime.now().isoformat()
    }
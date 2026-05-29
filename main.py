from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from core import calculate_stats

app = FastAPI(title="WhaleWatch Supercomputer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "🐋 WhaleWatch API Live",
        "status": "healthy",
        "time": datetime.now().isoformat()
    }

@app.get("/v1/signal/{ticker}")
def get_signal(ticker: str):
    result = calculate_stats(ticker)
    if not result:
        raise HTTPException(status_code=404, detail=f"No reliable data for {ticker.upper()}")
    return result

@app.get("/v1/top10")
def get_top10():
    # You can expand this list later
    watchlist = ["NVDA", "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "AVGO", "LMT", "TSM"]
    
    results = []
    for t in watchlist:
        stats = calculate_stats(t)
        if stats:
            results.append(stats)
    
    results.sort(key=lambda x: x.get('wilson_score', 0), reverse=True)
    
    return {
        "top_10": results[:10],
        "last_updated": datetime.now().isoformat(),
        "count": len(results)
    }
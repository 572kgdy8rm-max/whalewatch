from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import httpx
import math

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# WILSON SCORE (Genius Rating)
# ============================================================
def wilson_lower_bound(win_rate, total_trades):
    if total_trades == 0:
        return 0
    p = win_rate / 100
    n = total_trades
    z = 1.96
    lower = (p + (z*z)/(2*n) - z * ((p*(1-p) + (z*z)/(4*n))/n)**0.5) / (1 + (z*z)/n)
    return max(0, lower) * 100

# ============================================================
# SIGNAL DATA (Hardcoded for now)
# ============================================================
SIGNAL_DATA = {
    "NVDA": {"wins": 4, "total": 4, "excess": 35, "max_dd": -5},
    "LMT": {"wins": 6, "total": 6, "excess": 22, "max_dd": -2},
    "TSM": {"wins": 2, "total": 3, "excess": 18, "max_dd": -8},
    "BABA": {"wins": 3, "total": 4, "excess": 19, "max_dd": -12},
    "NU": {"wins": 3, "total": 3, "excess": 42, "max_dd": 0},
    "AVGO": {"wins": 2, "total": 3, "excess": 15, "max_dd": -5},
}

# ============================================================
# ROOT ENDPOINT
# ============================================================
@app.get("/")
def root():
    return {"message": "WhaleWatch API Live", "time": datetime.now().isoformat()}

# ============================================================
# GENIUS RATING ENDPOINT
# ============================================================
@app.get("/v1/signal/{ticker}")
def get_signal(ticker):
    ticker = ticker.upper()
    stats = SIGNAL_DATA.get(ticker, {"wins": 0, "total": 0, "excess": 0})
    
    win_rate = (stats["wins"] / stats["total"]) * 100 if stats["total"] > 0 else 0
    adjusted = wilson_lower_bound(win_rate, stats["total"])
    
    if adjusted >= 75:
        rating = "🔥 TOP"
        position = 5
    elif adjusted >= 65:
        rating = "✅ GOOD"
        position = 2.5
    elif adjusted >= 55:
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

# ============================================================
# LIVE PRICE ENDPOINT (Yahoo Finance - FREE)
# ============================================================
@app.get("/v1/live/{ticker}")
async def get_live_price(ticker):
    """Get real-time price from Yahoo Finance (no API key needed)"""
    ticker = ticker.upper()
    
    # Map for international tickers
    ticker_map = {
        "0700.HK": "0700.HK", "BABA": "BABA", "TSM": "TSM",
        "NOVO-B": "NOVO-B.CO", "WDS": "WDS.AX", "XRO": "XRO.AX"
    }
    yahoo_ticker = ticker_map.get(ticker, ticker)
    
    try:
        async with httpx.AsyncClient() as client:
            # Yahoo Finance API endpoint
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_ticker}"
            resp = await client.get(url, timeout=10)
            data = resp.json()
            
            result = data["chart"]["result"][0]
            meta = result["meta"]
            
            current_price = meta.get("regularMarketPrice")
            previous_close = meta.get("previousClose")
            market_state = meta.get("marketState", "UNKNOWN")
            
            if current_price is None:
                raise ValueError("No price data")
            
            change = current_price - previous_close if previous_close else 0
            change_percent = (change / previous_close) * 100 if previous_close else 0
            
            return {
                "ticker": ticker,
                "price": round(current_price, 2),
                "change": round(change, 2),
                "change_percent": round(change_percent, 2),
                "market_state": market_state,
                "currency": meta.get("currency", "USD"),
                "source": "Yahoo Finance",
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Yahoo Finance error: {str(e)}")

# ============================================================
# MULTI-LIVE PRICES (for portfolio view)
# ============================================================
@app.get("/v1/live/batch")
async def get_batch_prices(tickers: str):
    """Get prices for multiple tickers: /v1/live/batch?tickers=NVDA,TSLA,AAPL"""
    ticker_list = [t.strip().upper() for t in tickers.split(",")]
    results = {}
    
    for ticker in ticker_list[:10]:  # Limit to 10 per request
        try:
            async with httpx.AsyncClient() as client:
                yahoo_ticker = ticker
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_ticker}"
                resp = await client.get(url, timeout=5)
                data = resp.json()
                meta = data["chart"]["result"][0]["meta"]
                results[ticker] = {
                    "price": round(meta.get("regularMarketPrice", 0), 2),
                    "change_percent": round(((meta.get("regularMarketPrice", 0) - meta.get("previousClose", 1)) / meta.get("previousClose", 1)) * 100, 2)
                }
        except:
            results[ticker] = {"price": 0, "change_percent": 0}
    
    return {"prices": results, "timestamp": datetime.now().isoformat()}
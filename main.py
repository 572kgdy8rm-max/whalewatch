from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import httpx
import math
import yfinance as yf

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# WILSON SCORE (Quant Genius Rating)
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
# CALCULATE SIGNAL STATS ON DEMAND (NO HARDCODE)
# ============================================================
async def calculate_ticker_stats(ticker: str):
    """Fetch live data from Yahoo and calculate stats in real-time"""
    try:
        # Fetch stock data
        stock = yf.Ticker(ticker)
        hist = stock.history(period="2y")
        
        if hist.empty:
            return None
        
        # Fetch S&P 500 for comparison
        spy = yf.Ticker("SPY")
        spy_hist = spy.history(period="2y")
        
        # Align dates
        common_dates = hist.index.intersection(spy_hist.index)
        if len(common_dates) < 5:
            return None
        
        stock_prices = hist.loc[common_dates, 'Close']
        spy_prices = spy_hist.loc[common_dates, 'Close']
        
        # Calculate returns
        stock_returns = stock_prices.pct_change().dropna()
        spy_returns = spy_prices.pct_change().dropna()
        
        # Align returns
        min_len = min(len(stock_returns), len(spy_returns))
        stock_returns = stock_returns.iloc[-min_len:]
        spy_returns = spy_returns.iloc[-min_len:]
        
        # Calculate excess returns
        excess_returns = stock_returns - spy_returns
        wins = (excess_returns > 0).sum()
        total = len(excess_returns)
        win_rate = (wins / total) * 100 if total > 0 else 0
        avg_excess = excess_returns.mean() * 100 if total > 0 else 0
        max_drawdown = stock_returns.min() * 100 if len(stock_returns) > 0 else 0
        current_price = stock_prices.iloc[-1]
        
        # Get Genius Rating
        adjusted = wilson_lower_bound(win_rate, total)
        
        if adjusted >= 75:
            rating = "🔥 TOP"
            position_pct = 5
        elif adjusted >= 65:
            rating = "✅ GOOD"
            position_pct = 2.5
        elif adjusted >= 55:
            rating = "⚠️ SMALL"
            position_pct = 1
        else:
            rating = "❌ AVOID"
            position_pct = 0
        
        return {
            "ticker": ticker.upper(),
            "genius_rating": rating,
            "position_pct": position_pct,
            "win_rate": round(win_rate, 1),
            "total_trades": total,
            "excess_vs_spy": round(avg_excess, 1),
            "max_drawdown": round(max_drawdown, 1),
            "current_price": round(current_price, 2),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Error calculating {ticker}: {e}")
        return None

# ============================================================
# ENDPOINTS
# ============================================================
@app.get("/")
def root():
    return {"message": "WhaleWatch API Live", "time": datetime.now().isoformat()}

@app.get("/v1/signal/{ticker}")
async def get_signal(ticker: str):
    """Calculate Genius Rating on demand — zero hardcoded data"""
    result = await calculate_ticker_stats(ticker)
    if not result:
        raise HTTPException(status_code=404, detail=f"No data found for {ticker}")
    return result

@app.get("/v1/live/{ticker}")
async def get_live_price(ticker: str):
    """Get real-time price from Yahoo Finance"""
    try:
        stock = yf.Ticker(ticker.upper())
        ticker_info = stock.fast_info
        return {
            "ticker": ticker.upper(),
            "price": round(ticker_info.last_price, 2) if ticker_info.last_price else 0,
            "change": round(ticker_info.last_price - ticker_info.previous_close, 2) if ticker_info.last_price else 0,
            "change_percent": round(((ticker_info.last_price - ticker_info.previous_close) / ticker_info.previous_close) * 100, 2) if ticker_info.previous_close else 0,
            "source": "Yahoo Finance",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Price fetch failed: {str(e)}") 
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import yfinance as yf
import math

app = FastAPI()

# Allow your frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict later if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# WILSON SCORE (Quant Genius Rating Engine)
# ============================================================
def wilson_lower_bound(win_rate, total_trades):
    if total_trades == 0:
        return 0
    p = win_rate / 100
    n = total_trades
    z = 1.96  # 95% confidence
    lower = (p + (z*z)/(2*n) - z * math.sqrt((p*(1-p) + (z*z)/(4*n))/n)) / (1 + (z*z)/n)
    return max(0, lower) * 100

# ============================================================
# CALCULATE STATS FROM YAHOO FINANCE
# ============================================================
def calculate_stats(ticker):
    """Calculate Wilson score, excess returns, and drawdown from Yahoo data."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="2y")
        if hist.empty or len(hist) < 20:
            return None

        spy = yf.Ticker("SPY")
        spy_hist = spy.history(period="2y")

        common_dates = hist.index.intersection(spy_hist.index)
        if len(common_dates) < 20:
            return None

        stock_prices = hist.loc[common_dates, 'Close']
        spy_prices = spy_hist.loc[common_dates, 'Close']

        stock_returns = stock_prices.pct_change().dropna()
        spy_returns = spy_prices.pct_change().dropna()

        min_len = min(len(stock_returns), len(spy_returns))
        stock_returns = stock_returns.iloc[-min_len:]
        spy_returns = spy_returns.iloc[-min_len:]

        excess_returns = stock_returns - spy_returns
        wins = (excess_returns > 0).sum()
        total = len(excess_returns)
        win_rate = (wins / total) * 100 if total > 0 else 0
        avg_excess = excess_returns.mean() * 100 if total > 0 else 0
        max_drawdown = stock_returns.min() * 100 if len(stock_returns) > 0 else 0
        current_price = stock_prices.iloc[-1]

        wilson = wilson_lower_bound(win_rate, total)

        if wilson >= 75:
            rating = "🔥 TOP"
            position = 5
        elif wilson >= 65:
            rating = "✅ GOOD"
            position = 2.5
        elif wilson >= 55:
            rating = "⚠️ SMALL"
            position = 1
        else:
            rating = "❌ AVOID"
            position = 0

        return {
            "ticker": ticker.upper(),
            "genius_rating": rating,
            "position_pct": position,
            "win_rate": round(win_rate, 1),
            "total_trades": total,
            "excess_vs_spy": round(avg_excess, 1),
            "max_drawdown": round(max_drawdown, 1),
            "current_price": round(current_price, 2),
            "wilson_score": round(wilson, 1),
        }
    except Exception as e:
        print(f"Error calculating {ticker}: {e}")
        return None

# ============================================================
# API ENDPOINTS
# ============================================================
@app.get("/")
def root():
    return {"message": "WhaleWatch API Live", "time": datetime.now().isoformat()}

@app.get("/v1/signal/{ticker}")
async def get_signal(ticker):
    """Calculate Genius Rating for a specific ticker."""
    ticker = ticker.upper()
    result = calculate_stats(ticker)
    if not result:
        raise HTTPException(status_code=404, detail=f"No data for {ticker}")
    return {**result, "timestamp": datetime.now().isoformat()}

@app.get("/v1/top10")
async def get_top10():
    """Generate a dynamic Top 10 list based on the Wilson score."""
    DEFAULT_TICKERS = ["NVDA", "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "LMT", "AVGO", "TSM"]
    results = []
    for ticker in DEFAULT_TICKERS:
        stats = calculate_stats(ticker)
        if stats:
            results.append(stats)

    # Sort by the calculated Wilson score
    results.sort(key=lambda x: x.get('wilson_score', 0), reverse=True)
    top10 = results[:10]

    return {
        "top_10": top10,
        "last_updated": datetime.now().isoformat(),
        "total_tickers": len(results),
        "source": "live_calculation",
    }
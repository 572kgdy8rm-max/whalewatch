import yfinance as yf
import json
import requests
from datetime import datetime, timedelta
import time

# ============================================================
# CONFIGURATION
# ============================================================
TICKERS = [
    "NVDA", "LMT", "TSM", "BABA", "NU", "AVGO", "MSFT", "AAPL", 
    "GOOGL", "AMZN", "META", "TSLA", "PLTR", "DELL", "ORCL"
]

# ============================================================
# WILSON SCORE (same as backend)
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
# CALCULATE SIGNAL STATS FOR A TICKER
# ============================================================
def calculate_ticker_stats(ticker):
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
        
        # Genius Rating
        adjusted = wilson_lower_bound(win_rate, total)
        
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
            "total_trades": total,
            "excess_vs_spy": round(avg_excess, 1),
            "max_drawdown": round(max_drawdown, 1),
            "current_price": round(current_price, 2),
            "wilson_score": round(adjusted, 1)
        }
    except Exception as e:
        print(f"Error with {ticker}: {e}")
        return None

# ============================================================
# SCRAPE SEC FORM 4 (Insider Trades)
# ============================================================
def get_insider_trades(ticker, days_back=30):
    """Fetch recent insider trades from SEC EDGAR"""
    try:
        # Using free SEC EDGAR API via company_tickers.json
        url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={ticker}&type=4&dateb=&owner=include&count=40&output=atom"
        headers = {'User-Agent': 'WhaleWatch/1.0 (your@email.com)'}
        
        response = requests.get(url, headers=headers)
        # This returns XML — parsing would need more code
        # For now, return placeholder
        return {"ticker": ticker, "recent_trades": 0, "insider_buys": 0, "source": "SEC EDGAR"}
    except:
        return {"ticker": ticker, "recent_trades": 0, "insider_buys": 0, "error": True}

# ============================================================
# GENERATE TOP 10 LIST
# ============================================================
def generate_top_10(all_stats):
    """Rank by Genius Rating then excess returns"""
    valid = [s for s in all_stats if s and s.get('win_rate', 0) > 0]
    
    # Sort by: Genius Rating weight, then excess returns
    def score(s):
        rating_weight = {
            "🔥 TOP": 100,
            "✅ GOOD": 60,
            "⚠️ SMALL": 30,
            "❌ AVOID": 0
        }.get(s.get('genius_rating', '❌ AVOID'), 0)
        return rating_weight + s.get('excess_vs_spy', 0)
    
    valid.sort(key=score, reverse=True)
    return valid[:10]

# ============================================================
# MAIN
# ============================================================
def main():
    print(f"🔄 WhaleWatch Supercomputer Update - {datetime.now()}")
    print(f"Processing {len(TICKERS)} tickers...")
    
    all_stats = []
    for ticker in TICKERS:
        print(f"  Calculating {ticker}...")
        stats = calculate_ticker_stats(ticker)
        if stats:
            all_stats.append(stats)
        time.sleep(0.5)  # Rate limit
    
    # Generate Top 10
    top_10 = generate_top_10(all_stats)
    
    # Save to JSON file
    output = {
        "last_updated": datetime.now().isoformat(),
        "total_tickers": len(all_stats),
        "all_signals": all_stats,
        "top_10": top_10,
        "insider_trades": []  # Add when SEC scraping is fully implemented
    }
    
    with open('data/signals.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Complete! Top 10:")
    for i, ticker in enumerate(top_10[:5], 1):
        print(f"  {i}. {ticker['ticker']} - {ticker['genius_rating']} ({ticker['excess_vs_spy']:+}% vs SPY)")
    
    return output

if __name__ == "__main__":
    main()
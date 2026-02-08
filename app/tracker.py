import yfinance as yf

# Symbols you follow: Reliance, Nifty Bees (India), S&P 500 Index ETF, Capital Power (Canada)
watch_list = ["RELIANCE.NS", "NIFTYBEES.NS", "VFV.TO", "CPX.TO"]

def get_market_summary():
    print("--- Portfolio Performance Update ---")
    for ticker_symbol in watch_list:
        ticker = yf.Ticker(ticker_symbol)
        data = ticker.history(period="1d")
        
        if not data.empty:
            current_price = data['Close'].iloc[-1]
            # Fetching the previous close for percentage calculation
            prev_close = ticker.info.get('previousClose', current_price)
            change = ((current_price - prev_close) / prev_close) * 100
            print(f"{ticker_symbol}: {current_price:.2f} ({change:+.2f}%)")
        else:
            print(f"Data not found for {ticker_symbol}")

if __name__ == "__main__":
    get_market_summary()
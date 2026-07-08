import logging
from flask import Flask, jsonify
import yfinance as yf

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

app = Flask(__name__)

WATCH_LIST = ["RELIANCE.NS", "NIFTYBEES.NS", "VFV.TO", "CPX.TO"]


def fetch_ticker(symbol):
    log.info("Fetching %s", symbol)
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="1d")
    if data.empty:
        raise ValueError(f"No data returned for {symbol}")
    current_price = float(data["Close"].iloc[-1])
    prev_close = ticker.info.get("previousClose", current_price)
    change_pct = ((current_price - prev_close) / prev_close) * 100
    log.info("OK %s price=%.2f change=%.2f%%", symbol, current_price, change_pct)
    return {"ticker": symbol, "price": round(current_price, 2), "change_pct": round(change_pct, 2)}


@app.get("/")
def market_summary():
    results = []
    for symbol in WATCH_LIST:
        try:
            results.append(fetch_ticker(symbol))
        except Exception as exc:
            log.error("Failed %s: %s", symbol, exc)
            results.append({"ticker": symbol, "error": str(exc)})
    return jsonify(results)


@app.get("/health")
def health():
    return "", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

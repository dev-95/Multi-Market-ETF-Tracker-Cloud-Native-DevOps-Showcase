import logging
import time
from flask import Flask, jsonify, Response
import yfinance as yf
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

app = Flask(__name__)

WATCH_LIST = ["RELIANCE.NS", "NIFTYBEES.NS", "VFV.TO", "CPX.TO"]

REQUEST_COUNT = Counter("etf_requests_total", "Total requests to /")
REQUEST_LATENCY = Histogram("etf_request_duration_seconds", "Latency of / in seconds")
TICKER_STATUS = Gauge("etf_ticker_fetch_success", "1 if last fetch succeeded, 0 if failed", ["ticker"])


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
    REQUEST_COUNT.inc()
    start = time.time()
    results = []
    for symbol in WATCH_LIST:
        try:
            results.append(fetch_ticker(symbol))
            TICKER_STATUS.labels(ticker=symbol).set(1)
        except Exception as exc:
            log.error("Failed %s: %s", symbol, exc)
            results.append({"ticker": symbol, "error": str(exc)})
            TICKER_STATUS.labels(ticker=symbol).set(0)
    REQUEST_LATENCY.observe(time.time() - start)
    return jsonify(results)


@app.get("/health")
def health():
    return "", 200


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

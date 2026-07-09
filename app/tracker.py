import logging
import time
from datetime import datetime
from flask import Flask, jsonify, Response, render_template
import yfinance as yf
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

app = Flask(__name__)

WATCH_LIST = ["^NSEI", "^GSPTSE", "^GSPC", "^N225", "^KS11", "^HSI", "^STOXX50E"]

REQUEST_COUNT = Counter("etf_requests_total", "Total requests to /")
REQUEST_LATENCY = Histogram("etf_request_duration_seconds", "Latency of / in seconds")
TICKER_STATUS = Gauge("etf_ticker_fetch_success", "1 if last fetch succeeded, 0 if failed", ["ticker"])


def fetch_ticker(symbol):
    log.info("Fetching %s", symbol)
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="5d")
    closes = data["Close"].dropna()
    if len(closes) < 2:
        raise ValueError(f"Insufficient history for {symbol}")
    current_price = float(closes.iloc[-1])
    prev_close = float(closes.iloc[-2])
    change_pct = ((current_price - prev_close) / prev_close) * 100
    last_ts = closes.index[-1]
    market_status = "open" if last_ts.date() >= datetime.now(last_ts.tzinfo).date() else "closed"
    log.info("OK %s price=%.2f change=%.2f%% status=%s", symbol, current_price, change_pct, market_status)
    return {
        "ticker": symbol,
        "price": round(current_price, 2),
        "change_pct": round(change_pct, 2),
        "market_status": market_status,
    }


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


@app.get("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.get("/health")
def health():
    return "", 200


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

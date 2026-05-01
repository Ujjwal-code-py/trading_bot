# 🤖 Binance Futures Testnet Trading Bot

A Python CLI application to place **Market** and **Limit** orders on the [Binance Futures Testnet](https://testnet.binancefuture.com) (USDT-M Perpetual Futures).

---

## 📁 Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py          # Package init
│   ├── client.py            # Binance REST API client (auth + HTTP)
│   ├── orders.py            # Order placement logic (market & limit)
│   ├── validators.py        # Input validation
│   └── logging_config.py    # File + console logging setup
├── logs/                    # Auto-created log files
├── cli.py                   # CLI entry point (argparse)
├── .env.example             # Environment variable template
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/trading_bot.git
cd trading_bot
```

### 2. Create a virtual environment

```bash
python -m venv venv

# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Get Binance Testnet API credentials

1. Go to [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Log in (you can use GitHub to sign in)
3. Click **API Management** in the top menu
4. Generate a new API key — copy the **Key** and **Secret**

### 5. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```env
BINANCE_API_KEY=your_actual_api_key
BINANCE_API_SECRET=your_actual_api_secret
```

> ⚠️ Never commit `.env` to Git. It is already listed in `.gitignore`.

---

## 🚀 How to Run

### Basic syntax

```bash
python cli.py --symbol <SYMBOL> --side <BUY|SELL> --type <MARKET|LIMIT> --quantity <QTY> [--price <PRICE>]
```

### Examples

#### Place a MARKET BUY order
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

#### Place a MARKET SELL order
```bash
python cli.py --symbol BTCUSDT --side SELL --type MARKET --quantity 0.01
```

#### Place a LIMIT BUY order
```bash
python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.01 --price 50000
```

#### Place a LIMIT SELL order
```bash
python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.1 --price 3500
```

#### LIMIT order with custom time-in-force
```bash
python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.01 --price 50000 --tif IOC
```

### CLI Arguments

| Argument | Short | Required | Description |
|---|---|---|---|
| `--symbol` | `-s` | ✅ | Trading pair (e.g. `BTCUSDT`) |
| `--side` | | ✅ | `BUY` or `SELL` |
| `--type` | `-t` | ✅ | `MARKET` or `LIMIT` |
| `--quantity` | `-q` | ✅ | Order quantity (e.g. `0.01`) |
| `--price` | `-p` | For LIMIT | Limit price |
| `--tif` | | ❌ | Time-in-force: `GTC` (default), `IOC`, `FOK` |

---

## 📄 Sample Output

```
╔══════════════════════════════════════════════════════╗
║        🤖  Binance Futures Testnet Trading Bot       ║
║              USDT-M Perpetual Futures                ║
╚══════════════════════════════════════════════════════╝

📋 Order Summary
────────────────────────────────────────
   Symbol   : BTCUSDT
   Side     : BUY
   Type     : MARKET
   Quantity : 0.01
────────────────────────────────────────

📤 Sending MARKET BUY order — 0.01 BTCUSDT ...

=======================================================
          ✅  ORDER PLACED SUCCESSFULLY
=======================================================
  Order ID     : 3799833890
  Symbol       : BTCUSDT
  Side         : BUY
  Type         : MARKET
  Status       : FILLED
  Quantity     : 0.01
  Executed Qty : 0.01
  Avg Price    : 63450.10
  Price        : 0
  Time in Force: GTC
  Created At   : 1714567890123
=======================================================
```

---

## 📝 Logging

Logs are written to `logs/trading_bot_YYYYMMDD.log`.

Each log entry captures:
- API request parameters
- Full API response
- Validation errors
- Network/API exceptions

Log format:
```
2024-05-01 21:30:00 | INFO     | trading_bot.client | BinanceClient initialised — base URL: https://testnet.binancefuture.com
2024-05-01 21:30:00 | INFO     | trading_bot.orders | Initiating MARKET order: symbol=BTCUSDT side=BUY qty=0.01
2024-05-01 21:30:01 | DEBUG    | trading_bot.client | POST https://testnet.binancefuture.com/fapi/v1/order | params: {...}
2024-05-01 21:30:01 | DEBUG    | trading_bot.client | Response 200: {...}
2024-05-01 21:30:01 | INFO     | trading_bot.client | Order placed successfully — orderId=3799833890 status=FILLED
```

---

## 🧠 Assumptions

- All orders are placed on **USDT-M Perpetual Futures** (not COIN-M or Spot).
- The testnet base URL used is `https://testnet.binancefuture.com`.
- Credentials are stored in a `.env` file (not hardcoded).
- For LIMIT orders, the default time-in-force is `GTC` (Good Till Cancelled).
- Quantity and price precision must comply with Binance symbol filters — the testnet is more lenient, but if an error occurs, adjust the precision.

---

## 🛠️ Tech Stack

| Library | Purpose |
|---|---|
| `requests` | HTTP calls to Binance REST API |
| `python-dotenv` | Load credentials from `.env` |
| `argparse` | CLI argument parsing (stdlib) |
| `logging` | Structured log output (stdlib) |
| `hmac` / `hashlib` | HMAC-SHA256 API signature (stdlib) |

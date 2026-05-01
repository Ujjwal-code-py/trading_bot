#!/usr/bin/env python3
"""
Trading Bot CLI — Binance Futures Testnet
==========================================
Usage examples:
  python cli.py --symbol BTCUSDT --side BUY  --type MARKET --quantity 0.01
  python cli.py --symbol BTCUSDT --side SELL --type LIMIT  --quantity 0.01 --price 50000
  python cli.py --symbol ETHUSDT --side BUY  --type LIMIT  --quantity 0.1  --price 2000
"""

import argparse
import os
import sys

# Force UTF-8 output on Windows (avoids UnicodeEncodeError with box-drawing chars)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8")

from dotenv import load_dotenv

from bot.client import BinanceClient
from bot.logging_config import setup_logger
from bot.orders import place_limit_order, place_market_order, place_stop_limit_order
from bot.validators import ValidationError, validate_all

load_dotenv()
logger = setup_logger("trading_bot.cli")

BANNER = r"""
╔══════════════════════════════════════════════════════╗
║            Binance Futures Testnet Trading Bot       ║
║              USDT-M Perpetual Futures                ║
╚══════════════════════════════════════════════════════╝
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Place Market and Limit orders on Binance Futures Testnet.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--symbol", "-s",
        required=True,
        help="Trading pair symbol, e.g. BTCUSDT",
    )
    parser.add_argument(
        "--side",
        required=True,
        choices=["BUY", "SELL", "buy", "sell"],
        help="Order side: BUY or SELL",
    )
    parser.add_argument(
        "--type", "-t",
        dest="order_type",
        required=True,
        choices=["MARKET", "LIMIT", "STOP_LIMIT", "market", "limit", "stop_limit"],
        help="Order type: MARKET, LIMIT, or STOP_LIMIT",
    )
    parser.add_argument(
        "--quantity", "-q",
        required=True,
        help="Quantity to trade (e.g. 0.01)",
    )
    parser.add_argument(
        "--price", "-p",
        required=False,
        default=None,
        help="Limit price (required for LIMIT and STOP_LIMIT orders)",
    )
    parser.add_argument(
        "--stop-price",
        dest="stop_price",
        required=False,
        default=None,
        help="Stop trigger price (required for STOP_LIMIT orders)",
    )
    parser.add_argument(
        "--tif",
        default="GTC",
        choices=["GTC", "IOC", "FOK"],
        help="Time-in-force for LIMIT/STOP_LIMIT orders (default: GTC)",
    )
    return parser


def load_credentials() -> tuple[str, str]:
    """Load API credentials from environment variables."""
    api_key = os.getenv("BINANCE_API_KEY", "").strip()
    api_secret = os.getenv("BINANCE_API_SECRET", "").strip()

    if not api_key or not api_secret:
        logger.error("Missing API credentials. Set BINANCE_API_KEY and BINANCE_API_SECRET in .env")
        print(
            "\nError: API credentials not found.\n"
            "   Create a .env file with:\n"
            "     BINANCE_API_KEY=your_key_here\n"
            "     BINANCE_API_SECRET=your_secret_here\n"
        )
        sys.exit(1)

    return api_key, api_secret


def print_order_summary(params: dict) -> None:
    """Print a summary of the order about to be placed."""
    print("\nOrder Summary")
    print("─" * 40)
    print(f"   Symbol   : {params['symbol']}")
    print(f"   Side     : {params['side']}")
    print(f"   Type     : {params['order_type']}")
    print(f"   Quantity : {params['quantity']}")
    if params.get("price"):
        print(f"   Price    : {params['price']}")
    if params.get("stop_price"):
        print(f"   Stop     : {params['stop_price']}")
    print("─" * 40)


def main() -> None:
    print(BANNER)
    parser = build_parser()
    args = parser.parse_args()

    # ── 1. Validate inputs ─────────────────────────────────────────────
    try:
        params = validate_all(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )
    except ValidationError as exc:
        logger.warning("Input validation failed: %s", exc)
        print(f"\nValidation error: {exc}")
        sys.exit(1)

    logger.info("Validated input: %s", params)

    # ── 2. Load credentials & create client ────────────────────────────
    api_key, api_secret = load_credentials()
    client = BinanceClient(api_key=api_key, api_secret=api_secret)

    print_order_summary(params)

    # ── 3. Place order ─────────────────────────────────────────────────
    if params["order_type"] == "MARKET":
        result = place_market_order(
            client=client,
            symbol=params["symbol"],
            side=params["side"],
            quantity=params["quantity"],
        )
    elif params["order_type"] == "LIMIT":
        result = place_limit_order(
            client=client,
            symbol=params["symbol"],
            side=params["side"],
            quantity=params["quantity"],
            price=params["price"],
            time_in_force=args.tif,
        )
    else:  # STOP_LIMIT
        result = place_stop_limit_order(
            client=client,
            symbol=params["symbol"],
            side=params["side"],
            quantity=params["quantity"],
            price=params["price"],
            stop_price=params["stop_price"],
            time_in_force=args.tif,
        )

    if result is None:
        sys.exit(1)

    logger.info("CLI session complete.")


if __name__ == "__main__":
    main()

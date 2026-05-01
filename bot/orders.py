from datetime import datetime
from typing import Optional, Dict, Any

from bot.client import BinanceClient, BinanceClientError, NetworkError
from bot.logging_config import setup_logger

logger = setup_logger("trading_bot.orders")


def _format_order_response(response: Dict[str, Any]) -> str:
    """Format order response into a human-readable summary."""
    raw_ts = response.get('time') or response.get('updateTime')
    if raw_ts:
        created = datetime.fromtimestamp(raw_ts / 1000).strftime('%Y-%m-%d %H:%M:%S')
    else:
        created = 'N/A'

    lines = [
        "",
        "=" * 55,
        "              ORDER PLACED SUCCESSFULLY",
        "=" * 55,
        f"  Order ID     : {response.get('orderId', 'N/A')}",
        f"  Symbol       : {response.get('symbol', 'N/A')}",
        f"  Side         : {response.get('side', 'N/A')}",
        f"  Type         : {response.get('type', 'N/A')}",
        f"  Status       : {response.get('status', 'N/A')}",
        f"  Quantity     : {response.get('origQty', 'N/A')}",
        f"  Executed Qty : {response.get('executedQty', 'N/A')}",
        f"  Avg Price    : {response.get('avgPrice', 'N/A')}",
        f"  Price        : {response.get('price', 'N/A')}",
        f"  Time in Force: {response.get('timeInForce', 'N/A')}",
        f"  Created At   : {created}",
        "=" * 55,
    ]
    return "\n".join(lines)


def place_market_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    quantity: float,
) -> Optional[Dict[str, Any]]:
    """
    Place a MARKET order.

    Args:
        client:   Initialised BinanceClient instance.
        symbol:   Trading pair, e.g. 'BTCUSDT'.
        side:     'BUY' or 'SELL'.
        quantity: Amount to trade.

    Returns:
        API response dict on success, None on failure.
    """
    print(f"\nSending MARKET {side} order — {quantity} {symbol} ...")
    logger.info("Initiating MARKET order: symbol=%s side=%s qty=%s", symbol, side, quantity)

    try:
        response = client.place_order(
            symbol=symbol,
            side=side,
            order_type="MARKET",
            quantity=quantity,
        )
        print(_format_order_response(response))
        return response

    except BinanceClientError as exc:
        logger.error("Binance error placing MARKET order: %s", exc)
        print(f"\nError: Order failed — Binance API error: {exc}")
        return None

    except NetworkError as exc:
        logger.error("Network error placing MARKET order: %s", exc)
        print(f"\nError: Order failed — Network error: {exc}")
        return None

    except Exception as exc:
        logger.exception("Unexpected error placing MARKET order: %s", exc)
        print(f"\nError: Order failed — Unexpected error: {exc}")
        return None


def place_limit_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    time_in_force: str = "GTC",
) -> Optional[Dict[str, Any]]:
    """
    Place a LIMIT order.

    Args:
        client:        Initialised BinanceClient instance.
        symbol:        Trading pair, e.g. 'BTCUSDT'.
        side:          'BUY' or 'SELL'.
        quantity:      Amount to trade.
        price:         Limit price.
        time_in_force: 'GTC' (default), 'IOC', or 'FOK'.

    Returns:
        API response dict on success, None on failure.
    """
    print(f"\nSending LIMIT {side} order — {quantity} {symbol} @ {price} ...")
    logger.info(
        "Initiating LIMIT order: symbol=%s side=%s qty=%s price=%s tif=%s",
        symbol, side, quantity, price, time_in_force,
    )

    try:
        response = client.place_order(
            symbol=symbol,
            side=side,
            order_type="LIMIT",
            quantity=quantity,
            price=price,
            time_in_force=time_in_force,
        )
        print(_format_order_response(response))
        return response

    except BinanceClientError as exc:
        logger.error("Binance error placing LIMIT order: %s", exc)
        print(f"\nError: Order failed — Binance API error: {exc}")
        return None

    except NetworkError as exc:
        logger.error("Network error placing LIMIT order: %s", exc)
        print(f"\nError: Order failed — Network error: {exc}")
        return None

    except Exception as exc:
        logger.exception("Unexpected error placing LIMIT order: %s", exc)
        print(f"\nError: Order failed — Unexpected error: {exc}")
        return None


def place_stop_limit_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    stop_price: float,
    time_in_force: str = "GTC",
) -> Optional[Dict[str, Any]]:
    """
    Place a STOP-LIMIT order (triggers at stop_price, executes at price).

    Args:
        client:        Initialised BinanceClient instance.
        symbol:        Trading pair, e.g. 'BTCUSDT'.
        side:          'BUY' or 'SELL'.
        quantity:      Amount to trade.
        price:         Limit price (execution price after trigger).
        stop_price:    Trigger price.
        time_in_force: 'GTC' (default), 'IOC', or 'FOK'.

    Returns:
        API response dict on success, None on failure.
    """
    print(f"\nSending STOP-LIMIT {side} order — {quantity} {symbol} | stop @ {stop_price} | limit @ {price} ...")
    logger.info(
        "Initiating STOP_LIMIT order: symbol=%s side=%s qty=%s stop_price=%s price=%s tif=%s",
        symbol, side, quantity, stop_price, price, time_in_force,
    )

    try:
        response = client.place_order(
            symbol=symbol,
            side=side,
            order_type="STOP_LIMIT",
            quantity=quantity,
            price=price,
            stop_price=stop_price,
            time_in_force=time_in_force,
        )
        print(_format_order_response(response))
        return response

    except BinanceClientError as exc:
        logger.error("Binance error placing STOP_LIMIT order: %s", exc)
        print(f"\nError: Order failed — Binance API error: {exc}")
        return None

    except NetworkError as exc:
        logger.error("Network error placing STOP_LIMIT order: %s", exc)
        print(f"\nError: Order failed — Network error: {exc}")
        return None

    except Exception as exc:
        logger.exception("Unexpected error placing STOP_LIMIT order: %s", exc)
        print(f"\nError: Order failed — Unexpected error: {exc}")
        return None

from typing import Optional


VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_LIMIT"}


class ValidationError(Exception):
    """Raised when user input fails validation."""
    pass


def validate_symbol(symbol: str) -> str:
    """Validate and normalize trading symbol."""
    symbol = symbol.strip().upper()
    if not symbol or not symbol.isalnum():
        raise ValidationError(
            f"Invalid symbol '{symbol}'. Must be alphanumeric with no spaces or special characters (e.g., BTCUSDT)."
        )
    return symbol


def validate_side(side: str) -> str:
    """Validate order side (BUY or SELL)."""
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValidationError(
            f"Invalid side '{side}'. Must be one of: {', '.join(VALID_SIDES)}."
        )
    return side


def validate_order_type(order_type: str) -> str:
    """Validate order type (MARKET or LIMIT)."""
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type '{order_type}'. Must be one of: {', '.join(VALID_ORDER_TYPES)}."
        )
    return order_type


def validate_quantity(quantity: str) -> float:
    """Validate order quantity."""
    try:
        qty = float(quantity)
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid quantity '{quantity}'. Must be a positive number.")
    if qty <= 0:
        raise ValidationError(f"Quantity must be greater than 0, got {qty}.")
    return qty


def validate_price(price: Optional[str], order_type: str) -> Optional[float]:
    """Validate price — required for LIMIT and STOP_LIMIT orders, ignored for MARKET."""
    if order_type in ("LIMIT", "STOP_LIMIT"):
        if price is None:
            raise ValidationError(f"Price is required for {order_type} orders.")
        try:
            p = float(price)
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid price '{price}'. Must be a positive number.")
        if p <= 0:
            raise ValidationError(f"Price must be greater than 0, got {p}.")
        return p
    return None  # Not needed for MARKET orders


def validate_stop_price(stop_price: Optional[str], order_type: str) -> Optional[float]:
    """Validate stop price — required only for STOP_LIMIT orders."""
    if order_type == "STOP_LIMIT":
        if stop_price is None:
            raise ValidationError("Stop price is required for STOP_LIMIT orders.")
        try:
            sp = float(stop_price)
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid stop price '{stop_price}'. Must be a positive number.")
        if sp <= 0:
            raise ValidationError(f"Stop price must be greater than 0, got {sp}.")
        return sp
    return None


def validate_all(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: Optional[str] = None,
    stop_price: Optional[str] = None,
) -> dict:
    """
    Run all validations and return a clean, typed parameter dict.
    Raises ValidationError on any invalid input.
    """
    validated_type = validate_order_type(order_type)
    return {
        "symbol": validate_symbol(symbol),
        "side": validate_side(side),
        "order_type": validated_type,
        "quantity": validate_quantity(quantity),
        "price": validate_price(price, validated_type),
        "stop_price": validate_stop_price(stop_price, validated_type),
    }

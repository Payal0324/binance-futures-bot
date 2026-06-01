from typing import Optional

class ValidationError(Exception):
    """Exception raised for invalid order inputs."""
    pass


def validate_order_params(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
    stop_price: Optional[float] = None
) -> None:
    """
    Validates the order parameters for Binance Futures.
    
    Args:
        symbol: The trading symbol (e.g., BTCUSDT)
        side: BUY or SELL
        order_type: MARKET, LIMIT, or STOP_LIMIT
        quantity: The quantity to trade
        price: The execution limit price (required for LIMIT and STOP_LIMIT)
        stop_price: The trigger price (required for STOP_LIMIT)
        
    Raises:
        ValidationError: If any validation rule is violated.
    """
    if not symbol or not isinstance(symbol, str):
        raise ValidationError("Symbol is required and must be a string (e.g., BTCUSDT).")
        
    # Check Side
    normalized_side = side.upper() if isinstance(side, str) else ""
    if normalized_side not in ("BUY", "SELL"):
        raise ValidationError(f"Invalid side '{side}'. Side must be BUY or SELL.")

    # Check Order Type
    normalized_type = order_type.upper() if isinstance(order_type, str) else ""
    if normalized_type not in ("MARKET", "LIMIT", "STOP_LIMIT"):
        raise ValidationError(f"Invalid order type '{order_type}'. Supported types: MARKET, LIMIT, STOP_LIMIT.")

    # Check Quantity
    try:
        qty_val = float(quantity)
    except (ValueError, TypeError):
        raise ValidationError(f"Quantity '{quantity}' must be a numeric value.")
        
    if qty_val <= 0:
        raise ValidationError(f"Quantity {qty_val} must be greater than zero.")

    # Validate price for LIMIT and STOP_LIMIT orders
    if normalized_type in ("LIMIT", "STOP_LIMIT"):
        if price is None:
            raise ValidationError(f"Price is required for {normalized_type} orders.")
        try:
            price_val = float(price)
        except (ValueError, TypeError):
            raise ValidationError(f"Price '{price}' must be a numeric value.")
            
        if price_val <= 0:
            raise ValidationError(f"Price {price_val} must be greater than zero.")

    # Validate stopPrice for STOP_LIMIT orders
    if normalized_type == "STOP_LIMIT":
        if stop_price is None:
            raise ValidationError("Stop price is required for STOP_LIMIT orders.")
        try:
            stop_price_val = float(stop_price)
        except (ValueError, TypeError):
            raise ValidationError(f"Stop price '{stop_price}' must be a numeric value.")
            
        if stop_price_val <= 0:
            raise ValidationError(f"Stop price {stop_price_val} must be greater than zero.")

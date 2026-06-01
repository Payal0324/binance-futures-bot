import logging
from typing import Dict, Any, Optional
from bot.client import BinanceClient
from bot.validators import validate_order_params

logger = logging.getLogger("binance_bot.orders")

class OrderManager:
    """
    Manages order placement logic. Coordinates validation and API calls.
    """
    def __init__(self, client: BinanceClient):
        self.client = client

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Validates parameters and places an order on Binance Futures Testnet.
        
        Args:
            symbol: Trading symbol (e.g. BTCUSDT)
            side: BUY or SELL
            order_type: MARKET, LIMIT, or STOP_LIMIT
            quantity: Quantity to buy or sell
            price: Price for LIMIT/STOP_LIMIT orders
            stop_price: Trigger price for STOP_LIMIT orders
            
        Returns:
            Dict[str, Any]: The response dictionary from the Binance API.
        """
        # 1. Normalize values
        symbol = symbol.upper().strip()
        side = side.upper().strip()
        order_type = order_type.upper().strip()

        # 2. Perform validations
        logger.info(
            f"Validating order parameters: Symbol={symbol}, Side={side}, "
            f"Type={order_type}, Quantity={quantity}, Price={price}, StopPrice={stop_price}"
        )
        validate_order_params(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price
        )

        # 3. Build request payload
        # Map CLI order_type 'STOP_LIMIT' to Binance's API 'STOP'
        api_type = "STOP" if order_type == "STOP_LIMIT" else order_type

        params: Dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": api_type,
            "quantity": str(quantity)
        }

        if order_type == "LIMIT":
            params["price"] = str(price)
            params["timeInForce"] = "GTC"  # Good 'Til Cancelled (default standard)
        elif order_type == "STOP_LIMIT":
            params["price"] = str(price)
            params["stopPrice"] = str(stop_price)
            params["timeInForce"] = "GTC"

        # 4. Place order via client
        logger.info(f"Placing {order_type} order for {symbol}...")
        response = self.client.request(
            method="POST",
            endpoint="/fapi/v1/order",
            params=params,
            signed=True
        )
        
        logger.info(f"Order successfully placed. Order ID: {response.get('orderId')}")
        return response

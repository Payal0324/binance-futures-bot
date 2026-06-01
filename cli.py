import os
import sys
import json
import logging
import click
from typing import Tuple, Optional
import requests

from bot import setup_logging, BinanceClient, BinanceAPIError, OrderManager, ValidationError

# Global logger for CLI errors not caught inside manager
logger = logging.getLogger("binance_bot.cli")


def get_api_credentials() -> Tuple[str, str]:
    """Retrieves Binance API credentials from environment variables."""
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    
    if not api_key or not api_secret:
        click.secho("Error: Missing Binance API credentials.", fg="red", err=True)
        click.echo("Please set the following environment variables:", err=True)
        click.echo("  set BINANCE_API_KEY=your_testnet_api_key      (Windows Command Prompt)", err=True)
        click.echo("  $env:BINANCE_API_KEY=\"your_testnet_api_key\"  (Windows PowerShell)", err=True)
        click.echo("  set BINANCE_API_SECRET=your_testnet_api_secret  (Windows Command Prompt)", err=True)
        click.echo("  $env:BINANCE_API_SECRET=\"your_testnet_api_secret\"  (Windows PowerShell)", err=True)
        sys.exit(1)
        
    return api_key, api_secret


@click.command()
@click.option(
    "--symbol",
    required=True,
    help="Trading symbol (e.g., BTCUSDT).",
)
@click.option(
    "--side",
    required=True,
    type=click.Choice(["BUY", "SELL"], case_sensitive=False),
    help="Order side (BUY or SELL).",
)
@click.option(
    "--type",
    "order_type",
    required=True,
    type=click.Choice(["MARKET", "LIMIT", "STOP_LIMIT"], case_sensitive=False),
    help="Order type (MARKET, LIMIT, or STOP_LIMIT).",
)
@click.option(
    "--quantity",
    required=True,
    type=float,
    help="Order quantity (must be > 0).",
)
@click.option(
    "--price",
    type=float,
    help="Limit price. Required for LIMIT and STOP_LIMIT orders.",
)
@click.option(
    "--stop-price",
    type=float,
    help="Trigger price. Required for STOP_LIMIT orders.",
)
def main(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float],
    stop_price: Optional[float],
):
    """
    Binance Futures Testnet CLI Trading Bot.
    Places MARKET, LIMIT, or STOP_LIMIT orders.
    """
    # 1. Initialize logging
    setup_logging("bot.log")
    logger.info("CLI trading bot started.")

    # 2. Get credentials
    api_key, api_secret = get_api_credentials()

    try:
        # 3. Instantiate Client and Order Manager
        click.echo("Connecting to Binance Futures Testnet and syncing time...")
        client = BinanceClient(api_key=api_key, api_secret=api_secret)
        manager = OrderManager(client=client)

        # 4. Place order
        click.echo(f"Submitting {order_type.upper()} {side.upper()} order for {quantity} {symbol.upper()}...")
        response = manager.place_order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
        )

        # 5. Extract output requirements
        order_id = response.get("orderId")
        status = response.get("status")
        executed_qty = response.get("executedQty", "0")
        avg_price = response.get("avgPrice")
        
        # Display Success Message
        click.echo("\n" + "=" * 50)
        click.secho(" ORDER PLACED SUCCESSFULLY ", fg="green", bold=True, bg="black")
        click.echo("=" * 50)
        
        click.echo(f"Order ID:      {order_id}")
        click.echo(f"Status:        {status}")
        click.echo(f"Executed Qty:  {executed_qty}")
        if avg_price is not None and float(avg_price) > 0:
            click.echo(f"Avg Price:     {avg_price}")
        elif response.get("price") is not None and float(response.get("price")) > 0:
            click.echo(f"Limit Price:   {response.get('price')}")
        else:
            click.echo("Avg Price:     N/A (Market price or execution pending)")
            
        click.echo("-" * 50)
        click.echo("Full Binance Response:")
        click.echo(json.dumps(response, indent=2))
        click.echo("=" * 50)

    except ValidationError as e:
        click.secho(f"\nValidation Error: {e}", fg="yellow", bold=True, err=True)
        logger.warning(f"Validation failed: {e}")
        sys.exit(1)
        
    except BinanceAPIError as e:
        click.secho(f"\nBinance API Error: {e.message} (Code: {e.code})", fg="red", bold=True, err=True)
        logger.error(f"Binance API failure: {e}", exc_info=True)
        sys.exit(1)
        
    except requests.RequestException as e:
        click.secho(f"\nNetwork Error: Could not connect to Binance Testnet. Details: {e}", fg="red", bold=True, err=True)
        logger.error(f"Network error: {e}", exc_info=True)
        sys.exit(1)
        
    except Exception as e:
        click.secho(f"\nUnexpected Error: {e}", fg="red", bold=True, err=True)
        logger.error(f"Unexpected application failure: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

import hmac
import hashlib
import time
import urllib.parse
import logging
from typing import Dict, Any, Optional
import requests

# Logger configuration will be set up centrally, but we fetch the logger here
logger = logging.getLogger("binance_bot.client")

class BinanceAPIError(Exception):
    """Exception raised for errors returned by the Binance API."""
    def __init__(self, status_code: int, code: int, message: str):
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(f"Binance API Error {status_code}: [{code}] {message}")


class BinanceClient:
    """
    Binance USDT-M Futures Testnet API Client.
    Handles authentication, signature generation, time synchronization, and HTTP requests.
    """
    BASE_URL = "https://testnet.binancefuture.com"

    def __init__(self, api_key: str, api_secret: str):
        if not api_key or not api_secret:
            raise ValueError("API Key and API Secret must be provided.")
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        self.session.headers.update({
            "X-MBX-APIKEY": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded"
        })
        self.time_offset = 0
        self._sync_time()

    def _sync_time(self) -> None:
        """
        Synchronizes local time with Binance server time.
        Calculates time offset to prevent timestamp errors.
        """
        url = f"{self.BASE_URL}/fapi/v1/time"
        logger.debug(f"Syncing server time. Request: GET {url}")
        try:
            start_time = int(time.time() * 1000)
            response = requests.get(url, timeout=10)
            end_time = int(time.time() * 1000)
            
            # Simple round-trip time approximation
            rtt = (end_time - start_time) // 2
            
            response.raise_for_status()
            server_time = response.json()["serverTime"]
            local_time = start_time + rtt
            
            self.time_offset = server_time - local_time
            logger.info(f"Server time synchronized. Offset: {self.time_offset} ms (RTT: {rtt} ms)")
        except Exception as e:
            logger.warning(f"Failed to synchronize server time: {e}. Using local time (offset = 0).")
            self.time_offset = 0

    def _get_timestamp(self) -> int:
        """Returns the synchronized timestamp in milliseconds."""
        return int(time.time() * 1000) + self.time_offset

    def _sign_query(self, query_string: str) -> str:
        """Generates HMAC-SHA256 signature for the given query string."""
        return hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

    def request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, signed: bool = False) -> Dict[str, Any]:
        """
        Sends an HTTP request to the Binance Futures Testnet API.
        
        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            endpoint: API endpoint path (e.g. /fapi/v1/order)
            params: Query or body parameters
            signed: Whether the endpoint requires signature authentication
            
        Returns:
            Dict[str, Any]: The parsed JSON response.
            
        Raises:
            BinanceAPIError: If the server returns a non-2xx status code.
            requests.RequestException: For network/connection issues.
        """
        method = method.upper()
        url = f"{self.BASE_URL}{endpoint}"
        
        req_params = (params or {}).copy()
        
        if signed:
            req_params["timestamp"] = self._get_timestamp()
            # Construct raw query string for signature
            query_string = urllib.parse.urlencode(req_params)
            signature = self._sign_query(query_string)
            req_params["signature"] = signature

        # Prepare parameters for the request
        # For Binance, all signed params (even on POST/DELETE) are typically passed in query parameters or form data.
        # We will pass them as query string for GET, and data/form-encoded parameters for POST.
        kwargs = {}
        if method == "GET":
            kwargs["params"] = req_params
            log_params_str = urllib.parse.urlencode(req_params)
            logger.info(f"Outgoing Request: {method} {url}?{log_params_str}")
        else:
            kwargs["data"] = req_params
            log_params_str = urllib.parse.urlencode(req_params)
            logger.info(f"Outgoing Request: {method} {url} | Body: {log_params_str}")

        try:
            response = self.session.request(method, url, timeout=15, **kwargs)
            logger.info(f"Incoming Response: Status {response.status_code} | Body: {response.text}")
            
            if not response.ok:
                try:
                    err_json = response.json()
                    raise BinanceAPIError(
                        status_code=response.status_code,
                        code=err_json.get("code", 0),
                        message=err_json.get("msg", "Unknown API error")
                    )
                except ValueError:
                    # Not a JSON response
                    raise BinanceAPIError(
                        status_code=response.status_code,
                        code=0,
                        message=response.text
                    )
            
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Network error during request {method} {url}: {e}", exc_info=True)
            raise e
        except BinanceAPIError as e:
            logger.error(f"Binance API returned error status: {e}", exc_info=True)
            raise e
        except Exception as e:
            logger.error(f"Unexpected error during API request: {e}", exc_info=True)
            raise e

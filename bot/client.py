import time
import hmac
import hashlib
import requests
from typing import Any, Dict, Optional
from urllib.parse import urlencode

from bot.logging_config import setup_logger

logger = setup_logger("trading_bot.client")

TESTNET_BASE_URL = "https://testnet.binancefuture.com"


class BinanceClientError(Exception):
    """Raised when the Binance API returns an error response."""
    pass


class NetworkError(Exception):
    """Raised when a network/connection error occurs."""
    pass


class BinanceClient:
    """
    Lightweight wrapper around the Binance Futures Testnet REST API.
    Handles authentication (HMAC-SHA256 signatures) and HTTP calls.
    """

    def __init__(self, api_key: str, api_secret: str, base_url: str = TESTNET_BASE_URL):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "X-MBX-APIKEY": self.api_key,
            "Content-Type": "application/json",
        })
        logger.info("BinanceClient initialised — base URL: %s", self.base_url)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _timestamp(self) -> int:
        return int(time.time() * 1000)

    def _sign(self, params: dict) -> str:
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return signature

    def _get(self, endpoint: str, params: Optional[dict] = None, signed: bool = False) -> Any:
        params = params or {}
        if signed:
            params["timestamp"] = self._timestamp()
            params["signature"] = self._sign(params)

        url = f"{self.base_url}{endpoint}"
        logger.debug("GET %s | params: %s", url, {k: v for k, v in params.items() if k != "signature"})

        try:
            response = self.session.get(url, params=params, timeout=10)
        except requests.exceptions.ConnectionError as exc:
            logger.error("Network error on GET %s: %s", url, exc)
            raise NetworkError(f"Could not connect to {url}: {exc}") from exc
        except requests.exceptions.Timeout as exc:
            logger.error("Request timed out on GET %s: %s", url, exc)
            raise NetworkError(f"Request timed out: {url}") from exc
        except requests.exceptions.RequestException as exc:
            logger.error("Request error on GET %s: %s", url, exc)
            raise NetworkError(f"Request error: {exc}") from exc

        return self._handle_response(response)

    def _post(self, endpoint: str, params: dict, signed: bool = True) -> Any:
        if signed:
            params["timestamp"] = self._timestamp()
            params["signature"] = self._sign(params)

        url = f"{self.base_url}{endpoint}"
        log_params = {k: v for k, v in params.items() if k != "signature"}
        logger.debug("POST %s | params: %s", url, log_params)

        try:
            response = self.session.post(url, params=params, timeout=10)
        except requests.exceptions.ConnectionError as exc:
            logger.error("Network error on POST %s: %s", url, exc)
            raise NetworkError(f"Could not connect to {url}: {exc}") from exc
        except requests.exceptions.Timeout as exc:
            logger.error("Request timed out on POST %s: %s", url, exc)
            raise NetworkError(f"Request timed out: {url}") from exc
        except requests.exceptions.RequestException as exc:
            logger.error("Request error on POST %s: %s", url, exc)
            raise NetworkError(f"Request error: {exc}") from exc

        return self._handle_response(response)

    def _handle_response(self, response: requests.Response) -> Any:
        logger.debug("Response %s: %s", response.status_code, response.text[:500])
        try:
            data = response.json()
        except ValueError:
            raise BinanceClientError(f"Non-JSON response (HTTP {response.status_code}): {response.text}")

        # Binance error responses always have a negative "code" field
        if isinstance(data, dict) and data.get("code", 0) < 0:
            code = data["code"]
            msg = data.get("msg", "Unknown API error")
            logger.error("Binance API error %s: %s", code, msg)

            # -4120: order type not supported on this endpoint (testnet limitation)
            if code == -4120:
                raise BinanceClientError(
                    "STOP_LIMIT orders are not supported on the Binance Futures Testnet. "
                    "This order type works correctly on the mainnet. "
                    "Use MARKET or LIMIT orders for testnet testing."
                )

            raise BinanceClientError(f"API error {code}: {msg}")

        return data

    # ------------------------------------------------------------------
    # Public API methods
    # ------------------------------------------------------------------

    def get_server_time(self) -> Dict:
        """Check server connectivity and return server time."""
        return self._get("/fapi/v1/time")

    def get_exchange_info(self) -> Dict:
        """Return exchange trading rules and symbol information."""
        return self._get("/fapi/v1/exchangeInfo")

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        time_in_force: str = "GTC",
    ) -> Dict:
        """
        Place a futures order on the testnet.

        Args:
            symbol:        e.g. 'BTCUSDT'
            side:          'BUY' or 'SELL'
            order_type:    'MARKET' or 'LIMIT'
            quantity:      order quantity
            price:         required for LIMIT orders
            time_in_force: 'GTC' (default), 'IOC', 'FOK'

        Returns:
            Raw API response dict.
        """
        params: Dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
        }

        if order_type == "LIMIT":
            if price is None:
                raise ValueError("price is required for LIMIT orders")
            params["price"] = price
            params["timeInForce"] = time_in_force

        elif order_type == "STOP_LIMIT":
            if price is None:
                raise ValueError("price is required for STOP_LIMIT orders")
            if stop_price is None:
                raise ValueError("stop_price is required for STOP_LIMIT orders")
            params["type"] = "STOP"  # Binance internal name for stop-limit
            params["price"] = price
            params["stopPrice"] = stop_price
            params["timeInForce"] = time_in_force

        logger.info(
            "Placing order — symbol=%s side=%s type=%s qty=%s price=%s",
            symbol, side, params["type"], quantity, price,
        )

        response = self._post("/fapi/v1/order", params)
        logger.info("Order placed successfully — orderId=%s status=%s", response.get("orderId"), response.get("status"))
        return response

from datetime import datetime

from lib.algorithm_interface import AlgorithmInterface
from lib.exchange_interface import ExchangeInterface
from lib.logger import logger, float_to_human_readable


class SafeTrade(AlgorithmInterface):
    exchange: ExchangeInterface
    last_bought_price: float
    last_sold_price: float
    wallet_crypto_amount: float
    wallet_fiat_amount: float

    def __init__(self, exchange: ExchangeInterface, cached_vars: dict):
        super().__init__(exchange, cached_vars)

    def get_current_vars(self) -> dict:
        return {
            "last_bought_price": self.last_bought_price,
            "last_sold_price": self.last_sold_price,
            "wallet_crypto_amount": self.wallet_crypto_amount,
            "wallet_fiat_amount": self.wallet_fiat_amount
        }

    def set_current_vars(self, new_vars: dict):
        self.last_bought_price = new_vars.get("last_bought_price", 0.0)
        # force a purchase on next action if last_bought_price is not set
        if self.last_bought_price == 0.0:
            logger.warning(f"Last_bought_price is not set, forcing a purchase on next action.")
            self.last_sold_price = self.exchange.get_current_price() * 10
            self.last_bought_price = self.exchange.get_current_price() * 10
        else:
            self.last_sold_price = new_vars.get("last_sold_price", 0.0)
        self.wallet_crypto_amount = self.exchange.get_crypto_wallet_amount()
        self.wallet_fiat_amount = self.exchange.get_fiat_wallet_amount()
        if new_vars.get("wallet_fiat_amount") is not None and self.wallet_fiat_amount != new_vars.get(
                "wallet_fiat_amount"):
            logger.warning(f"Provided/cached wallet_fiat_amount ({new_vars.get('wallet_fiat_amount')}) "
                           f"does not match wallet_fiat_amount reported by exchange ({self.wallet_fiat_amount})."
                           f"Ignoring new value and using exchange wallet amount.")
        if new_vars.get("wallet_crypto_amount") is not None and self.wallet_crypto_amount != new_vars.get(
                "wallet_crypto_amount"):
            logger.warning(f"Provided/cached wallet_crypto_amount ({new_vars.get('wallet_crypto_amount')}) "
                           f"does not match wallet_crypto_amount reported by exchange ({self.wallet_crypto_amount})."
                           f"Ignoring new value and using exchange wallet amount.")

    def perform_action(self) -> dict:
        current_price = self.exchange.get_current_price()
        logger.debug(f"{self.codename}: Current price: {float_to_human_readable(current_price)}")
        result = {
            "action": "hold",
            "action_result": None,
            "transacted_amount": None,
        }
        if current_price * (1 - self.exchange.exchange_fee * 2) > self.last_bought_price and self.wallet_crypto_amount != 0:
            expected_fiat_amount: float = current_price * self.wallet_crypto_amount * (1 - self.exchange.exchange_fee)
            # sell entire crypto wallet
            result = self.perform_crypto_sale(self.wallet_crypto_amount, expected_fiat_amount)
            if result["action_result"] != "failure":
                self.last_sold_price = current_price

        elif current_price * (
                1 + self.exchange.exchange_fee * 2) < self.last_sold_price and self.wallet_fiat_amount != 0:
            expected_crypto_amount: float = 1 / current_price * self.wallet_fiat_amount * (
                    1 - self.exchange.exchange_fee)
            # use entire fiat wallet to buy
            result = self.perform_crypto_purchase(self.wallet_fiat_amount, expected_crypto_amount)
            if result["action_result"] != "failure":
                self.last_bought_price = current_price
        else:
            logger.debug(f"{self.codename}: Performing no action")

        result["wallet_fiat_amount"] = self.wallet_fiat_amount
        result["wallet_crypto_amount"] = self.wallet_crypto_amount
        result["current_price"] = current_price
        result["unix_timestamp"] = datetime.now().timestamp()

        return result

import json
import urllib.request
from typing import Tuple

from lib.exchange_interface import ExchangeInterface
from lib.logger import logger


class Simulator(ExchangeInterface):
    _wallet_crypto_amount: float
    _wallet_fiat_amount: float

    def __init__(self, cached_vars=None):
        super().__init__()
        if cached_vars is None:
            logger.warning("No cached vars provided, using BTC-EUR as crypto_codename, 0.001 as exchange_fee, "
                           "assuming empty crypto wallet and 100.0 in fiat wallet")
            cached_vars = {
                "crypto_codename": "BTC-EUR",
                "exchange_fee": 0.001,
                "wallet_crypto_amount": 0,
                "wallet_fiat_amount": 100.0
            }
        self.set_current_vars(cached_vars)

    def get_current_vars(self) -> dict:
        return {
            "crypto_codename": self.crypto_codename,
            "exchange_fee": self.exchange_fee,
            "wallet_crypto_amount": self._wallet_crypto_amount,
            "wallet_fiat_amount": self._wallet_fiat_amount
        }

    def set_current_vars(self, new_vars: dict):
        self.crypto_codename = new_vars["crypto_codename"]
        self.exchange_fee = new_vars["exchange_fee"]
        self._wallet_crypto_amount = new_vars["wallet_crypto_amount"]
        self._wallet_fiat_amount = new_vars["wallet_fiat_amount"]

    def get_crypto_wallet_amount(self) -> float:
        return self._wallet_crypto_amount

    def get_fiat_wallet_amount(self) -> float:
        return self._wallet_fiat_amount

    def get_current_price(self) -> float:
        # get current price from yahoo
        yahoo_dat = urllib.request.urlopen("https://query1.finance.yahoo.com/v8/finance/chart/SHIB-EUR").read().decode(
            'utf-8')
        result_dictionary = json.loads(yahoo_dat)
        return result_dictionary["chart"]["result"][0]["meta"]["regularMarketPrice"]

    def buy_crypto(self, fiat_to_spend_amount: float) -> Tuple[bool, float]:
        if fiat_to_spend_amount > self._wallet_fiat_amount:
            logger.error(f"Not enough fiat to in wallet to spend requested amount {fiat_to_spend_amount}. "
                         f"Current fiat total: {self._wallet_fiat_amount}")
            return False, 0
        self._wallet_crypto_amount = 1 / self.get_current_price() * self._wallet_fiat_amount * (1 - self.exchange_fee)
        self._wallet_fiat_amount = 0
        # simulations never fail
        return True, self._wallet_crypto_amount

    def sell_crypto(self, crypto_to_sell_amount: float) -> Tuple[bool, float]:
        if crypto_to_sell_amount > self._wallet_crypto_amount:
            logger.error(f"Not enough crypto to sell requested amount ({crypto_to_sell_amount}). "
                         f"Current crypto total: {self._wallet_crypto_amount}")
            return False, 0
        self._wallet_fiat_amount = self.get_current_price() * self._wallet_crypto_amount * (1 - self.exchange_fee)
        self._wallet_crypto_amount = 0
        # simulations never fail
        return True, self._wallet_fiat_amount

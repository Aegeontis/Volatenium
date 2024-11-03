from abc import ABC, abstractmethod
from typing import Tuple


class ExchangeInterface(ABC):
    exchange_fee: float
    crypto_codename: str

    @abstractmethod
    def __init__(self, cached_vars: dict = None):
        pass

    @abstractmethod
    def get_current_vars(self) -> dict:
        """
        Returns the current set variables of the exchange, such as crypto_codename and exchange_fee
        :return:
        """
        pass

    @abstractmethod
    def set_current_vars(self, new_vars: dict):
        """
        Sets new variables of the exchange, such as crypto_codename and exchange_fee
        :return:
        """
        pass

    @abstractmethod
    def get_current_price(self) -> float:
        """
        Returns the current price of crypto_codename as reported by the exchange.
        :return:
        """
        pass

    @abstractmethod
    def get_crypto_wallet_amount(self) -> float:
        """
        Returns the amount of crypto_codename in the exchange wallet.
        :return:
        """
        pass

    @abstractmethod
    def get_fiat_wallet_amount(self) -> float:
        """
        Returns the amount of fiat in the exchange wallet.
        :return:
        """
        pass

    @abstractmethod
    def buy_crypto(self, fiat_to_spend_amount: float) -> Tuple[bool, float]:
        """
        Buys crypto_codename crypto for requested_amount of fiat.
        :param fiat_to_spend_amount: Amount of fiat to spend
        :return: A tuple (success, crypto_amount), where:
            - success (bool): True if the transaction is successful, False if the transaction failed.
            - crypto_amount (float): The amount of crypto that was actually bought on the exchange. Returns None if the
            transaction fails.
        """
        pass

    @abstractmethod
    def sell_crypto(self, crypto_to_sell_amount: float) -> Tuple[bool, float]:
        """
        Sells requested_amount of crypto_codename crypto.
        :param crypto_to_sell_amount: Amount of crypto to sell
        :return: A tuple (success, crypto_amount), where:
            - success (bool): True if the transaction is successful, False if the transaction failed.
            - crypto_amount (float): The amount of fiat that was actually received on the exchange. Returns None if the
            transaction fails.
        """
        pass

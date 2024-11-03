from abc import ABC, abstractmethod

from lib.exchange_interface import ExchangeInterface
from lib.logger import logger


class AlgorithmInterface(ABC):
    codename: str
    wallet_fiat_amount: float
    wallet_crypto_amount: float

    def __init__(self, exchange: ExchangeInterface, cached_vars=None):
        if cached_vars is None:
            cached_vars = {}
        self.exchange = exchange
        self.codename = self.__class__.__name__
        self.set_current_vars(cached_vars)

    @abstractmethod
    def get_current_vars(self) -> dict:
        """
        Returns the current set variables of the algorithm. Used to store the current state of the algorithm on disk.
        :return:
        """
        pass

    @abstractmethod
    def set_current_vars(self, new_vars: dict):
        """
        Sets new variables of the algorithm. Used to restore the state of the algorithm from disk.
        :param new_vars:
        :return:
        """
        pass

    def perform_crypto_sale(self, crypto_to_sell_amount: float, expected_fiat_amount: float) -> dict:
        """
        Performs a crypto sale and returns a dictionary with the results.
        :param crypto_to_sell_amount: Amount of crypto to sell
        :param expected_fiat_amount: Expected amount of fiat to be received in the exchange.
        :return: A dictionary with the following structure:
            {
                "action": "sell_crypto",
                "action_result": str # "success" | "failure" | "partial"
                "transacted_amount": float,  # The amount of fiat that was received or None
            }
        """
        result_dict: dict = {
            "action": "sell_crypto",
            "action_result": None,
            "transacted_amount": None
        }
        # perform sale on the exchange
        action_success, received_fiat = self.exchange.sell_crypto(crypto_to_sell_amount)

        # evaluate sale results
        if action_success:
            if received_fiat != expected_fiat_amount:
                result_dict["action_result"] = "partial"
                logger.warning(
                    f"{self.codename}: Partial crypto sale: Expected {expected_fiat_amount} fiat, received {received_fiat} fiat")
            else:
                result_dict["action_result"] = "success"
                logger.info(
                    f"{self.codename}: Successful crypto sale: Expected {expected_fiat_amount} fiat, received {received_fiat} fiat")
        else:
            result_dict["action_result"] = "failure"
            logger.error(
                f"{self.codename}: Failed crypto sale: Expected {expected_fiat_amount} fiat, received {received_fiat} fiat")
        result_dict["transacted_amount"] = received_fiat

        # update local wallet amounts with exchange reported amounts
        self.wallet_fiat_amount = self.exchange.get_fiat_wallet_amount()
        self.wallet_crypto_amount = self.exchange.get_crypto_wallet_amount()

        return result_dict

    def perform_crypto_purchase(self, fiat_to_spend_amount: float, expected_crypto_amount: float) -> dict:
        """
        Performs a crypto purchase and returns a dictionary with the results.
        :param fiat_to_spend_amount: Amount of fiat to spend
        :param expected_crypto_amount: Expected amount of crypto to be received
        :return: A dictionary with the following structure:
            {
                "action": "buy_crypto",
                "action_result": str, # "success", "failure" or "partial"
                "transacted_amount": float,  # The amount of crypto that was bought or None
            }
        """
        result_dict: dict = {
            "action": "buy_crypto",
            "action_result": None,
            "transacted_amount": None
        }

        # perform purchase on the exchange
        action_success, bought_amount = self.exchange.buy_crypto(fiat_to_spend_amount)

        # evaluate purchase results
        if action_success:
            if bought_amount != expected_crypto_amount:
                result_dict["action_result"] = "partial"
                logger.warning(
                    f"{self.codename}: Partial purchase: Expected {expected_crypto_amount}, received {bought_amount}")
            else:
                result_dict["action_result"] = "success"
                logger.info(
                    f"{self.codename}: Successful purchase: Expected {expected_crypto_amount}, received {bought_amount}")
        else:
            result_dict["action_result"] = "failure"
            logger.error(
                f"{self.codename}: Failed purchase: Expected {expected_crypto_amount}, received {bought_amount}")
        result_dict["transacted_amount"] = bought_amount

        # update local wallet amounts with exchange reported amounts
        self.wallet_fiat_amount = self.exchange.get_fiat_wallet_amount()
        self.wallet_crypto_amount = self.exchange.get_crypto_wallet_amount()

        return result_dict

    @abstractmethod
    def perform_action(self) -> dict:
        """
        Calculates the decision to buy or sell and performs it or does nothing .
        :return: A dictionary with the following structure:
            {
                "action": str,  # "buy_crypto" | "sell_crypto" | "hold"
                "action_result": str, # "success" | "failure" | "partial"
                "transacted_amount": float,  # Amount that was bought or sold or None
                "wallet_fiat_amount": float,  # Fiat that is currently in the exchange wallet
                "wallet_crypto_amount": float,  # Crypto that is currently in the exchange wallet
                "current_price": float # Reported market price at time of action
                "unix_timestamp": int # The current unix timestamp
            }
        """
        pass

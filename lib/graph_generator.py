import json
from datetime import datetime

import matplotlib.dates as mdates
from matplotlib import pyplot as plt

from lib.logger import logger


def generate_graph(algorithm_name: str, exchange_name: str, crypto_codename: str):
    # Prepare data for plotting
    with open("cache/history.json", "r") as f:
        data = json.load(f)[exchange_name][algorithm_name]

    if data is None:
        logger.error(f"No data found for {algorithm_name} on {exchange_name}.")
        return

    # Only use data from one crypto_codename
    filtered_data = [item for item in data if item["crypto_codename"] == crypto_codename]

    if not filtered_data:
        logger.error(f"No data found for {exchange_name} on {algorithm_name} with crypto_codename {crypto_codename}.")
        return

    # Convert UNIX timestamps to datetime and then to matplotlib date format
    timestamps = [mdates.date2num(datetime.fromtimestamp(item["unix_timestamp"])) for item in filtered_data]
    prices = [item["current_price"] for item in filtered_data]

    # Separate data by action type
    buy_x = [timestamps[i] for i, item in enumerate(filtered_data) if item["action"] == "buy_crypto"]
    buy_y = [prices[i] for i, item in enumerate(filtered_data) if item["action"] == "buy_crypto"]

    sell_x = [timestamps[i] for i, item in enumerate(filtered_data) if item["action"] == "sell_crypto"]
    sell_y = [prices[i] for i, item in enumerate(filtered_data) if item["action"] == "sell_crypto"]

    hold_x = [timestamps[i] for i, item in enumerate(filtered_data) if item["action"] == "hold"]
    hold_y = [prices[i] for i, item in enumerate(filtered_data) if item["action"] == "hold"]

    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot buy, sell, and hold actions
    ax.scatter(buy_x, buy_y, c="red", s=20, label="Buy")
    ax.scatter(sell_x, sell_y, c="green", s=20, label="Sell")
    ax.scatter(hold_x, hold_y, c="blue", s=20, label="Hold")

    # Format x-axis as date and y-axis as human-readable numbers
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
    ax.yaxis.get_major_formatter().set_scientific(False)

    # Labels and legend
    ax.set_xlabel("Timestamp")
    ax.set_ylabel("Crypto Price")
    plt.xticks(rotation=45)
    ax.legend()
    # add title
    ax.set_title(f"{algorithm_name} on {exchange_name}")

    # Save the graph as an SVG file at the specified path
    plt.tight_layout()
    plt.savefig("cache/graph.svg", format="svg")
    logger.info(f"Graph saved at cache/graph.svg")
    plt.close()

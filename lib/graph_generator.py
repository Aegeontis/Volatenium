import json
from datetime import datetime

import matplotlib.dates as mdates
from matplotlib import pyplot as plt


def generate_graph():
    # Prepare data for plotting
    with open("cache/history.json", "r") as f:
        data = json.load(f)

    # Convert UNIX timestamps to datetime and then to matplotlib date format
    timestamps = [mdates.date2num(datetime.fromtimestamp(item["unix_timestamp"])) for item in data]
    prices = [item["current_price"] for item in data]

    # Separate data by action type
    buy_x = [timestamps[i] for i, item in enumerate(data) if item["action"] == "buy_crypto"]
    buy_y = [prices[i] for i, item in enumerate(data) if item["action"] == "buy_crypto"]

    sell_x = [timestamps[i] for i, item in enumerate(data) if item["action"] == "sell_crypto"]
    sell_y = [prices[i] for i, item in enumerate(data) if item["action"] == "sell_crypto"]

    hold_x = [timestamps[i] for i, item in enumerate(data) if item["action"] == "hold"]
    hold_y = [prices[i] for i, item in enumerate(data) if item["action"] == "hold"]

    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot buy, sell, and hold actions
    ax.scatter(buy_x, buy_y, c="red", s=20, label="Buy")
    ax.scatter(sell_x, sell_y, c="green", s=20, label="Sell")
    ax.scatter(hold_x, hold_y, c="blue", s=0.5, label="Hold")

    # Format x-axis as date and y-axis as human-readable numbers
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
    ax.yaxis.get_major_formatter().set_scientific(False)

    # Labels and legend
    ax.set_xlabel("Timestamp")
    ax.set_ylabel("Crypto Price")
    plt.xticks(rotation=45)
    ax.legend()

    # Save the graph as an SVG file at the specified path
    plt.tight_layout()
    plt.savefig("cache/graph.svg", format="svg")
    plt.close()

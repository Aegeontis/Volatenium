#!/usr/bin/python3

import argparse
import importlib
import re as regex
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from lib.graph_generator import generate_graph
from lib.logger import *

if __name__ == '__main__':
    logger.info("Starting script")

    parser = argparse.ArgumentParser()
    parser.add_argument("--generate-graph", action="store_true",
                        help="Generate graphs using cache/history.json and exit.")

    args = parser.parse_args()

    if args.generate_graph:
        # read algo name and exchange name from cli
        exchange_name = input("Enter exchange name: ")
        algorithm_name = input("Enter algorithm name: ")
        algo_id = input("Enter algorithm id (check settings.yaml): ")
        logger.info(f"Generating graphs for {algorithm_name} on {exchange_name}")
        generate_graph(algorithm_name, exchange_name, algo_id)
        logger.info("Graphs generated. Exiting...")
        exit()

    logger.info("Reading settings")
    settings = read_settings()

    action_interval = (settings.get("general_settings", {}) or {}).get("action_interval", None)
    if action_interval is None:
        logger.warning("action_interval not set, using 60 seconds as default")
        action_interval = 60
    else:
        logger.info(f"action_interval set to {action_interval} seconds")

    logger.info("Reading cached variables")
    cached_vars = read_state()

    logger.info("Initiating algorithms")
    jobs = []
    for exchange in settings["exchanges"]:
        logger.info(f"Initializing exchange: {exchange}")

        # load the cached values for this algorithm
        if exchange not in cached_vars:
            cached_vars[exchange] = {}

        # Import the exchange class
        exchange_module = importlib.import_module(
            f"exchanges.{regex.sub(r'([a-z])([A-Z])', r'\1_\2', exchange).lower()}")
        exchange_class = getattr(exchange_module, exchange)
        initialized_ids = []
        for algorithm in settings["exchanges"][exchange]["algorithms"]:
            algorithm_name = algorithm["codename"]
            logger.info(f"Initializing {algorithm_name} on {exchange}")
            # Import the algorithm class
            algo_module = importlib.import_module(
                f"algorithms.{regex.sub(r'([a-z])([A-Z])', r'\1_\2', algorithm_name).lower()}")
            algorithm_class = getattr(algo_module, algorithm_name)

            # use cached values if they exist, otherwise use values from settings
            algorithm_vars = None
            exchange_vars = None
            if cached_vars.get("exchanges", {}).get(exchange, {}) != {}:
                if initialized_ids.__contains__(algorithm["id"]):
                    logger.error(
                        f"Duplicate algorithm id found for {algorithm_name} on {exchange}. Duplicate id: {algorithm["id"]}")
                    logger.error("Duplicate ids can lead to data loss and unexpected behavior.")
                    logger.critical("Exiting...")
                    exit(1)
                initialized_ids.append(algorithm["id"])
                exchange_vars = next(
                    (entry for entry in cached_vars["exchanges"][exchange]["algorithms"] if
                     entry["id"] == algorithm["id"]),
                    {}).get("exchange_vars", None)
                algorithm_vars = next(
                    (entry for entry in cached_vars["exchanges"][exchange]["algorithms"] if
                     entry["id"] == algorithm["id"]),
                    {}).get("algorithm_vars", None)
            if algorithm_vars is None or algorithm_vars == {}:
                algorithm_vars = algorithm.get("algorithm_vars", None)
            if exchange_vars is None or exchange_vars == {}:
                exchange_vars = algorithm.get("exchange_vars", None)

            # Create a separate object for each enabled exchange for this algorithm
            jobs.append(algorithm_class(exchange_class(exchange_vars), algorithm["id"], algorithm_vars))

    logger.info(f"Starting main loop with {len(jobs)} jobs and {action_interval} seconds between actions")
    while True:
        logger.info(f"Performing actions...")
        state_vars = {
            "exchanges": {}
        }
        # Execute all algorithms at the same time
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(algorithm.perform_action): algorithm for algorithm in jobs}

            for future in as_completed(futures):
                algorithm = futures[future]
                log_action(future.result(), algorithm.exchange.codename, algorithm.codename)

                exchange_exists = False
                for exchange in state_vars["exchanges"]:
                    if algorithm.exchange.codename == exchange:
                        exchange_exists = True
                        state_vars["exchanges"][exchange]["algorithms"].append({
                            "id": algorithm.id_in_list,
                            "codename": algorithm.codename,
                            "algorithm_vars": algorithm.get_current_vars(),
                            "exchange_vars": algorithm.exchange.get_current_vars()
                        })
                    break
                if not exchange_exists:
                    state_vars["exchanges"][algorithm.exchange.codename] = {
                        "algorithms": [{
                            "id": algorithm.id_in_list,
                            "codename": algorithm.codename,
                            "algorithm_vars": algorithm.get_current_vars(),
                            "exchange_vars": algorithm.exchange.get_current_vars()
                        }]
                    }

        # store variables
        store_state(state_vars)

        # wait until the next minute
        wait_time = action_interval - time.localtime().tm_sec
        logger.info(f"Sleeping until next minute ({wait_time}s)")
        time.sleep(wait_time)

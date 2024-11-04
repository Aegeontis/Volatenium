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
        algorithm_name = input("Enter algorithm name: ")
        exchange_name = input("Enter exchange name: ")
        logger.info(f"Generating graphs for {algorithm_name} on {exchange_name}")
        generate_graph(algorithm_name, exchange_name)
        logger.info("Graphs generated. Exiting...")
        exit()

    logger.info("Reading settings")
    settings = read_settings()

    logger.info("Reading cached variables")
    cached_vars = read_variables()

    logger.info("Initiating algorithms")
    algorithms = []
    for algorithm in settings["enabled_algorithms"]:
        logger.info(f"Initializing {algorithm['name']}")
        # Import the algorithm module
        module = importlib.import_module(
            f"algorithms.{regex.sub(r'([a-z])([A-Z])', r'\1_\2', algorithm["name"]).lower()}")
        # Get the class defined in the module
        algorithm_class = getattr(module, algorithm["name"])
        # Create a separate object for each enabled exchange for this algorithm
        for exchange in algorithm["enabled_exchanges"]:
            logger.info(f"Initializing {algorithm['name']} on {next(iter(exchange))}")
            # use first key as exchange name
            exchange_name = next(iter(exchange))
            # Import the exchange module
            module = importlib.import_module(
                f"exchanges.{regex.sub(r'([a-z])([A-Z])', r'\1_\2', exchange_name).lower()}")
            # Get the class defined in the module
            exchange_class = getattr(module, exchange_name)
            # Instantiate both the algorithm and the exchange and add it to the list
            algorithms.append(
                algorithm_class(exchange_class(exchange.get(exchange_name, None)),
                                cached_vars.get(algorithm["name"], {}).get("algorithm_vars", None)))

    logger.info("Starting main loop")
    # TODO: Add setting for loop speed for each algorithm and start separate loops
    while True:
        logger.debug(f"Performing actions...")
        variables = {}
        # Execute all algorithms at the same time
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(algorithm.perform_action): algorithm for
                       algorithm in algorithms}

            for future in as_completed(futures):
                algorithm = futures[future]
                log_action(future.result(), algorithm.codename, algorithm.exchange.codename)

                # make sure the dict exists
                if algorithm.codename not in variables:
                    variables[algorithm.codename] = []

                variables[algorithm.codename].append({
                    algorithm.exchange.codename: algorithm.exchange.get_current_vars(),
                    "algorithm_vars": algorithm.get_current_vars()
                })

        # store variables
        store_variables(variables)

        # wait until the next minute
        wait_time = 60 - time.localtime().tm_sec
        logger.debug(f"Sleeping until next minute ({wait_time}s)")
        time.sleep(wait_time)

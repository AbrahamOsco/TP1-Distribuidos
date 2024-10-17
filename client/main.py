import logging
import os
from client.analyzer.SteamAnalyzer import SteamAnalyzer
import signal

def run_analyzer(percent_of_file):
    analyzer = SteamAnalyzer(percent_of_file)
    signal.signal(signal.SIGTERM, lambda _n, _f: analyzer.stop())
    analyzer.run()

def main():
    percent_of_file_for_use_by_execution = os.getenv("PERCENT_OF_FILE_FOR_USE_BY_EXECUTION", 1)
    percentages = [float(p.strip()) for p in percent_of_file_for_use_by_execution.split(',')]
    logging.info(f"Starting executions of Client")

    for i, percent in enumerate(percentages, 1):
        logging.info(f"Starting execution {i} of {len(percentages)} with {percent*100}% of file")
        run_analyzer(percent)
        logging.info(f"Finished execution {i} of {len(percentages)}")
    
    logging.info("All executions completed")

main()


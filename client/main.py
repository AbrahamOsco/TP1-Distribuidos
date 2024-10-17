import logging
import os
from client.analyzer.SteamAnalyzer import SteamAnalyzer
import signal

def run_analyzer(percent_of_file):
    analyzer = SteamAnalyzer(percent_of_file)
    signal.signal(signal.SIGTERM, lambda _n, _f: analyzer.stop())
    try:
        analyzer.run()
    finally:
        analyzer.stop()

def main():
    print("Starting Client")
    percent_of_file_for_use_by_execution = os.getenv("PERCENT_OF_FILE_FOR_USE_BY_EXECUTION", 1)
    print(f"Percent of file for use by execution: {percent_of_file_for_use_by_execution}")
    percentages = [float(p.strip()) for p in percent_of_file_for_use_by_execution.split(',')]
    print(f"Starting executions of Client")

    for i, percent in enumerate(percentages, 1):
        print(f"Starting execution {i} of {len(percentages)} with {percent*100}% of file")
        run_analyzer(percent)
        print(f"Finished execution {i} of {len(percentages)}")
    
    print("All executions completed")


if __name__ == "__main__":
    main()


from client.analyzer.SteamAnalyzer import SteamAnalyzer
import signal

def main():
    analyzer = SteamAnalyzer()
    signal.signal(signal.SIGTERM, lambda _n,_f: analyzer.stop())
    analyzer.run()

main()


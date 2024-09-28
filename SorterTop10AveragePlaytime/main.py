from Sorter import Sorter
import signal

def main():
    sorter = Sorter()
    signal.signal(signal.SIGTERM, lambda _n,_f: sorter.stop())
    sorter.run()

if __name__ == "__main__":
    main()
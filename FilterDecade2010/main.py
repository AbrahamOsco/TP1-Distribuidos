from Filter import Filter
import signal

def main():
    filter = Filter()
    signal.signal(signal.SIGTERM, lambda _n,_f: filter.stop())
    filter.run()

if __name__ == "__main__":
    main()
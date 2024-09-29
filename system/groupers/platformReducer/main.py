from Reducer import Reducer
import signal

def main():
    reducer = Reducer()
    signal.signal(signal.SIGTERM, lambda _n,_f: reducer.stop())
    reducer.run()

if __name__ == "__main__":
    main()
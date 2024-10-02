"""from Grouper import Grouper
import signal

def main():
    grouper = Grouper()
    signal.signal(signal.SIGTERM, lambda _n,_f: grouper.stop())
    grouper.run()

if __name__ == "__main__":
    main()"""
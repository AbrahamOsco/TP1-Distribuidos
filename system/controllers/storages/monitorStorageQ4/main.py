"""from Storage import Storage
import signal

def main():
    storage = Storage()
    signal.signal(signal.SIGTERM, lambda _n,_f: storage.stop())
    storage.run()

if __name__ == "__main__":
    main()"""
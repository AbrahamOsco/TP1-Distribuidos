"""from Select import Select
import signal

def main():
    select = Select()
    signal.signal(signal.SIGTERM, lambda _n,_f: select.stop())
    select.run()

if __name__ == "__main__":
    main()"""
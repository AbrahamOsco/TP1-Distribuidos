"""from system.controllers.joiners.MonitorJoinerQ4.Joiner import Joiner
import signal

def main():
    joiner = Joiner()
    signal.signal(signal.SIGTERM, lambda _n,_f: joiner.stop())
    joiner.run()

if __name__ == "__main__":
    main()"""
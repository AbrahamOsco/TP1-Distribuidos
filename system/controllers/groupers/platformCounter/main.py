from system.controllers.groupers.platformCounter.PlatformCounter import PlatformCounter
import signal

def main():
    platformCounter = PlatformCounter()
    #signal.signal(signal.SIGTERM, lambda _n,_f: counter.stop())
    platformCounter.run()

main()
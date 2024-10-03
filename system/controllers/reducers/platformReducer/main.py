from system.controllers.reducers.platformReducer.PlatformReducer import PlatformReducer
import signal

def main():
    platformReducer = PlatformReducer()
    #signal.signal(signal.SIGTERM, lambda _n,_f: counter.stop())
    platformReducer.run()

main()
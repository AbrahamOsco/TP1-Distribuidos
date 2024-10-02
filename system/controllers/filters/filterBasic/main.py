from system.controllers.filters.filterBasic.FilterBasic import FilterBasic
import signal

def main():
    filter = FilterBasic()
    #signal.signal(signal.SIGTERM, lambda _n,_f: filter.stop())
    filter.run()

main()

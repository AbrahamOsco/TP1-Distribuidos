from Filter import FilterGender
import signal

def main():
   filter = FilterGender()
   signal.signal(signal.SIGTERM, lambda _n,_f: filter.stop())
   filter.run()

if __name__ == "__main__":
   main()
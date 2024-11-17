import time
import logging
import threading
from LeaderElection import LeaderElection

def main():
    print(f"Starting Leader Election... 🗡️🗡️ ⚡🗡️ ⚡🗡️ ⚡ ⚡")
    leader_election :LeaderElection = LeaderElection()
    thr_leader = threading.Thread(target= lambda: leader_election.find_new_leader())
    thr_leader.start()
    #time.sleep(5)
    #logging.info(f"[{leader_election.id}] Current Leader: {leader_election.get_leader_id()}")
    #if leader_election.am_i_leader():
    #   logging.info(f"[{leader_election.id}] Simulating leader failure...")
    #   logging.info("Deberia haberme ido! 🤿")
    #   leader_election.stop()
    #   exit(0)
    #   return
    #time.sleep(5)
    #if not leader_election.am_i_leader():
    #    logging.info(f"[{leader_election.id}] Starting new leader election after failure...")
    #    leader_election.find_new_leader()
    #
    #time.sleep(50)
    #thr_leader.join()
    #leader_election.free_resources()    

main()



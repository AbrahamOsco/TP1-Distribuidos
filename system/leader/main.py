import time
import logging
import threading
from LeaderElection import LeaderElection

def main():
    leader_election :LeaderElection = LeaderElection()
    thr_leader = threading.Thread(target= lambda: leader_election.find_new_leader())
    thr_leader.start()
    time.sleep(40)
    #time.sleep(4)
    #logging.info(f"[{leader_election.id}] Current Leader: {leader_election.get_leader_id()}")
    #if leader_election.am_i_leader():
    #   logging.info(f"[{leader_election.id}] Simulating leader failure...")
    #   logging.info("Deberia haberme ido! 🤿")
    #   leader_election.stop()
    #   exit(0)
    #   return
    #time.sleep(1)
    #if not leader_election.am_i_leader():
    #    logging.info(f"[{leader_election.id}] Starting new leader election after failure...")
    #    leader_election.find_new_leader()
    #
    #time.sleep(1)
    #thr_leader.join()
    #leader_election.release_resources()    

main()
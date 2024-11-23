import os
import logging
from LeaderElection import LeaderElection

def main():
    leader_election = LeaderElection()
    leader_election.find_new_leader()
    logging.info("END  new leader end? 🌵")
main()


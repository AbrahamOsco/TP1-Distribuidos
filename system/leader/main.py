import time
import logging
from LeaderElection import LeaderElection


def main():
    leader_election = LeaderElection()
    leader_election.run()
    time.sleep(3)
    


main()
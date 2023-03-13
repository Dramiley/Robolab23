# !/usr/bin/env python3
from communication_facade import CommunicationFacade


class Odometry:
    communication: CommunicationFacade = None

    def __init__(self):
        """
        Initializes odometry module
        """

        # YOUR CODE FOLLOWS (remove pass, please!)
        pass

    def set_communication(self, communication: CommunicationFacade):
        self.communication = communication

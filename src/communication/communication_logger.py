#!/usr/bin/env python3

class CommunicationLogger:
    """
    Dummy logger class to replace the logger from the server
    """

    def debug(self, message):
        print("==> CommunicationLog: " + message)

    def error(self, message):
        print("==> CommunicationError: " + message)

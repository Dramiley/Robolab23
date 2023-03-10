#!/usr/bin/env python3

class CommunicationLogger:
    """
    Dummy logger class to replace the logger from the server
    """

    class bcolors:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKCYAN = '\033[96m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'

    def success(self, message):
        print()
        print(self.bcolors.OKGREEN + "==>\r\nCommunicationSuccess: ")
        print(message)
        print("<==")
        print(self.bcolors.ENDC)

    def debug(self, message):
        print()
        print(self.bcolors.OKBLUE + "==>\r\nCommunicationLog: ")
        print(message)
        print("<==")
        print(self.bcolors.ENDC)

    def error(self, message):
        print()
        print(self.bcolors.BOLD + self.bcolors.FAIL + "==>\r\nCommunicationError: ")
        print(message)
        print("<==")
        print()
        print(self.bcolors.ENDC)

    def warning(self, message):
        print()
        print(self.bcolors.BOLD + self.bcolors.WARNING + "==>\r\nCommunicationWarning: ")
        print(message)
        print("<==")
        print()
        print(self.bcolors.ENDC)

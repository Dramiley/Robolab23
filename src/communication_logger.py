#!/usr/bin/env python3
from controller import simulator_log


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

    level = -1

    def setLevel(self, level):
        self.level = level

    def success(self, message):
        simulator_log('communication.log', {'message': message, 'color': 'success'})
        print(self.bcolors.OKGREEN + message + self.bcolors.ENDC)

    def debug(self, message):
        simulator_log('communication.log', {'message': message, 'color': 'debug'})
        print(self.bcolors.OKBLUE + message + self.bcolors.ENDC)

    def error(self, message):
        simulator_log('communication.log', {'message': message, 'color': 'error'})
        print(self.bcolors.BOLD + self.bcolors.FAIL + message + self.bcolors.ENDC)

    def warning(self, message):
        simulator_log('communication.log', {'message': message, 'color': 'warning'})
        print(self.bcolors.BOLD + self.bcolors.WARNING + message + self.bcolors.ENDC)

    def info(self, message):
        simulator_log('communication.log', {'message': message, 'color': 'info'})
        print(self.bcolors.OKCYAN + message + self.bcolors.ENDC)

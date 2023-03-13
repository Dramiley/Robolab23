from communication import Communication
from robot import Robot
from communication_logger import CommunicationLogger
from odometry import Odometry


class Controller:
    robot = None
    communication = None
    odometry = None

    def __init__(self, client):
        # setup communication
        self.communication = Communication(client, CommunicationLogger()).facade

        # setup error handling
        self.communication.set_callback('error', lambda message: print("COMM. FEHLER GEMELDET: " + message))

        # replace with robot.run_robot()
        self.robot = Robot()
        self.robot.set_communication(self.communication)

        # setup odometry
        self.odometry = Odometry()
        self.odometry.set_communication(self.communication)

    def run(self):
        print("Controller started")

        # go!
        self.robot.run()


""" DEMO IMPLEMENTATION
# setup planet handling
communication.ready()
communication.set_callback('planet',
                           lambda planetName, startX, startY, startOrientation: print(
                               'got planet %s at %s/%s/%s' % (
                                   planetName, startX, startY, startOrientation)))
time.sleep(1)

# setup path handling
communication.path(0, 0, 90, 2, 4, 270, "free")
communication.set_callback('path', lambda startX, startY, startOrientation, endX, endY, endOrientation, pathStatus,
                                          pathWeight: print(
    'got path from %s/%s/%s to %s/%s/%s with status %s and weight %s' % (
        startX, startY, startOrientation, endX, endY, endOrientation, pathStatus, pathWeight)))
time.sleep(1)
"""

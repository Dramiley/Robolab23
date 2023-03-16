import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import time

from robot import Robot
from controller import simulator_log


class DummyMotor:
    count_per_rot = 100
    position = 0


class RobotDummy(Robot):
    """
    This class is a simulator for the robot.
    It is used to test the code without the robot.
    """

    controller = None
    __orientation = 0
    __position = (0, 0)

    motor_left = DummyMotor()
    motor_right = DummyMotor()

    was_path_blocked = False
    motor_pos_list = []
    # read map from file
    # read map name from planets/current_map.txt
    # get the current directory
    __current_dir = os.path.dirname(os.path.realpath(__file__))
    print("Current dir: " + __current_dir)

    with open(__current_dir + '/simulator/planets/current.txt') as __file:
        __file_name = __current_dir + '/simulator/planets/' + __file.read().strip() + '.json'

        # if file exists, read it
        if os.path.isfile(__file_name):
            with open(__file_name) as __json_file:
                __sim = json.load(__json_file)
                __map = __sim['startPosition']
                __position = __map['x'], __map['y']
                __orientation = __map['orientation']
                __map = __sim['paths']
        else:
            raise Exception("Map file " + __file_name + " does not exist")

    def __has_path_ahead(self):
        # can we drive into our current orientation?
        index_of_current_orientation = self.__orientation // 90

        # this is where we are
        path = self.__path()

        # output the path we are going to take
        new_path = path['paths'][index_of_current_orientation]

        # check if our path is valid
        return new_path is not None

    def getOrientation(self):
        return self.__orientation

    def drive_until_communication_point(self):
        print("Driving until communication point...")

        # can we drive into our current orientation?
        index_of_current_orientation = self.__orientation // 90

        # this is where we are
        path = self.__path()
        new_path = path['paths'][index_of_current_orientation]

        # check if our path is valid
        print("Taking new path: " + str(new_path))
        if new_path is None:
            simulator_log('communication.log', {'simulator.action': 'crash',
                                                'message': "You went off road. This map has no path in orientation " + str(
                                                    self.__orientation) + " at position " + str(self.__position),
                                                'color': 'error'})
            raise Exception("You went off road. This map has no path in orientation " + str(
                self.__orientation) + " at position " + str(self.__position))

        if "blocked" in new_path and new_path['blocked']:
            simulator_log('communication.log', {'message': "Path was blocked, turning around", 'color': 'warning'})
            self.was_path_blocked = True
            self.__orientation += 180
        else:
            self.was_path_blocked = False

            # update position
            self.__orientation = new_path['orientation']
            self.__position = new_path['x'], new_path['y']

        # log
        self.__log("Pos: " + str(self.__position) + " | " + str(self.__orientation) + "° | Path blocked: " + str(
            self.was_path_blocked))

        # tell the controller that we reached the communication point
        self.controller.communication_point_reached()

    def turn_deg(self, deg):
        # runde auf 90°
        deg = round(deg / 90) * 90

        # drehe um die angegebene Anzahl an Grad
        self.__orientation += deg

        # runde auf 360°
        self.__orientation %= 360

        # log
        self.__log("Turning " + str(deg) + "° | Orientation: " + str(self.__orientation))

    def station_scan(self) -> bool:
        # 1. rotate 90deg
        self.turn_deg(90)
        # 2. scan if there is something
        return self.__has_path_ahead()

    def set_controller(self, controller):
        self.controller = controller

    def __log(self, message=""):
        # print to console
        print("I think I am now at position " + str(self.__position) + " and my orientation is " + str(
            self.__orientation))
        print(message)

        # update visualisation
        self.__update_visualisation()

    def __update_visualisation(self):
        time.sleep(.3)
        simulator_log('position',
                      {'x': self.__position[0], 'y': self.__position[1], 'orientation': self.__orientation})

    def __path(self):
        # a path contains x and y coordinates
        # a path also contains an array paths

        for p in self.__map:
            if p['x'] == self.__position[0] and p['y'] == self.__position[1]:
                return p

        raise ("Path not found: " + str(self.__position))

    def __init__(self):
        # clean history file
        __current_dir = os.path.dirname(os.path.realpath(__file__))
        open(__current_dir + '/simulator/history.json', 'w').close()

        # inform user
        print("Using simulator robot ...")
        print("I think I am at position " + str(self.__position) + " and my orientation is " + str(self.__orientation))


def __del__(self):
    # wait for user to press any input
    time.sleep(1)


if __name__ == "__main__":
    r = RobotDummy()
    r.drive_until_communication_point()
    r.turn_deg(-90)
    r.drive_until_communication_point()
    r.turn_deg(180)
    r.drive_until_communication_point()
    r.drive_until_communication_point()
    r.turn_deg(180)
    r.drive_until_communication_point()
    r.turn_deg(90)
    r.drive_until_communication_point()
    r.turn_deg(-90)
    r.drive_until_communication_point()
    r.turn_deg(90)
    r.drive_until_communication_point()
    r.turn_deg(90)
    r.drive_until_communication_point()
    r.turn_deg(180)
    r.drive_until_communication_point()
    r.drive_until_communication_point()
    r.turn_deg(180)
    r.drive_until_communication_point()
    r.turn_deg(90)
    r.drive_until_communication_point()
    r.turn_deg(-90)
    r.drive_until_communication_point()
    r.drive_until_communication_point()

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import time

from robot import Robot


class DummyMotor:
    count_per_rot = 100
    position = 0


class RobotDummy(Robot):

    """
    This class is a dummy for the robot.
    It is used to test the code without the robot.
    """

    controller = None
    __orientation = 0
    __position = (0, 0)

    motor_left = DummyMotor()
    motor_right = DummyMotor()

    # read map from file
    with open('maps/Fassaden-M1.json') as __json_file:
        __map = json.load(__json_file)
        __position = __map['x'], __map['y']
        __orientation = __map['orientation']

    def __has_path_ahead(self):
        # can we drive into our current orientation?
        index_of_current_orientation = self.__orientation // 90

        # this is where we are
        path = self.__path_by_coordinates(self.__position, self.__map)

        # output the path we are going to take
        new_path = path['paths'][index_of_current_orientation]

        # check if our path is valid
        return new_path is not None

    def drive_until_communication_point(self):
        # can we drive into our current orientation?
        index_of_current_orientation = self.__orientation // 90

        # this is where we are
        path = self.__path_by_coordinates(self.__position, self.__map)

        # output the path we are going to take
        new_path = path['paths'][index_of_current_orientation]

        # check if our path is valid
        print("Taking new path: " + str(new_path))
        if new_path is None:
            raise Exception("Invalid path")
        elif new_path == -1 or new_path == -2:
            raise Exception("Path is not an object")

        # update position
        self.__orientation = new_path['orientation']
        self.__position = new_path['x'], new_path['y']

        # log
        self.__log("Position: " + str(self.__position) + " | Orientation: " + str(self.__orientation))

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
        print(message)

        # update visualisation
        self.__update_visualisation()

    def __update_visualisation(self):
        # write to file
        with open('dummy/position.json', 'w') as outfile:
            json.dump({'x': self.__position[0], 'y': self.__position[1], 'orientation': self.__orientation}, outfile)

        time.sleep(.5)

    def __path_by_coordinates(self, coordinates, path):
        # a path contains x and y coordinates
        # a path also contains an array paths

        if path is None or path == -1 or path == -2:
            return None

        if 'paths' not in path:
            return None

        if path['x'] == coordinates[0] and path['y'] == coordinates[1]:
            return path

        for p in path['paths']:
            result = self.__path_by_coordinates(coordinates, p)
            if result is not None:
                return result

    def __init__(self):
        print("Using dummy robot ...")


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

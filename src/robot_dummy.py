from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import time

"""
This is a dummy class for the robot.
The path is read from a json file.
"""

# start webserver via node
import os


class DummyMotor:
    count_per_rot = 100
    position = 0


class RobotDummy:
    controller = None
    orientation = 0
    position = (0, 0)

    motor_left = DummyMotor()
    motor_right = DummyMotor()

    # read map from file
    with open('maps/Fassaden-M1.json') as json_file:
        map = json.load(json_file)
        position = map['x'], map['y']
        orientation = map['orientation']

    def drive_until_communication_point(self):
        # can we drive into our current orientation?
        index_of_current_orientation = self.orientation // 90

        # this is where we are
        path = self.__path_by_coordinates(self.position, self.map)

        # output the path we are going to take
        new_path = path['paths'][index_of_current_orientation]

        # check if our path is valid
        print("Taking new path: " + str(new_path))
        if new_path is None:
            raise Exception("Invalid path")
        elif new_path == -1 or new_path == -2:
            raise Exception("Path is not an object")

        # update position
        self.orientation = new_path['orientation']
        self.position = new_path['x'], new_path['y']

        # log
        self.log("Position: " + str(self.position) + " | Orientation: " + str(self.orientation))

    def notify_at_communication_point(self):
        self.drive_until_communication_point()
        self.controller.communication_point_reached()

    def turn_deg(self, deg):
        # runde auf 90°
        deg = round(deg / 90) * 90

        # drehe um die angegebene Anzahl an Grad
        self.orientation += deg

        # runde auf 360°
        self.orientation %= 360

        # log
        self.log("Turning " + str(deg) + "° | Orientation: " + str(self.orientation))

    def set_controller(self, controller):
        self.controller = controller

    def log(self, message=""):
        # print to console
        print(message)

        # update visualisation
        self.__update_visualisation()

    def __update_visualisation(self):
        # write to file
        with open('dummy/position.json', 'w') as outfile:
            json.dump({'x': self.position[0], 'y': self.position[1], 'orientation': self.orientation}, outfile)

        # time.sleep(.3)

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

        """
        try:
            stream = os.system("cd dummy; node server.js &")
        except Exception as e:
            print("Server already on")

        # wait for user to press any input
        time.sleep(.7)
        """

    def __del__(self):

        # wait for user to press any input
        time.sleep(1)

        """
        # stop webserver via node
        try:
            stream = os.system("pkill node")
        except Exception as e:
            print("Server already off")
        """


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
"""
    # start robot
    r.drive_until_communication_point()
    r.turn_deg(-90)
    r.drive_until_communication_point()
    r.turn_deg(90)
    r.drive_until_communication_point()
    r.turn_deg(180)
    r.drive_until_communication_point()
    r.turn_deg(-90)
    r.drive_until_communication_point()
    r.turn_deg(-90)
    r.drive_until_communication_point()
    r.turn_deg(-90)
    r.drive_until_communication_point()
    r.turn_deg(90)
    r.drive_until_communication_point()
    r.drive_until_communication_point()

    r.turn_deg(90)
    r.drive_until_communication_point()
    r.turn_deg(90)
    r.drive_until_communication_point()
    r.turn_deg(-90)
    r.drive_until_communication_point()
    r.turn_deg(90)
    r.drive_until_communication_point()
    r.turn_deg(-90)
    r.drive_until_communication_point()
    r.turn_deg(90)
    r.drive_until_communication_point()
    r.turn_deg(180)
    r.drive_until_communication_point()
    r.turn_deg(90)
    r.drive_until_communication_point()
    r.drive_until_communication_point()
    r.drive_until_communication_point()
    r.turn_deg(180)
    r.drive_until_communication_point()
    r.drive_until_communication_point()
    r.drive_until_communication_point()
    r.turn_deg(-90)
    r.drive_until_communication_point()
    r.turn_deg(180)
    r.drive_until_communication_point()
    r.turn_deg(-90)
    r.drive_until_communication_point()
    r.turn_deg(90)
    r.drive_until_communication_point()
    r.turn_deg(-90)
    r.drive_until_communication_point()
    r.turn_deg(90)
    r.drive_until_communication_point()
    r.turn_deg(-90)
    r.drive_until_communication_point()
    r.turn_deg(180)
    r.drive_until_communication_point()
    r.drive_until_communication_point()
    r.turn_deg(90)
    r.drive_until_communication_point()
    r.turn_deg(180)
    r.drive_until_communication_point()
    r.turn_deg(-90)
    r.drive_until_communication_point()

    r.drive_until_communication_point()
    r.turn_deg(90)
    r.drive_until_communication_point()
    r.turn_deg(-90)
    r.drive_until_communication_point()
    r.turn_deg(180)
    r.drive_until_communication_point()

    r.drive_until_communication_point()
    r.drive_until_communication_point()
    r.turn_deg(90)
    r.drive_until_communication_point()
    r.turn_deg(90)
    r.drive_until_communication_point()
    r.turn_deg(180)
    r.drive_until_communication_point()
    r.turn_deg(-90)
    r.drive_until_communication_point()
    r.turn_deg(180)
    r.drive_until_communication_point()
    r.drive_until_communication_point()
    r.drive_until_communication_point()
    
"""

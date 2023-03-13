import json
import time


class RobotoDummy:
    controller = None
    orientation = 0
    position = (0, 0)

    # read map from file
    with open('maps/Kepler-0815.json') as json_file:
        map = json.load(json_file)

    def drive_until_start(self):
        self.position = self.map['x'], self.map['y']

        # log
        self.log("Start at: " + str(self.position) + " | Orientation: " + str(self.orientation))

    def drive_until_communication_point(self):
        # can we drive into our current orientation?
        index_of_current_orientation = self.orientation // 90

        # this is where we are
        path = self.__path_by_coordinates(self.position)

        # output the path we are going to take
        new_path = path['paths'][index_of_current_orientation]

        # check if our path is valid
        # print("Current path: " + json.dumps(path, indent=1))
        print("Taking new path: " + str(index_of_current_orientation))
        # print("New Path is: " + json.dumps(new_path, indent=1))
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
        print(message)

    def __path_by_coordinates(self, coordinates, path=None):
        if path is None:
            path = self.map

        # a path contains x and y coordinates
        # a path also contains an array paths

        if path == -2:
            return self.__path_by_coordinates(coordinates, self.map)

        if path is None or path == -1:
            return None

        if path['x'] == coordinates[0] and path['y'] == coordinates[1]:
            return path

        for p in path['paths']:
            result = self.__path_by_coordinates(coordinates, p)
            if result is not None:
                return result


if __name__ == "__main__":
    r = RobotoDummy()
    r.drive_until_start()
    r.drive_until_communication_point()
    r.drive_until_communication_point()
    r.turn_deg(90)
    r.drive_until_communication_point()

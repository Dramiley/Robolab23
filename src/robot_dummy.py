import json


class RobotoDummy:
    controller = None
    orientation = 0
    position = (0, 0)

    # read map from file
    with open('maps/Kepler-0815.json') as json_file:
        map = json.load(json_file)

    def drive_until_start(self):
        self.position = self.map['x'], self.map['y']

    def drive_until_communication_point(self):
        pass

    def notify_at_communication_point(self):
        pass

    def turn_deg(self, deg):
        # runde auf 90°
        deg = round(deg / 90) * 90

        # drehe um die angegebene Anzahl an Grad
        self.orientation += deg

        # runde auf 360°
        self.orientation %= 360

    def set_controller(self, controller):
        self.controller = controller


if __name__ == "__main__":
    RobotoDummy().drive_until_start()

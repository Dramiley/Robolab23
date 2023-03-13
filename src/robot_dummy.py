class RobotoDummy:
    controller = None
    orientation = 0
    current_map_path = []
    current_map = None

    def drive_until_start(self):
        pass

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

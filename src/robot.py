import ev3dev.ev3 as ev3
import time
import sys
import measurements as ms
from planet import Direction
from typing import List

from communication_facade import CommunicationFacade


class Robot:
    """
    Controls the robot's actions

    TODO: explore planet
        - add path etc
    TODO: implement decision making (go to target/search target)
    TODO: include communication into decision-making

    """

    communication: CommunicationFacade = None

    def __init__(self, left_port: str = "outB", right_port: str = "outD", start_dir: Direction = Direction.NORTH):
        self.motor_left = ev3.LargeMotor(left_port)
        self.motor_right = ev3.LargeMotor(right_port)

        self.current_dir = start_dir  # keeps track of robot's direction

        self.color = ms.ColorDetector()

    def move_motor(self, m):  # Vorwärts bewegen
        # m.run_timed(time_sp=100, speed_sp=50)
        m.speed_sp = 50
        m.commands = "run-forever"

    def moveBack(self, m):  # Rückwärts bewegen
        m.run_timed(time_sp=100, speed_sp=-50)

    def run(self):
        self.move_motor(self.motor_left)
        self.move_motor(self.motor_right)

    def stop(self):  # Stoppen
        self.motor_left.stop()
        self.motor_right.stop()

    def turn180(self):  # 180 Grad drehen
        self.motor_left.run_timed(time_sp=10000, speed_sp=72)

    def obstacleInWay(self):
        self.moveBackward(2)
        ev3.Sound.speak('Slow down! meteorite in sight')
        self.turn180()
        self.followline()

    def followline(self):  # folgt der Linie

        self.color.color_check()  # checkt die Farbe
        integral = 0
        lerror = 0
        tempo = 80
        starttime = time.time()
        self.motor_left.command = "run-forever"
        self.motor_right.command = "run-forever"
        while self.color.name == 'grey':
            self.color = ms.ColorDetector()
            self.color.color_check()
            greytone = self.color.greytone
            # if time.time() -  starttime >= 2:
            #    starttime = time.time()
            #    if ms.is_obstacle_ahead():
            #        self.obstacleInWay()
            REFERENCE_GREYTONE = 200
            error = greytone - REFERENCE_GREYTONE
            error = error / 2
            integral = integral + error
            if error < 10 and error > -10:
                # wenn genau zwischen den beiden Farben, setzt integral auf 0
                integral = 0
            derivative = error - lerror
            lenkfaktor = 60 * error + 10 * integral + 40 * derivative
            lenkfaktor = lenkfaktor / 100
            power1 = tempo + lenkfaktor
            power2 = tempo - lenkfaktor
            self.motor_left.speed_sp = int(power1)
            self.motor_left.command = "run-forever"
            self.motor_right.speed_sp = int(power2)
            self.motor_right.command = "run-forever"
            lerror = error
            self.color.color_check()
        self.stop()
        if input("Enter to continue") == "w":
            self.followline()

    def on_new_node(self) -> List[Direction]:
        """
        Actions to perform when an unknown node is entered:
            - check all 4 directions for paths and return for which directions there exist paths
            - (whether node is known or not is determined by odometry.py)

        For the Colorsensor to hit another path of the node, the robot has to be aligned accordingly
            - drive a little bit forward, turn, scan, drive backwards->scan next node
        """

        pass

    def move_distance_straight(self, d_cm: int):
        """
        Moves the robot d_cm [cm] on a straight line
        """
        pass

    def set_communication(self, communication: CommunicationFacade):
        self.communication = communication


def run_robot():
    robo = Robot()
    robo.followline()

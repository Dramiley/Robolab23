import ev3dev.ev3 as ev3
import time
import sys
import pdb
import logging
import measurements as ms
from typing import List

from planet import Direction
import math


class Robot:
    """
    Controls the robot's actions

    TODO: explore planet
        - add path etc
    TODO: implement decision making (go to target/search target)
    TODO: include communication into decision-making

    """


    def __init__(self, left_port: str = "outB", right_port: str = "outD", start_dir: Direction = Direction.NORTH,
                 stop=False, controller=None):

        # DEFS
        self.SPEED = 150 # speed of the motors, 150 is working

        self.controller = controller
        self.color: ms.ColorDetector = None
        self.obj_detec: ms.ObjectDetector = None
        self.middlegreytone = 170
        self.was_path_blocked = False  # stores whether last path driven was blocked or not->set when obstacle is detected
        self.motor_left = None
        self.motor_right = None
        self.motor_pos_list = None

        self.motor_left = ev3.LargeMotor(left_port)
        self.motor_right = ev3.LargeMotor(right_port)

        self.motor_pos_list = []

        if stop:
            self.stop()
            sys.exit(0)

        self.current_dir = start_dir  # keeps track of robot's direction

        try:
            self.color = ms.ColorDetector(self.controller)
        except Exception as e:
            print("Could not initialize color sensors wrapper ")
            print(e)

        try:
            self.obj_detec = ms.ObjectDetector()
        except Exception as e:
            print("Could not initialize object detector sensors wrapper")
            print(e)

    def __track_motor_pos(self):
        """
        Tracks motor positions of the motors in a list of tuples
        """
        motor_pos_left = self.motor_left.position
        motor_pos_right = self.motor_right.position
        self.motor_pos_list.append([motor_pos_left, motor_pos_right])

    def __reset_motor_pos_list(self):
        # init with current pos list
        motor_left_pos0 = self.motor_left.position
        motor_right_pos0 = self.motor_right.position
        self.motor_pos_list = [(motor_left_pos0, motor_right_pos0)]

    def __move_time(self, t, s):  # Rückwärts bewegen
        self.motor_left.run_timed(time_sp=t, speed_sp=s)
        self.motor_right.run_timed(time_sp=t, speed_sp=s)

    def __drive(self, speedleft, speedright):

        self.motor_left.speed_sp = speedleft
        self.motor_left.command = "run-forever"
        self.motor_right.speed_sp = speedright
        self.motor_right.command = "run-forever"

    def stop(self):  # Stoppen
        self.motor_left.stop()
        self.motor_right.stop()

    def scan_turn(self):
        starttime = time.time()
        self.motor_left.run_timed(time_sp=1400, speed_sp=131)
        self.motor_right.run_timed(time_sp=1400, speed_sp=-131)

        while self.color.subname != 'black' and time.time() - starttime <= 2:
            self.color.color_check()
        self.stop()

    def __speak(self, text):
        try:
            ev3.Sound.speak(text).wait()
        except Exception as e:
            print("Could not speak")
            print(e)

    def calibrate(self):

        # if the current hour is later than 22:00 or earlier than 6:00, do not calibrate
        if 22 <= time.localtime().tm_hour <= 23 or 0 <= time.localtime().tm_hour <= 6:
            self.__speak("Calibration not necessary at this time")
            self.middlegreytone = 170
            self.__move_distance_straight(4)
            return

        self.__speak("Calibration")
        self.color.color_check()
        white = self.color.greytone
        self.__move_distance_straight(4)
        self.color.color_check()
        black = self.color.greytone
        middlegreytone = ((white + black) / 2) + 10  # 50
        self.middlegreytone = middlegreytone

    def __obstacle_in_way(self):
        self.stop()
        self.__move_time(500, -100)
        time.sleep(1)
        # play notes a, c, e, g, a, c, e, g
        ev3.Sound.tone([(100, 200, 800)] * 2).wait()

        self.was_path_blocked = True

        self.turn_deg(175)

    def __followline(self):
        # folgt der Linie
        # self.communication.test_planet("Gromit")
        # reset was_path_blocked
        print("followline")
        self.was_path_blocked = False

        self.color.color_check()  # checkt die Farbe
        middle_greytone = self.middlegreytone
        integral = 0
        lerror = 0
        tempo = self.SPEED
        de = 0.80 * tempo
        di = 0.05 * tempo
        dd = 0.60 * tempo
        starttime = time.time()

        self.__reset_motor_pos_list()

        while self.color.name == 'grey':

            # if the integral is greater than 100, stop the robot
            if integral > 5000:
                # for the next 5 seconds, call every second the stop function
                for i in range(5):
                    self.stop()
                    time.sleep(1)
                # play three error beeps
                ev3.Sound.tone([(1000, 500, 100)]).wait()
                break

            self.color.color_check()
            greytone = self.color.greytone
            if time.time() - starttime >= 1:
                starttime = time.time()
                if self.obj_detec.is_obstacle_ahead():
                    self.__obstacle_in_way()
                    # self.motor_left.command = "run-forever"
                    # self.motor_right.command = "run-forever"
            # MIDDLEGREYTONE = 200
            error = greytone - middle_greytone
            error = error / 2
            integral = integral + error
            if error < 10 and error > -10:
                # wenn genau zwischen den beiden Farben, setzt integral auf 0
                integral = 0

            derivative = error - lerror
            lenkfaktor = de * error + di * integral + dd * derivative
            lenkfaktor = lenkfaktor / 100
            power_left = tempo + lenkfaktor
            power_right = tempo - lenkfaktor

            self.__run_motors(power_left, power_right)
            self.__track_motor_pos()

            lerror = error
            self.color.color_check()
        self.stop()

    def __run_motors(self, power_left: float, power_right: float):
        """
        Starts the motor
        """
        self.motor_left.speed_sp = int(power_left)
        self.motor_left.command = "run-forever"
        self.motor_right.speed_sp = int(power_right)
        self.motor_right.command = "run-forever"

    def __station_center(self):
        """
        Center the robot on the station
        """

        self.motor_left.run_timed(time_sp=800, speed_sp=60)
        time.sleep(0.8)
        self.motor_left.run_timed(time_sp=312, speed_sp=65)
        self.motor_right.run_timed(time_sp=312, speed_sp=-65)
        time.sleep(0.5)
        self.__move_distance_straight(4.4)
        time.sleep(1)

    def station_scan(self) -> bool:
        """
        1. rotate 90deg
        2. scan if there is something

        Returns:
            True if there was black line
        """
        self.color.color_check()
        while self.color.subname != 'white':
            # rotating until not on path anymore
            self.__drive(131, -131)
            self.color.color_check()
        self.stop()
        self.scan_turn()
        if self.color.subname == 'black':
            return True
        else:
            return False

    def __move_distance_straight(self, d_cm: int):
        """
        Moves the robot d_cm [cm] on a straight line#
        """
        self.__move_time(1000, d_cm * 20)
        time.sleep(1)

    def set_controller(self, controller):
        self.controller = controller

    def skip_calibrate(self):
        self.middlegreytone = 175
        self.black = 37
        self.white = 297

    def begin(self):
        self.__followline()
        self.__station_center()

    def turn_deg(self, deg):
        """
        Turns the robot by param degrees
        """
        ROT_TIME_FACTOR = 13.88
        rot_dir = math.copysign(1, deg)
        speed = rot_dir * 133
        # so time isnt negative
        deg = abs(deg)
        self.motor_left.run_timed(time_sp=ROT_TIME_FACTOR * deg, speed_sp=speed)
        self.motor_right.run_timed(time_sp=ROT_TIME_FACTOR * deg, speed_sp=-speed)
        time.sleep(ROT_TIME_FACTOR * 10 ** -3 * deg)

    def drive_until_communication_point(self):
        """
        Drives the robot to the next communication point
        """
        self.__followline()
        self.__station_center()
        # tell the controller that we reached the communication point
        self.controller.communication_point_reached()

    def deadly_stop(self):
        while True:
            self.stop()
            time.sleep(0.1)

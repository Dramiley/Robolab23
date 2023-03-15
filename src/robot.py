import ev3dev.ev3 as ev3
import time
import sys
import measurements as ms
from typing import List

from planet import Direction


class Robot:
    """
    Controls the robot's actions

    TODO: explore planet
        - add path etc
    TODO: implement decision making (go to target/search target)
    TODO: include communication into decision-making

    """

    controller = None
    color: ms.ColorDetector = None
    obj_detec: ms.ObjectDetector = None
    middlegreytone = 200
    path_was_blocked = False # stores whether last path driven was blocked or not->set when obstacle is detected

    motor_left = None
    motor_right = None

    def __init__(self, left_port: str = "outB", right_port: str = "outD", start_dir: Direction = Direction.NORTH):

        self.motor_left = ev3.LargeMotor(left_port)
        self.motor_right = ev3.LargeMotor(right_port)
        self.current_dir = start_dir  # keeps track of robot's direction

        try:
            self.color = ms.ColorDetector()
            print("Color Okay")
        except Exception as e:
            print("Could not initialize color sensors wrapper ")
            print(e)

        try:
            self.obj_detec = ms.ObjectDetector()
            print("Object Detector Okay")
        except Exception as e:
            print("Could not initialize object detector sensors wrapper")
            print(e)

    def __move_time(self, t, s):  # Rückwärts bewegen
        self.motor_left.run_timed(time_sp=t, speed_sp=s)
        self.motor_right.run_timed(time_sp=t, speed_sp=s)

    def __drive(self, speedleft, speedright):

        self.motor_left.speed_sp = speedleft
        self.motor_left.command = "run-forever"
        self.motor_right.speed_sp = speedright
        self.motor_right.command = "run-forever"

    def __stop(self):  # Stoppen
        self.motor_left.stop()
        self.motor_right.stop()

    def __turn170(self):  # 180 Grad drehen
        self.motor_left.run_timed(time_sp=2500, speed_sp=120)
        self.motor_right.run_timed(time_sp=2500, speed_sp=-120)
        time.sleep(2.5)

    def __turn180(self):  # 180 Grad drehen
        self.motor_left.run_timed(time_sp=2500, speed_sp=131)
        self.motor_right.run_timed(time_sp=2500, speed_sp=-131)
        time.sleep(2.5)

    def __turn90(self):
        self.motor_left.run_timed(time_sp=1250, speed_sp=131)
        self.motor_right.run_timed(time_sp=1250, speed_sp=-131)
        time.sleep(1.5)

    def __scan_turn(self):
        self.motor_left.run_timed(time_sp=1250, speed_sp=131)
        self.motor_right.run_timed(time_sp=1250, speed_sp=-131)

        while self.color.subname != 'black' and time.time() - starttime <= 2:
            self.color.color_check()
        self.__stop()

        starttime = time.time()

    def __speak(self, text):
        try:
            ev3.Sound.speak(text).wait()
        except Exception as e:
            print("Could not speak")
            print(e)

    def __calibrate(self):
        self.__speak("Calibration started")
        self.__speak('White')
        time.sleep(5)
        self.color.color_check()
        white = self.color.greytone
        print("white = " + str(white))
        self.__speak('Black')
        time.sleep(5)
        self.color.color_check()
        black = self.color.greytone
        print("black = " + str(black))
        middlegreytone = ((white + black) / 2) + 55
        print("grey = " + str(middlegreytone))
        self.middlegreytone = middlegreytone

    def __obstacle_in_way(self):
        self.__stop()
        self.__move_time(500, -100)
        time.sleep(1)
        self.__speak('Meteroit spotted')

        self.path_was_blocked = True

        self.__turn170()
        self.__followline()

    def __followline(self):  # folgt der Linie
        # self.communication.test_planet("Gromit")
        self.color.color_check()  # checkt die Farbe
        middle_greytone = self.middlegreytone
        integral = 0
        lerror = 0
        tempo = 80
        starttime = time.time()

        while self.color.name == 'grey':
            self.color.color_check()
            greytone = self.color.greytone
            if time.time() - starttime >= 3:
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
            lenkfaktor = 60 * error + 10 * integral + 40 * derivative
            lenkfaktor = lenkfaktor / 100
            power_left = tempo + lenkfaktor
            power_right = tempo - lenkfaktor

            self.__run_motors(power_left, power_right)

            lerror = error
            self.color.color_check()
        self.__stop()

    def __run_motors(self, power_left: int, power_right: int):
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

        self.motor_left.run_timed(time_sp=500, speed_sp=60)
        time.sleep(0.5)
        self.motor_left.run_timed(time_sp=312, speed_sp=65)
        self.motor_right.run_timed(time_sp=312, speed_sp=-65)
        time.sleep(0.5)
        self.__move_distance_straight(5)
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

        self.__stop()

        # scan 90 deg (to the robot's right
        self.__scan_turn()

        # check whether there was something black within the 90deg turn
        if self.color.subname == 'black':
            return True
        else:
            return False

    def __move_distance_straight(self, d_cm: int):
        """
        Moves the robot d_cm [cm] on a straight line#
        """
        self.__move_time(1000, int(d_cm * 20))
        time.sleep(1)

    def set_controller(self, controller):
        self.controller = controller

    def __run(self):
        self.__calibrate()
        # while True:
        #      print("1 for followline")
        #      print("2 for station_center")
        #      print("3 for turn180")
        #      print("4 for quit")
        #      print("5 for station_scan")
        #      print("6 for turn90")
        #      print("7 for station_scan2")
        #      i = input()
        #      if i == "1":
        #          self.__followline()
        #      elif i == "2":
        #          self.__station_center()
        #      elif i == "3":
        #          self.__turn180()
        #      elif i == "4":
        #          break
        #      elif i == "5":
        #          t = int(input("Wie oft drehen?\n"))
        #          print(self.__station_scan(t))
        #      elif i == "6":
        #          self.__turn90()
        #      elif i == "7":
        #          print(self.__station_scan_alternative())

    def drive_until_communication_point(self):
        """
        Drives the robot to the next communication point
        """
        self.path_was_blocked = False # reset
        self.__followline()
        # center on station
        self.__station_center()

        # tell the controller that we reached the communication point
        self.controller.communication_point_reached()

    def turn_deg(self, deg):
        """
        Turns the robot by param degrees
        """
        self.motor_left.run_timed(time_sp=1250, speed_sp=133)
        self.motor_right.run_timed(time_sp=1250, speed_sp=-133)
        time.sleep(1.25 / 90 * (deg % 360))
        self.stop()

    def __has_path_ahead(self):
        """
        Returns true if the robot has a path ahead
        """
        # TODO: think about replacing station_scan with this method
        # raise NotImplementedError("That's bad news man")

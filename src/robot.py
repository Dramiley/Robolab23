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
    color: ms.ColorDetector = None
    obj_detec: ms.ObjectDetector = None
    MIDDLEGREYTONE = 200

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

    def move_time(self, t,s):  # Rückwärts bewegen
        self.motor_left.run_timed(time_sp=t, speed_sp=s)
        self.motor_right.run_timed(time_sp=t, speed_sp=s)

    def drive(self):
        
        self.motor_left.speed_sp = 80
        self.motor_left.command = "run-forever"
        self.motor_right.speed_sp = 80
        self.motor_right.command = "run-forever"
        

    def stop(self):  # Stoppen
        self.motor_left.stop()
        self.motor_right.stop()

    def turn170(self):  # 180 Grad drehen
        self.motor_left.run_timed(time_sp=2500, speed_sp=120)
        self.motor_right.run_timed(time_sp=2500, speed_sp=-120)
        time.sleep(2.5)

    def turn180(self):  # 180 Grad drehen
        self.motor_left.run_timed(time_sp=2500, speed_sp=133)
        self.motor_right.run_timed(time_sp=2500, speed_sp=-133)#
        time.sleep(2.5)
    
    def turn90(self):
        self.motor_left.run_timed(time_sp=1250, speed_sp=133)
        self.motor_right.run_timed(time_sp=1250, speed_sp=-133)
        time.sleep(1.25)
        
    def calibrate(self):
        ev3.Sound.speak('Calibration starting').wait()
        ev3.Sound.speak('White').wait()
        time.sleep(5)
        self.color.color_check()
        white = self.color.greytone
        print("white = " + str(white))
        ev3.Sound.speak('Black').wait()
        time.sleep(5)
        self.color.color_check()
        black = self.color.greytone
        print("black = " + str(black))
        MIDDLEGREYTONE = ((white + black) / 2) + 55
        print("grey = " + str(MIDDLEGREYTONE))
        self.MIDDLEGREYTONE = MIDDLEGREYTONE
    
    def obstacleInWay(self, MIDDLEGREYTONE):
        self.stop()
        self.move_time(500, -100)
        time.sleep(1)
        ev3.Sound.speak('Meteroit spotted').wait()
        self.turn170()
        self.followline(MIDDLEGREYTONE)

    def followline(self):  # folgt der Linie
        #self.communication.test_planet("Gromit")
        self.color.color_check()  # checkt die Farbe
        MIDDLEGREYTONE = self.MIDDLEGREYTONE
        integral = 0
        lerror = 0
        tempo = 80
        starttime = time.time()
        self.motor_left.command = "run-forever"
        self.motor_right.command = "run-forever"
        while self.color.name == 'grey':
            self.color.color_check()
            greytone = self.color.greytone
            if time.time() -  starttime >= 3:
                starttime = time.time()
                if self.obj_detec.is_obstacle_ahead():
                    self.obstacleInWay(MIDDLEGREYTONE)
                    self.motor_left.command = "run-forever"
                    self.motor_right.command = "run-forever"
            # MIDDLEGREYTONE = 200
            error = greytone - MIDDLEGREYTONE
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
        #self.communication.ready()

    def station_scan(self, turns):
        self.move_distance_straight(7)
        backturns = 4 - turns
        while turns > 0:
            self.turn90() 
            turns = turns - 1 
        self.color.color_check()
        while (backturns) > 0:
            self.turn90()
            backturns = backturns - 1
        self.move_distance_straight(-7)
        if self.color.subname == 'black':
            return True
        else: return False
        
        
    
        
        
        
        
            
        
            
        
    
    
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
        Moves the robot d_cm [cm] on a straight line#
        """
        self.move_time(1000, d_cm*20)
        time.sleep(1)

    def set_communication(self, communication: CommunicationFacade):
        self.communication = communication

    def run(self):
        self.calibrate()
        while True:
            print("1 for followline")
            print("2 for station_scan")
            print("3 for turn180")
            print("4 for quit")
            print("5 for station_scan")
            print("6 for turn90")
            i = input() 
            if i == "1":
                self.followline()
            elif i == "2":
                self.station_scan()
            elif i == "3":
                self.turn180()
            elif i == "4":
                sys.exit()
            elif i == "5":
                t = int(input("Wie oft drehen?\n"))
                print(self.station_scan(t))
            elif i == "6":
                self.turn90()

    def drive_until_start(self):
        """
        Drives the robot until it reaches the start node
        """
        self.run()
        #self.followline()
            
        pass

    def explore(self, planetName, startX, startY, startOrientation):
        """
        Explores the planet
        @param planetName: name of the planet
        @param startX: x-coordinate of the start node
        @param startY: y-coordinate of the start node
        @param startOrientation: orientation of the start node
        """
        pass

    def drive_to_next_communication_point(self):
        """
        Drives the robot to the next communication point
        """
        self.followline()
        pass

    def drive_to(self, x, y):
        """
        Drives the robot to the node at (x,y)
        """
        pass
import ev3dev.ev3 as ev3
import time
import sys
import measurements as ms

class Robot:
    """
    Controls the robot's actions

    TODO: explore planet
        - add path etc
    TODO: implement decision making (go to target/search target)
    TODO: include communication into decision-making

    """

    def __init__(self, left_port: str="outB", right_port: str="outD"):
        self.motor_left = ev3.LargeMotor(left_port)
        self.motor_right = ev3.LargeMotor(right_port)

    def move_motor(self, m): # Vorwärts bewegen
        # m.run_timed(time_sp=100, speed_sp=50)
        m.speed_sp = 50
        m.commands = "run-forever"

    def moveBack(self, m): # Rückwärts bewegen
        m.run_timed(time_sp=100, speed_sp=-50)

    def steer(self, m, speed): # Lenken
        m.run_timed(time_sp=100, speed_sp=speed)

    def moveForward(self, dur): # Vorwärts fahren

        while dur > 0:
            self.move_motor(self.motor_left)
            self.move_motor(self.motor_right)
            dur = dur - 1

    def run(self):
        self.move_motor(self.motor_left)
        self.move_motor(self.motor_right)

    def stop(self): # Stoppen
        self.motor_left.stop()
        self.motor_right.stop()

    def moveBackward(self, dur): # Rückwärts fahren
        self.stop()
        while dur > 0:
            self.moveBack(self.motor_left)
            self.moveBack(self.motor_right)
            dur = dur - 1

    def turnRight(self, dur): # Rechts drehen
        while dur > 0:
            self.steer(self.motor_left, 100)
            self.steer(self.motor_right, -90)
            dur = dur - 1
        self.run()

    def turnLeft(self, dur):  # Links drehen
        while dur > 0:
            self.steer(self.motor_right, 100)
            self.steer(self.motor_left, -90)
            dur = dur - 1
        self.run()


    def turn180(self): # 180 Grad drehen
        self.motor_left.run_timed(time_sp=10000, speed_sp=72)

    def obstacleInWay(self):
        self.moveBackward(2)
        ev3.Sound.speak('Slow down! meteorite in sight')
        self.turn180()
        self.followline()

    def followline(self): # folgt der Linie
        color = ms.ColorDetector()
        color.color_check() # checkt die Farbe
        integral = 0
        lerror = 0
        tempo = 50
        starttime = time.time()
        self.motor_left.command = "run-forever"
        self.motor_right.command = "run-forever"
        while color.name == 'grey':
            color = ms.ColorDetector()
            color.color_check()
            greytone = color.greytone
            if time.time() -  starttime >= 2:
                starttime = time.time()
                if ms.is_obstacle_ahead():
                    self.obstacleInWay()
            error = greytone - 200
            integal = integral + error
            if error == 0:
                integral = 0
            deveriate = error - lerror
            Lenkfaktor = 10*error + integral + 2*deveriate
            Lenkfaktor = Lenkfaktor / 100
            power1 = tempo + Lenkfaktor
            power2 = tempo - Lenkfaktor
            self.motor_left.speed_sp = int(power1)
            self.motor_left.command = "run-forever"
            self.motor_right.speed_sp = int(power2)
            self.motor_right.command = "run-forever"
            lerror = error
            color.color_check()
        self.stop()

def run_robot():
    robo = Robot()
    robo.followline()
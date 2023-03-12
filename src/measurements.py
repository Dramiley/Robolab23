import ev3dev.ev3 as ev3

class ColorDetector:
    def __init__(self):
        self.name = ''
        self.greytone = 0

        self.cs = ev3.ColorSensor()

    def color_check(self):
        self.cs.mode = 'RGB-RAW'

        if self.cs.red > 120 and self.cs.blue < 80 and self.cs.green < 80:
            self.name = 'red'
            print(self.name)
        elif self.cs.red < 60 and self.cs.blue > 100 and self.cs.green > 100:
            self.name = 'blue'
        else:
            self.name = 'grey'
            self.greytone = (self.cs.red + self.cs.blue + self.cs.green) // 3


class ObstacleDetector:

    def __init__(self) -> bool:
        self.us = ev3.UltrasonicSensor()
        self.distance = 20 # distance from which on obstacles are being detected

    def is_obstacle_ahead(self):
        '''
        returns true if ultrasonic sensor dects an obstacle within next x (20??) c,
        - should be checked periodically by calling function (if robot has moved since last measurement)
        '''
        self.us.mode = 'US-SI-CM' # compare to continous measurement 'US-DIST-CM'

        # report true if dist<20
        # make sure to take mean value in dt bc values fluctuate
        dist = self.us.distance_centimeters# gets value
        if dist < self.distance:
            return True
        else:
            return False
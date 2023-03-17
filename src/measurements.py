import ev3dev.ev3 as ev3


class ColorDetector:
    def __init__(self):
        self.name = ''
        self.greytone = 0
        self.subname = ''

        try:
            self.cs = ev3.ColorSensor()
            self.us = ev3.UltrasonicSensor()
        except Exception as e:
            print(e)

    def color_check(self):
        try:
            self.cs.mode = 'RGB-RAW'

            if self.cs.red > 120 and self.cs.blue < 80 and self.cs.green < 80:
                self.name = 'red'
                self.subname = 'red'
                # print(self.name)
            elif self.cs.red < 60 and self.cs.blue > 100 and self.cs.green > 90:
                self.name = 'blue'
                self.subname = 'blue'
            else:
                self.name = 'grey'
                self.greytone = (self.cs.red + self.cs.blue + self.cs.green) // 3
                if self.greytone < 100:
                    self.subname = 'black'
                elif self.greytone > 230:
                    self.subname = 'white'
                elif self.greytone > 100 and self.greytone < 230:
                    self.subname = 'grey'
        except Exception as e:
            print("Could not initialize color sensors: {e}")


class ObjectDetector:
    def __init__(self):
        self.us = ev3.UltrasonicSensor()
        self.us.mode = 'US-SI-CM'  # compare to continous measurement 'US-DIST-CM'

    def is_obstacle_ahead(self):
        '''
        returns true if ultrasonic sensor dects an obstacle within next x (20??) c,
        - should be checked periodically by calling function (if robot has moved since last measurement)
        '''
        # report true if dist<20
        # make sure to take mean value in dt bc values fluctuate
        dist = self.us.distance_centimeters  # gets value
        if dist < 20:
            return True
        else:
            return False

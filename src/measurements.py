import ev3dev.ev3 as ev3

class ColorDetector:
    def __init__(self):
        self.name = ''
        self.greytone = 0
        
        
    def color_check(self):
        cs = ev3.ColorSensor()
        cs.mode = 'RGB-RAW'
        greytone = 0

        if cs.red > 120 and cs.blue < 80 and cs.green < 80:
            self.name = 'red'
            print(self.name)
        elif cs.red < 60 and cs.blue < 100 and cs.green > 100:
            self.name = 'blue'
        elif cs.red-cs.blue < 50 and cs.red-cs.green < 50 and cs.blue-cs.green < 50:
            self.name = 'grey'
            self.greytone = cs.red + cs.blue + cs.green // 3
        else:
            self.name = 'other'

def is_obstacle_ahead():
    '''
    returns true if ultrasonic sensor dects an obstacle within next x (20??) c,
    - should be checked periodically by calling function (if robot has moved since last measurement)
    '''
    us = ev3.UltrasonicSensor()
    us.mode = 'US-SI-CM' # compare to continous measurement 'US-DIST-CM'

    # report true if dist<20
    # make sure to take mean value in dt bc values fluctuate
    dist = us.distance_centimeters# gets value
    if dist < 20:
        return True
    else:
        return False
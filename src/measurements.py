import ev3dev.ev3 as ev3

def color_check():
    cs = ev3.ColorSensor()
    cs.mode = 'RGB-RAW'
    # cs.bin_data("hhh")

    if cs.red > 120 and cs.blue < 80 and cs.green < 80:
        return 'red'
    elif cs.red < 60 and cs.blue < 60 and cs.green <80:
        return 'black'
    elif cs.red > 180 and cs.blue > 180 and cs.green > 180:
        return 'white'
    elif cs.red < 50 and cs.blue < 100 and cs.green > 110:
        return 'blue'
    elif cs.red <  230 and cs.blue < 230 and cs.green < 230 and cs.red > 80 and cs.blue > 80 and cs.green > 80:
        return 'grey'
    else:
        return 'other'

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
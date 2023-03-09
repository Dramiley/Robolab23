import ev3dev.ev3 as ev3

def color_check():
    cs = ev3.ColorSensor()
    cs.mode = 'RGB-RAW'
    # cs.bin_data("hhh")

    if cs.red > 120 and cs.blue < 80 and cs.green < 80:
        print('red')
    elif cs.red < 80 and cs.blue < 80 and cs.green <80:
        print('black')
    elif cs.red > 160 and cs.blue > 150 and cs.green > 200:
        print('white')
    elif cs.red < 50 and cs.blue < 100 and cs.green > 110:
        print('blue')
    else:
        print('I dont know')

def is_obstacle_ahead():
    '''
    returns true if ultrasonic sensor dects an obstacle within next x (20??) c,
    - should be checked periodically by calling function (if robot has moved since last measurement)
    '''
    us = ev3.UltrasonicSensor()
    us.mode = 'US-SI-CM' # compare to continous measurement 'US-DIST-CM'

    # report true if dist<20
    # make sure to take mean value in dt bc values fluctuate
    dist = us.distance_centimeters # gets value
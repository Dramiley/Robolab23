import ev3dev.ev3 as ev3
import time
import sys
import measurements as ms

motor_left = ev3.LargeMotor("outB")
motor_right = ev3.LargeMotor("outD")

def move(m):
    m.run_timed(time_sp=1000, speed_sp=170)

def moveBack(m):
    m.run_timed(time_sp=1000, speed_sp=-170)
    
def steer(m):
    m.run_timed(time_sp=1000, speed_sp=60)



def moveForward(dur):
    
    while dur > 0:
        move(motor_left)
        move(motor_right)
        dur = dur - 1
        time.sleep(1)
   
def moveBackward(dur):
    while dur > 0:
        moveBack(motor_left)
        moveBack(motor_right)
        dur = dur - 1
        time.sleep(1)
    
def turnRight(dur): # Rechts drehen
    while dur > 0:
        steer(motor_left)
        dur = dur - 1
        time.sleep(1)

def turnLeft(dur):  # Links drehen
    while dur > 0:
        steer(motor_right)
        dur = dur - 1
        time.sleep(1)
        
def turn180(): # 180 Grad drehen
    turnRight(12)
   
def followline(): # folgt der Linie
    color = ms.color_check() # checkt die Farbe
    print(color)
    while color == 'black':
        moveForward(1)
        color = ms.color_check()
        if ms.is_obstacle_ahead(): # weicht aus
            obstacleInWay()
        if color == 'white':
            findLine() # sucht die Linie wieder
        elif color == 'blue':
            print("Blue Planet found")
        elif color == 'red':
            print("Red Planet found")
        else:
            print(color)

def findLine():
    turnRight(1)	
    color = ms.color_check()
    if color == 'black':
        followline()
    else: 
        findLine()
        
def obstacleInWay():
    moveBackward(2)
    turn180()
    followline()
        
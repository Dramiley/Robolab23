import ev3dev.ev3 as ev3
import time
import sys
import measurements as ms

motor_left = ev3.LargeMotor("outB")
motor_right = ev3.LargeMotor("outD")

def move(m):
    m.run_timed(time_sp=1000, speed_sp=300)

def moveBack(m):
    m.run_timed(time_sp=1000, speed_sp=-300)
    
def steer(m):
    m.run_timed(time_sp=1000, speed_sp=200)



def moveForward(dur):
    
    while dur > 0:
        move(motor_left)
        move(motor_right)
        dur = dur - 1
        
   
def moveBackward(dur):
    while dur > 0:
        moveBack(motor_left)
        moveBack(motor_right)
        dur = dur - 1
        
    
def turnRight(dur): # Rechts drehen
    while dur > 0:
        steer(motor_left)
        dur = dur - 1
        

def turnLeft(dur):  # Links drehen
    while dur > 0:
        steer(motor_right)
        dur = dur - 1
        
        
def turn180(): # 180 Grad drehen
    turnRight(12)
    
def turn90(): # 90 Grad drehen
    turnRight(6)
   
def findRight():
    turnRight(1)	
    color = ms.color_check()
    while color == 'white':
        turnRight(1)
        color = ms.color_check()
    if color != 'white':
        followline()
    
    

def findLeft():
    turnLeft(1)
    color = ms.color_check()
    while color == 'black':
        turnLeft(1)
        color = ms.color_check()
    if color != 'black':
        followline()
    
        
def obstacleInWay():
    moveBackward(2)
    ev3.Sound.speak('Slow down! meteorite in sight')
    turn180()
    followline()

def followline(): # folgt der Linie
    color = ms.color_check() # checkt die Farbe
    print(color)
    if color == 'white':
        findRight()
    elif color == 'black':
        findLeft()
    while color == 'grey':
        moveForward(1)
        turnLeft(1)
        color = ms.color_check()
        if ms.is_obstacle_ahead(): # weicht aus
            obstacleInWay()
        if color == 'white':
            findRight() # sucht die Linie wieder
        elif color == 'black':
            findLeft()
        elif color == 'blue':
            print("Blue Planet found")
            break
        elif color == 'red':
            print("Red Planet found")
            break
        elif color == 'other':
            print(color)
            

        
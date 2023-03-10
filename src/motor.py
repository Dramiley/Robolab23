import ev3dev.ev3 as ev3
import time
import sys
import measurements as ms

# Motoren initialisieren
motor_left = ev3.LargeMotor("outB")
motor_right = ev3.LargeMotor("outD")

def move(m): # Vorwärts bewegen
    # m.run_timed(time_sp=100, speed_sp=50)
    m.speed_sp = 50
    m.command = "run-forever"

def moveBack(m): # Rückwärts bewegen
    m.run_timed(time_sp=100, speed_sp=-50)
    
def steer(m, speed): # Lenken
    m.run_timed(time_sp=100, speed_sp=speed)




#def moveForward(dur): # Vorwärts fahren
#    
#    while dur > 0:
#        move(motor_left)
#        move(motor_right)
#        dur = dur - 1
        
def run():
    move(motor_left)
    move(motor_right)

def moveBackward(dur): # Rückwärts fahren
    while dur > 0:
        moveBack(motor_left)
        moveBack(motor_right)
        dur = dur - 1
        
    
def turnRight(dur): # Rechts drehen
    while dur > 0:
        steer(motor_left, 50)
        steer(motor_right, -20)
        dur = dur - 1
        

def turnLeft(dur):  # Links drehen
    while dur > 0:
        steer(motor_right, 50)
        steer(motor_left, -20)
        dur = dur - 1
        
        
def turn180(): # 180 Grad drehen
    turnRight(12)
    
def turn90(): # 90 Grad drehen
    turnRight(6)
    
        
def obstacleInWay():
    moveBackward(2)
    ev3.Sound.speak('Slow down! meteorite in sight')
    turn180()
    followline()
    
#def findRight():
#    if ms.is_obstacle_ahead(): # weicht aus
#            obstacleInWay()
#    turnRight(16)	
#    color = ms.ColorDetector()
#    color.color_check()
#    while color.name == 'white':
#        turnRight(16)
#        color = ms.ColorDetector()
#        color.color_check()
#    if color.name != 'white':
#        followline()
    

#def findLeft():
#    if ms.is_obstacle_ahead(): # weicht aus
#            obstacleInWay()
#    turnLeft(16)
#    color = ms.ColorDetector()
#    color.color_check()
#    while color == 'black':
#        turnLeft(16)
#        color = ms.ColorDetector()
#        color.color_check()
#    if color != 'black':
#       followline()

def followline(): # folgt der Linie
    run()
    color = ms.ColorDetector()
    color.color_check() # checkt die Farbe
    greytone = color.greytone 
    if greytone < -2:
            turnLeft(abs(greytone))
    if greytone > 2:
            turnRight(abs(greytone))
    #if color.name == 'white':
    #    findRight()
    #elif color.name == 'black':
    #    findLeft()
    while color.name == 'grey':
        color = ms.ColorDetector()
        color.color_check()
        greytone = color.greytone
        if ms.is_obstacle_ahead(): # weicht aus
            obstacleInWay()
        #if color.name == 'white':
        #    findRight() # sucht die Linie wieder
        #elif color.name == 'black':
        #    findLeft()
        if color.name == 'blue':
            print("Blue Planet found")
            break
        if color.name == 'red':
            print("Red Planet found")
            break
        if color.name == 'other':
            print(color.name)
            break
        if greytone < 0:
            turnLeft(abs(greytone))
        elif greytone > 0:
            turnRight(abs(greytone))
        

        
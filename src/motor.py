import ev3dev.ev3 as ev3
import time
import sys
import measurements as ms

# Motoren initialisieren
motor_left = ev3.LargeMotor("outB")
motor_right = ev3.LargeMotor("outD")

def move(m): # Vorwärts bewegen
    # m.run_timed(time_sp=100, speed_sp=50)
    m.speed_sp = 100
    m.command = "run-forever"

def moveBack(m): # Rückwärts bewegen
    m.run_timed(time_sp=1000, speed_sp=-100)
    
def steer(m, speed): # Lenken
    m.run_timed(time_sp=100, speed_sp=speed)




def moveForward(dur): # Vorwärts fahren
    
    while dur > 0:
        move(motor_left)
        move(motor_right)
        dur = dur - 1
        
def run():
    move(motor_left)
    move(motor_right)

def stop(): # Stoppen
    motor_left.stop()
    motor_right.stop() 
    
def moveBackward(dur): # Rückwärts fahren
    stop()
    while dur > 0:
        moveBack(motor_left)
        moveBack(motor_right)
        dur = dur - 1
        
    
def turnRight(dur): # Rechts drehen
    while dur > 0:
        steer(motor_left, 100)
        steer(motor_right, -90)
        dur = dur - 1
    run()
        

def turnLeft(dur):  # Links drehen
    while dur > 0:
        steer(motor_right, 100)
        steer(motor_left, -90)
        dur = dur - 1
    run()
        
        
def turn180(): # 180 Grad drehen
    motor_left.run_timed(time_sp=10000, speed_sp=72)
    
        
def obstacleInWay():
    moveBackward(2)
    ev3.Sound.speak('Slow down! meteorite in sight')
    turn180()
    followline()
    

def followline(): # folgt der Linie
    run()
    color = ms.ColorDetector()
    color.color_check() # checkt die Farbe
    while color.name == 'grey':
        color = ms.ColorDetector()
        color.color_check()
        greytone = color.greytone
        if ms.is_obstacle_ahead():
            obstacleInWay()
        elif greytone < -2:
            turnLeft(3)
        elif greytone > 2:
            turnRight(3)
    stop()
    
        

        
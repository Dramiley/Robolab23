import ev3dev.ev3 as ev3
import time
import sys


def move(m):
    m.reset()
    m.stop_action = "brake"
    m.speed_sp = 1050
    m.command = "run-forever"
    time.sleep(3)
    m.stop()


def rot(m):
    m.reset()
    m.stop_action = "brake"
    m.speed_sp = 10
    m.command = "run-forever"
    time.sleep(3)
    m.stop()


def run_try_motor():
    motor_move_port = "outA"
    motor_move = ev3.LargeMotor(motor_move_port)

    motor_rot_port = "outB"
    motor_rot = ev3.LargeMotor(motor_rot_port)

    while True:
        inp = input("Type cmd: ")
        if inp == "move":
           deg = 1
           move(motor_move)
        else:
            rot(motor_rot)

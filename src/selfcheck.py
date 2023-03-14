# run main
from inspect import isfunction

import main
from robot import Robot
from robot_dummy import RobotDummy

# add system tests here
if __name__ == "__main__":

    # test if the public functions of robot and robot_dummy are the same
    for func in dir(Robot):
        if func.startswith('_'):
            continue
        if func not in dir(RobotDummy):
            raise Exception('RobotDummy is missing function {}'.format(func))

    # and vice versa
    for func in dir(RobotDummy):
        if func.startswith('_'):
            continue
        if func not in dir(Robot):
            raise Exception('Robot is missing function {}'.format(func))

    # try and run the main
    # main.run()

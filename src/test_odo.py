import json

from robot import Robot
from odometry import Odometry
from planet import Direction

def odo():
    rob = Robot()
    rob._Robot__followline()
    rob._Robot__station_center()

    odo = Odometry()
    odo.set_coords((0, 0))
    odo.set_dir(Direction.NORTH)
    odo.calculate(rob.motor_pos_list)
    new_coords = odo.get_coords()
    new_dir = odo.get_dir()
    print(f"New coords: {new_coords}, new dir: {new_dir}")

    with open('motor_pos.txt', 'w') as filehandle:
        json.dump(rob.motor_pos_list, filehandle)
        filehandle.write(f"Calculated: New coords:{new_coords}, New dir:{new_dir}")


if __name__ == '__main__':
    odo()

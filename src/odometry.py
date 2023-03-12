# !/usr/bin/env python3
import math
from robot import Robot
from planet import Direction
from typing import Tuple, List

class Odometry:
    def __init__(self, robot:Robot, start_pos: Tuple[int, int]=(0, 0), start_dir: int=Direction.NORTH):
        """
        Initializes odometry module
        """

        # YOUR CODE FOLLOWS (remove pass, please!)

        # TODO: wheel_d shoudl be an attribute of Robot Class
        self.wheel_d = -1

        self.robot = robot

        self.tracking_interval = 0.5 # determines how often motor_pos should be tracked [per second]
        start_pos_left = self.robot.motor_left
        start_pos_right = self.robot.motor_right
        self.motor_pos_list = [[start_pos_left, start_pos_right]] # list of 2-element lists [[motor_pos1, motor_pos2], [.,.], ...]

        self.calc_parameters()

        self.current_pos = start_pos
        self.current_dir = start_dir

    def calc_parameters(self):
        wheel_radius = 2.7 # in cm
        wheel_circumference = 2*math.pi*wheel_radius

        # TODO: do count_per_rot have the same value for both motors?
        tacho_c_per_rot_r = self.robot.motor_left.count_per_rot
        self.distance_per_tick = wheel_circumference/tacho_c_per_rot_r

    def track_motor_pos(self):
        """
        Tracks motor positions of the motors in a list of tuples
        """
        motor_pos_left = self.robot.motor_left.position
        motor_pos_right = self.robot.motor_right.position
        self.motor_pos_list.append([motor_pos_left, motor_pos_right])

    def calculate(self):
        """
        Calculates all required values based on tracked pos_values

        Note: list comprehension idea taken from https://stackoverflow.com/a/5314307/20675205
        """
        #  get diffs to calculate from
        diffs = [[n_l-f_l, n_r-f_r] for [f_l, f_r], [n_l, n_r] in zip(list, list[1:])]

        # based on diffs and distance_per_tick d_r and d_l can be calculated
        distances = [[l*self.distance_per_tick, r*self.distance_per_tick] for [l, r] in diffs]
        d_s = [ 0.5*(d_l+d_r) for [d_l, d_r] in distances]
        alpha = [(d_r-d_l)/self.wheel_d for [d_l, d_r] in distances]

        r_s = [ d/self.wheel_d for d in d_s]
        # TODO: for alpha=0 we have to set s=d_l (or =d_r, doesn't matter)
        s = [ 2*r*math.sin(al/2) for [r, al] in zip(r_s, alpha)]

        # Calculate positions

        for angle, distance in zip(alpha, s):
            dir_vector = (math.cos(self.current_dir), math.sin(self.current_dir)) # unit vector denoting the direction

            # get vector which points towards new point
            rotated_vector = self.rotate_vector_by_deg(dir_vector, angle/2)
            # calculate new position coordinates
            self.current_pos += distance*rotated_vector
            # update dir
            self.current_dir += angle

    def rotate_vector_by_deg(self, vec: Tuple[int, int], deg: int) -> Tuple[int, int]:
        # rot_matrix = [
        #     [math.cos(deg), -math.sin(deg)],
        #     [math.sin(deg), math.cos(deg)]
        # ]
        # return dot product of rot_matrix and vec
        x_new = vec[0]*math.cos(deg) - vec[1]*math.sin(deg)
        y_new = vec[0]*math.sin(deg) + vec[1]*math.cos(deg)
        return (x_new, y_new)


    def reset_storage(self):
        """
        Resets tracked position values so new calculations can be computed completely separately

        TODO: init motor_pos_list with new start_pos (based on robot's orientation, only 4 possibilites here)
        """
        self.motor_pos_list = []


# !/usr/bin/env python3
import math
import time
import logging
import pdb
from threading import Thread
from typing import Tuple, List
from communication_facade import CommunicationFacade

from planet import Direction
from robot import Robot


class Odometry:

    def __init__(self, robot: Robot, track_interval: int = 0.5):
        """
        Initializes odometry module

        Parameters:
            track_interval (int): motor pos is read every track_interval seconds
        """

        # YOUR CODE FOLLOWS (remove pass, please!)

        # TODO: wheel_d should be an attribute of Robot Class
        self.wheel_d = 12.3  # wheel distance in cm

        self.robot = robot

        self.tracking_interval = track_interval

        # odometry should be running only when told so
        self.running = False

        self.tracking_thread = None

        self.__calc_parameters()

    def get_coords(self) -> Tuple[int, int]:
        """
        Returns current coords based on self.current_pos by rounding cm to coordinates (nearest multiple of 50cm)
        """
        RASTER_WIDTH = 50  # fixed
        delta_x = self.current_pos[0]
        delta_y = self.current_pos[1]

        sign_x = math.copysign(1, delta_x)  # because python has no built-in sign function :-|
        sign_y = math.copysign(1, delta_y)  # because python has no built-in sign function :-|

        delta_coords_x = ((abs(delta_x) + RASTER_WIDTH / 2) // 50) * 50
        delta_coords_y = ((abs(delta_y) + RASTER_WIDTH / 2) // 50) * 50

        new_coords_x = int(self.start_pos_coords[0] + sign_x * delta_coords_x)
        new_coords_y = int(self.start_pos_coords[1] + sign_y * delta_coords_y)
        # print(f"New coords x: {new_coords_x}, New coords y: {new_coords_y}")

        return (new_coords_x, new_coords_y)

    def get_dir(self) -> int:
        """
        Returns current orientation direction based on current_dir
        """
        self.current_dir = self.current_dir % 360  # makes sure self.current_dir is positive
        return ((self.current_dir + 45) // 90) * 90  # +45 makes sure that values nearer to 90 than 0 are rounded up

    def set_dir(self, dir: Direction):
        self.current_dir = dir

    def set_coords(self, coords: Tuple[int, int]):
        self.start_pos_coords = coords

    def __calc_parameters(self):
        wheel_radius = 2.7  # in cm
        wheel_circumference = 2 * math.pi * wheel_radius

        # TODO: do count_per_rot have the same value for both motors?
        tacho_c_per_rot_r = self.robot.motor_left.count_per_rot
        # TODO: is distance_per_tick given somewhere??
        self.distance_per_tick = wheel_circumference / tacho_c_per_rot_r

    def calculate(self, track_list: List[Tuple[int, int]]):
        """
        Calculates all required values based on tracked pos_values

        Note: list comprehension idea taken from https://stackoverflow.com/a/5314307/20675205
        """
        # current pos is relative
        self.current_pos = (0, 0)

        #  get diffs to calculate from
        diffs = [[n_l - f_l, n_r - f_r] for [f_l, f_r], [n_l, n_r] in zip(track_list, track_list[1:])]

        # based on diffs and distance_per_tick d_r and d_l can be calculated
        distances = [[l * self.distance_per_tick, r * self.distance_per_tick] for [l, r] in diffs]
        d_s = [0.5 * (d_l + d_r) for [d_l, d_r] in distances]
        alpha = [(d_r - d_l) / self.wheel_d for [d_l, d_r] in distances]

        r_s = [d / self.wheel_d for d in d_s]
        # TODO: for alpha=0 we have to set s=d_l (or =d_r=d_s, doesn't matter)
        s = [self.__get_driven_distance(r, al) for [r, al] in zip(r_s, alpha)]

        # Calculate positions

        for angle, distance in zip(alpha, s):
            dir_vector = (math.cos(self.current_dir), math.sin(self.current_dir))  # unit vector denoting the direction

            # get vector which points towards new point
            rotated_vector = self.__rotate_vector_by_deg(dir_vector, angle / 2)
            # calculate new position coordinates
            new_pos_x = (distance * rotated_vector[0]) + self.current_pos[0]
            new_pos_y = (distance * rotated_vector[1]) + self.current_pos[1]
            self.current_pos = (new_pos_x, new_pos_y)
            # update dir
            self.current_dir += angle

        # pdb.set_trace()

    def __get_driven_distance(self, r: int, al: int) -> int:
        """
        Returns distance s traveled by a wheel on circle with radius r and al
        """
        if al:
            return 2 * r * math.sin(al / 2)

        # alpha=0 -> traveled straight line->s=d
        return r * self.wheel_d

    def __rotate_vector_by_deg(self, vec: Tuple[int, int], deg: int) -> Tuple[int, int]:
        # rot_matrix = [
        #     [math.cos(deg), -math.sin(deg)],
        #     [math.sin(deg), math.cos(deg)]
        # ]
        # return dot product of rot_matrix and vec
        x_new = vec[0] * math.cos(deg) - vec[1] * math.sin(deg)
        y_new = vec[0] * math.sin(deg) + vec[1] * math.cos(deg)
        return (x_new, y_new)

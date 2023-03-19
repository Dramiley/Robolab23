#!/usr/bin/env python3
"""
TODO:
    - write list and weights of traversed nodes into logfile and compare it to manual traversion
TODO: Refactoring
    - replace Tuple[int, int] with alias type, see https://stackoverflow.com/a/33045252/20675205
TODO:
    - make sure blocked paths don't get confused with loops

TODO: add support for blocked path (don't mark as unexplored when entered node which has an adjacent blocked path)
"""

# Attention: Do not import the ev3dev.ev3 module in this file
from enum import IntEnum, unique
from typing import Optional, List, Tuple, Dict, Set

import math
import logging
import sys
import pdb
import operator

sys.path.insert(0, 'planet')


@unique
class Direction(IntEnum):
    """ Directions in shortcut """
    NORTH = 0
    EAST = 90
    SOUTH = 180
    WEST = 270


Weight = int
"""
Weight of a given path (received from the server)

Value:  -1 if blocked path
        >0 for all other paths
        never 0
"""


class Planet:
    """
    Contains the representation of the map and provides certain functions to manipulate or extend
    it according to the specifications
    """

    def __init__(self):
        """ Initializes the data structure

        Attributes:
            self.paths = Dict[Path]
            self.nodes = List[Tuple[int, int]]
                - planets node ids to coordinates of nodes for easier representation
            self.computed_shortest_paths = Dict
                - indizes=(normally) 2-element frozenset (set doesn't work bc not hasable) consisting of 2 nodes
                    - note: only one element for path of a node to itself!!! (since it's a set)
                    - ->allows for getting shortest path without having to introduce rules for ordering e.g. [n1, n2] or [n2, n1]
                - values=tuple (path, weight)
            self.computations_uptodate (bool): True if no new path has been added since last computation (which could make the computations obsolete)
                - ionitiates recomputation if False
        """
        self.paths = {}
        self.nodes = []

        self.unexplored = {}  # dict keeping track of unexplored paths of the format node: Set[Direction] which are the unexplored directions
        self.unexplored_nodes = [] # list of unexplored nodes (dont know in which dir, result from unveiling paths with unexplored nodes)

    def __is_node_known(self, node: Tuple[int, int]) -> bool:
        """
        Returns true if node has already been explored, else false
        """
        is_known = node in self.paths.keys()
        return is_known

    def add_path(self, start: Tuple[Tuple[int, int], Direction], target: Tuple[Tuple[int, int], Direction],
                 weight: int):
        """
        Adds a bidirectional path defined between the start and end coordinates to the map and assigns the weight to it

            Example:
                add_path(((0, 3), Direction.NORTH), ((0, 3), Direction.WEST), 1)
            :param start: 2-Tuple
            :param target:  2-Tuple
            :param weight: Integer
            :return: void

        NOTE:
            - blocked paths are registered as loops (start=targe) and weight=-1

        TODO: initiate recomputation of self.computed_shortest_paths
            - instead of having to compute them every time on the run
        """
        start_coords = start[0]
        start_entry_dir = start[1]
        target_coords = target[0]
        target_entry_dir = target[1]

        if not (target_coords in self.paths.keys()):
            # if no path is yet known for target_coords
            # since we need to add path to both start and target (paths are bidirectional)
            self.paths[target_coords] = {}

        if not (start_coords in self.paths.keys()):
            # if no path is yet known for start_coords
            self.paths[start_coords] = {}

        self.add_new_path(start, target, weight)

    def add_new_path(self, start: Tuple[Tuple[int, int], Direction], target: Tuple[Tuple[int, int], Direction],
                     weight: int):
        """
        Adds new path to self.paths AND updates self.unexplored
        """
        start_coords = start[0]
        start_exit_dir = start[1]
        target_coords = target[0]
        target_entry_dir = target[1]

        self.paths[start_coords][start_exit_dir] = (target_coords, target_entry_dir, weight)
        self.paths[target_coords][target_entry_dir] = (start_coords, start_exit_dir, weight)

        if start_coords in self.unexplored.keys() and start_exit_dir in self.unexplored[start_coords]:
            self.__mark_dir_explored(start_coords, start_exit_dir)
        if target_coords in self.unexplored.keys() and target_entry_dir in self.unexplored[target_coords]:
            self.__mark_dir_explored(target_coords, target_entry_dir)


    def get_paths(self) -> Dict[Tuple[int, int], Dict[Direction, Tuple[Tuple[int, int], Direction, Weight]]]:
        """
        Returns all paths

        Example:
            {
                (0, 3): {
                    Direction.NORTH: ((0, 3), Direction.WEST, 1),
                    Direction.EAST: ((1, 3), Direction.WEST, 2),
                    Direction.WEST: ((0, 3), Direction.NORTH, 1)
                },
                (1, 3): {
                    Direction.WEST: ((0, 3), Direction.EAST, 2),
                    ...
                },
                ...
            }
        :return: Dict
        """

        # YOUR CODE FOLLOWS (remove pass, please!)
        return self.paths

    def update_path_to_blocked(self, start: Tuple[int, int], end: Tuple[int, int], start_dir: Direction):
        """
        Since meteorites can land anytime, already explored paths can get blocked later on.
        Calling this function allows to register already explored paths as blocked

        WARNINGS: make sure that path is explored (calling is_path_explored() )
        NOTE: maybe leave this func out and just call add_path() again?
        """
        the_blocked_path = self.paths[start][start_dir]  # format (node, dir, weight)
        end_dir = the_blocked_path[1]

        # for debugging
        if the_blocked_path[0] == end:
            # it should node==target
            raise AssertionError("Somehow path points to another target node than the one given")

        # make path blocked for start
        self.paths[start][start_dir] = (start, start_dir, -1)
        self.paths[end][end_dir] = (end, end_dir, -1)

    def __djikstra(
            self, start: Tuple[int, int], target: Tuple[int, int]
    ) -> Optional[ Tuple[ List[Tuple[ Tuple[int, int], Direction]], int] ]:
        """"
        Computes shortest path and its weight btw start and end based on self.paths
        ->Easier implementation based on wikipedia article https://en.wikipedia.org/wiki/Dijkstra's_algorithm

        Returns:
            - (path, weight), None if target is unreachable
        """
        dist = {start: 0}
        prev = {start: None}
        unvisited = list(self.paths.keys())

        # init values
        for node in self.paths.keys():
            if node != start:
                dist[node] = math.inf
                prev[node] = None

        while unvisited:
                # get node n_min with min dist (taken from https://stackoverflow.com/a/3282904/20675205)
                n_min = min(unvisited, key=lambda n: dist[n])

                if n_min == target:
                    # we only care about shorest path to target
                    break

                # remove n_min from unvisited
                unvisited.remove(n_min)
                # for each neighbor of n_min in unvisited compare edge dist over n_min to current one
                neighbors_dict = self.__get_neighbors(n_min) # dict of format neighbor: (direction, weight)

                for neighbor in neighbors_dict.keys():
                    weight = neighbors_dict[neighbor][1]
                    if weight > 0:
                        # dont include blocked paths (weight=-1) into computation
                        direction = neighbors_dict[neighbor][0]

                        new = dist[n_min] + weight

                        if new < dist[neighbor]:
                            dist[neighbor] = new
                            prev[neighbor] = (n_min, direction)

        if dist[target] == math.inf:
            return None

        shortest_path = self.__dijkstra_reconstruct_path(start, target, dist, prev)
        return shortest_path

    def __dijkstra_reconstruct_path(
            self, start: Tuple[int, int], target: Tuple[int, int], dist: Dict[Tuple[int, int], int], prev: Dict[Tuple[int, int], Optional[Tuple[Tuple[int, int], Direction]]]
    ) -> Tuple[List[ Tuple[ Tuple[int, int], Direction ]], int]:
        """
        Parameters:
            - start, end: nodes of wanted path
            - dist[node] = min_dist from start to node
            - prev[node] = (prev_node, dir) with dir=direction which should be taken from prev_node in order to reach target

        Returns:
            - tuple of (path, weight) with path given as list of node and direction in which the path should be followed
        """

        path = [(target, None)]
        current_node = target

        while current_node != start:
            path.insert(0, prev[current_node])
            current_node = prev[current_node][0]

        return (path, dist[target])

    def __get_neighbors(self, node: Tuple[int, int]) -> Dict[Tuple[int, int], Tuple[Direction, int]]:
        """
        Returns Dict of neighbor nodes of 'node' and corresponding (Direction, weight)
        """
        neighbor_dict = {}
        for outgoing_path in self.paths[node].items():
            # outgoing_path format = {dir: (end, end_entry, weight)}
            direc = outgoing_path[0]
            node = outgoing_path[1][0]
            weight = outgoing_path[1][2]
            neighbor_dict[node] = (direc, weight)
        return neighbor_dict



    def get_shortest_path(self, start: Tuple[int, int], target: Tuple[int, int]) -> Optional[
        List[Tuple[Tuple[int, int], Direction]]]:
        """
        Returns a shortest path between two nodes

        Examples:
            shortest_path((0,0), (2,2)) returns: [((0, 0), Direction.EAST), ((1, 0), Direction.NORTH)]
            shortest_path((0,0), (1,2)) returns: None
        :param start: 2-Tuple
        :param target: 2-Tuple
        :return: None, List[] or List[Tuple[Tuple[int, int], Direction]]
        """

        # YOUR CODE FOLLOWS (remove pass, please!)

        if self.__is_node_known(target):
            # perform djikstra and return shortest path
            result = self.__djikstra(start, target)
            if result is None:
                return None
            # else we want only path, not the weight
            shortest_path = result[0]
            return shortest_path
        else:
            # continue exploration until target is found
            return None

    def is_path_explored(self, node: Tuple[int, int], dir: Direction):
        if self.__is_node_known(node):
            return True
        elif dir in self.paths[node]:
            return True

        return False

    def add_possible_unexplored_path(self, node: Tuple[int, int], dir: Direction):
        """
        Tracks unexplored path (node, direction)
            ->adds path to self.unexplored if it is not explored
        """
        if dir in self.paths[node].keys():
            # there is already a path registered for this dir
            return

        if node not in self.unexplored.keys():
            self.unexplored[node] = set()

        self.unexplored[node].add(dir)

    def get_next_exploration_dir(self, current_node: Tuple[int, int]) -> Optional[Direction]:
        """

        Continue exploring planet by going to the nextnearest node which has an unexplored dir

        1. get next node to be explored (if there is one!!!)
        2. drive to that node and continue exploring it in that direction

        Returns:
            - direction which to follow for exploration
            - None if whole map has been explored

        """
        if not self.unexplored and not self.unexplored_nodes:
            # planet is fully explored!!!
            return None

        if current_node in self.unexplored:
            # continue exploring that current node (->dfs)
            return next(iter(self.unexplored[current_node]))

        all_unexplored_nodes = list(self.unexplored.keys())+self.unexplored_nodes
        # shortest_paths are a list of the form [(Path, weight)]
        shortest_paths = [self.__djikstra(current_node, target) for target in all_unexplored_nodes]
        # remove all None values bc they cant be compared in min function
        shortest_paths = list(filter(lambda x: x != None, shortest_paths))

        if not shortest_path:
            # nothing to explore anymore
            return None

        shortest_path = min(shortest_paths, key=operator.itemgetter(1))
        next_path_without_weight = shortest_path[0]  # format: List[Tuple[node, Direction]]
        # TODO: check that next_dir really accesses the direction-element!
        # [0]=(node, weight) -> [1]=weight
        next_dir = next_path_without_weight[0][1]
        return next_dir

    def __mark_dir_explored(self, node_coords: Tuple[int, int], dir: Direction):
        """
        Unmarks dir of node_coords as not being unexplored anymore
        ->WARNING: make sure node_coords is unexplored in dir before passing it to this function!
        """

        self.unexplored[node_coords].remove(dir)
        if not self.unexplored[node_coords]:
            # no more unexplored dirs for node_coords
            # remove as unexplored if all directions of node have been explored
            del self.unexplored[node_coords]

    def is_exploration_complete(self) -> bool:
        """
        Returns: True if all nodes have been explored, False otherwise
        @rtype: bool

        TODO: redundant, completeness can be checked by checking if get_next_exploration_path == None
        """
        # TODO: remove
        # return False

        # we are complete if there are no unexplored nodes
        is_complete = not self.unexplored
        return is_complete

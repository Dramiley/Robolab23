#!/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
from enum import IntEnum, unique
from typing import Optional, List, Tuple, Dict, Set


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


class Path:
    """
    Class representation of a path

    Attributes:
        - node1_id: id of first npde
        - entry_dir1: entry direction of path into node1
        - node2_id: id of 2nd node
        - entry_dir2: entry direction of path into node2
        - weight

    """

    def __init__(self, node1_id: int, entry_dir1: Direction, node2_id: int, entry_dir2: Direction, weight):
        self.node1_id = node1_id
        self.entry_dir1 = entry_dir1
        self.nodle2_id = node2_id
        self.entry_dir2 = entry_dir2
        self.weight = weight


class Planet:
    """
    Contains the representation of the map and provides certain functions to manipulate or extend
    it according to the specifications
    """

    def __init__(self):
        """ Initializes the data structure

        Parameters:
            self.paths = List[Path]
            self.nodes = List[Tuple[int, int]]
                - maps node ids to coordinates of nodes for easier representation
        """
        self.paths = []
        self.nodes = []

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
        """
        start_coords = start[0]
        start_id = self.get_node_id(start_coords)
        start_entry_dir = start[1]
        target_coords = target[0]
        target_entry_dir = target[1]
        target_id = self.get_node_id(target_coords)

        path = Path(start_id, start_entry_dir, target_id, target_entry_dir, weight)
        self.paths.append(path)


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
        pass

    def shortest_path(self, start: Tuple[int, int], target: Tuple[int, int]) -> Optional[List[Tuple[Tuple[int, int], Direction]]]:
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
        pass

    def get_node_coord(self, id: int) -> Tuple[int, int]:
        """"
        Returns coords belonging to node specified by given id
        """
        return self.nodes[id]

    def get_node_id(self, coord: Tuple[int, int]):
        """
        Returns node it based on given coordinates, if node is unknown a new one is registered with given coords
        """
        try:
            return self.nodes.index(coord)
        except:
            self.nodes.append(coord)
            return self.nodes.index(coord)


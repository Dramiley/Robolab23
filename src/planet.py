#!/usr/bin/env python3
"""
TODO: Refactoring
    - replace Tuple[int, int] with alias type, see https://stackoverflow.com/a/33045252/20675205
"""

# Attention: Do not import the ev3dev.ev3 module in this file
from enum import IntEnum, unique
from typing import Optional, List, Tuple, Dict, Set

import logging

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

        Parameters:
            self.paths = Dict[Path]
            self.nodes = List[Tuple[int, int]]
                - maps node ids to coordinates of nodes for easier representation
        """
        self.paths = {}
        self.nodes = []

    def is_node_known(self, node: Tuple[int, int]) -> bool:
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
        """
        start_coords = start[0]
        start_entry_dir = start[1]
        target_coords = target[0]
        target_entry_dir = target[1]

        self.path[start_coords][start_entry_dir] = (target_coords, target_entry_dir, weight)
        self.path[target_coords][target_entry_dir] = (start_coords, start_entry_dir, weight)

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

    def expand_node(
            self, node: Tuple[int, int],
            weight0: int,
            unvisited: List[Tuple[int, int]],
            shortest_paths: Dict[int, Tuple[int, int]]
        ) -> Dict[Tuple[int, int] ,Tuple[int, Tuple[int, int]]]:
        """
        Expands node given by its coordinates and returns neighbor paths as list of (node, weight, parent)

        Args:
            node: node to expand
            weight0: weight which was necessary to get to that node
            unvisited: list of unvisited nodes
        """
        outgoing_paths = self.paths[node] # outgoing_paths is of form {Direction: (coords, weight)}
        marked = {} # dict with keys=nodes, values=(weight, parent_node)
        logging.debug(f'Expanding node {node}')
        for (coords, weight) in outgoing_paths.values():
            new_weight = weight+weight0
            if coords in unvisited:
                marked[coords] = (new_weight, node)
            else:
                # check whether this path is shorter
                prev_weight = shortest_paths[coords][0]

                if prev_weight > new_weight:
                    marked[coords] = (new_weight, node)
        return marked

    def djikstra_reconstruct_shortest_path(self,
            shortest_paths: Dict[Tuple[int, int], Tuple[int, Tuple[int, int]]],
            start: Tuple[int, int], target: Tuple[int, int]
        ) -> Tuple[List[Tuple[Tuple[int, int], Direction]], int]:
        """
        Returns path as list of nodes based on given shortest_paths and its weight

        Returns:
            (List[(node direction)], weight)
        """
        list = [(target, None)]
        weight = shortest_paths[target][0]
        current_node = target
        while current_node != start:
            end_node = current_node
            current_node = shortest_paths[current_node][1]
            dir = None
            outgoing_paths = self.paths[current_node]
            for d in outgoing_paths.keys():
                if outgoing_paths[d] == end_node:
                    dir = d
            list.append((current_node, d))
        list.reverse() # bc appeding started from target towards start
        return (list, weight)

    def djikstra(self, start_coords: Tuple[int, int], target_coords: Tuple[int, int]) -> Optional[Tuple[List[Tuple[int, int]], int]]:
        """
        1. choose node1 with minimal weight out of marked nodes
        2. if this node is target->finished else continue
        3. expand node1 updating marked nodes
        4. continue with 1

        Args:
            - start_coords, target_coords: coords of start/target
        Returns:
            - If exists: List of nodes denoting shortest path between start and target and its weight
            - if no path between start and target: None

        TODO: shortest path has to include list of directions to traverse!!!
        TODO: does it make sense to start search from target node? (for if it's isolated?)
        TODO: test sorted(marked.items(), key=lambda x: x[1][0]) on marked
        TODO: save calculated shortest paths so they dont have to be recalculated
        """
        # init data structures
        unvisited = set(self.paths.keys()) # set of unvivisted nodes
        unvisited.remove(start_coords)
        marked = {start_coords: (0, None)} # dict with keys=nodes, values=(weight, parent_node)
        shortest_paths = {} # dict with key=nodes, values=(weight, parent_node)

        # actual algorithm
        next_node = start_coords
        weight0 = 0
        while unvisited:
            new_marked_nodes = self.expand_node(next_node, weight0, unvisited, shortest_paths)

            marked.update(new_marked_nodes)
            sorted_marked = sorted(marked.items(), key=lambda x: x[1][0]) # x=[(start_coords,(weight, target_coords))]

            next_node = sorted_marked[0][0] # sorted_marked = list of (start_coords, (weight, target_coords))
            if next_node == target_coords:
                # return shortest path based on shortest_paths
                return self.djikstra_reconstruct_shortest_path(shortest_paths, target_coords)
            weight0 = sorted_marked[1]
            unvisited.remove(next_node)

        return None


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
        if self.is_node_known():
            # perform djikstra and return shortest path
            shortest_path = self.djikstra()[0]
        else:
            # continue exploration until target is found
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


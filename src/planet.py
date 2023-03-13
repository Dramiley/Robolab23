#!/usr/bin/env python3
"""
TODO:
    - write list and weights of traversed nodes into logfile and compare it to manual traversion
TODO: Refactoring
    - replace Tuple[int, int] with alias type, see https://stackoverflow.com/a/33045252/20675205
TODO:
    - store computed shortest_paths in a variable
TODO:
    - maybe don't stop djikstra() even if target node is found->maybe will need following nodes later on (store!)
"""

# Attention: Do not import the ev3dev.ev3 module in this file
from enum import IntEnum, unique
from typing import Optional, List, Tuple, Dict, Set

import math
import logging
import sys
import pdb
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
                - maps node ids to coordinates of nodes for easier representation
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

        self.unexplored = {} # dict keeping track of unexplored paths of the form node: Direction
        self.computed_shortests_paths = {} # stores shortests paths, indezes=2-element sets, values=List[node, dir]
        self.computations_uptodate = False

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

        TODO: initiate recomputation of self.computed_shortest_paths
            - instead of having to compute them every time on the run
        """
        start_coords = start[0]
        start_entry_dir = start[1]
        target_coords = target[0]
        target_entry_dir = target[1]

        if not (start_coords in self.paths.keys()):
            # if no path is yet known for start_coords
            self.paths[start_coords] = {}

            # init shortest path to node itself
            path_to_self = frozenset([start_coords, start_coords]) # since set->only 1 element
            self.computed_shortests_paths[path_to_self] = ([], 0)
        if not (target_coords in self.paths.keys()):
            # if no path is yet known for target_coords
            self.paths[target_coords] = {}

            # init shortest path to node itself
            path_to_self = frozenset([target_coords, target_coords]) # since set->only 1 element
            self.computed_shortests_paths[path_to_self] = ([], 0)

        self.paths[start_coords][start_entry_dir] = (target_coords, target_entry_dir, weight)
        self.paths[target_coords][target_entry_dir] = (start_coords, start_entry_dir, weight)

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
        outgoing_paths = self.paths[node] # outgoing_paths is of form {Direction: (coords, dir, weight)}
        marked = {} # dict with keys=nodes, values=(weight, parent_node)
        logging.debug(f'Expanding node {node}')
        # pdb.set_trace()
        for (coords, _, weight) in outgoing_paths.values():
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

        Args:
            shortest_paths: Dict of structure {node: (weight, parent_node)}
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
                connected_node = outgoing_paths[d][0]
                if connected_node == end_node:
                    dir = d
            list.append((current_node, dir))
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
        marked = {start_coords: (0, None)} # dict with keys=nodes, values=(weight, parent_node)
        shortest_paths = {start_coords: (0, None)} # dict with key=nodes, values=(weight, parent_node)

        # actual algorithm
        next_node = start_coords
        weight0 = 0
        while unvisited:
            shortest_paths[next_node] = marked[next_node]
            marked.pop(next_node)

            new_marked_nodes = self.expand_node(next_node, weight0, unvisited, shortest_paths)
            unvisited.remove(next_node)

            # TODO: Problem; start_coords ist in markeds
            marked.update(new_marked_nodes)
            sorted_marked = sorted(marked.items(), key=lambda x: x[1][0]) # x=[(start_coords,(weight, target_coords))]
            # logging.debug(f"Sorted marked: {sorted_marked}")
            next_path = sorted_marked[0]
            (next_node, (weight0, _)) = next_path
            # next_node = sorted_marked[0][0] # sorted_marked = list of (start_coords, (weight, target_coords))
            if next_node == target_coords:
                # return shortest path based on shortest_paths
                shortest_paths[next_node] = marked[next_node]
                return self.djikstra_reconstruct_shortest_path(shortest_paths, start_coords, target_coords)
            # next_node has been explored->shortest path

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
        node_id = frozenset([start, target])
        if node_id in self.computed_shortests_paths.keys():
            # path has already been computed previously
            return self.computed_shortests_paths[node_id]
        # TODO: remove elif when implemented precomputation of djikstra, since all known nodes must have a shortest path then
        elif self.is_node_known(target):
            # perform djikstra and return shortest path
            shortest_path = self.djikstra(start, target)[0]
            return shortest_path
        else:
            # continue exploration until target is found
            return None

    def store_shortest_paths(self,
                            start: Tuple[int, int], target: Tuple[int, int],
                            list: List[Tuple[Tuple[int, int], Direction]]
    ):
        """
        Stores the given shortest path (=list) so they don't have to be recomputed
        - Note: subpaths are also shortest paths!!!
        """
        nodes_set = frozenset([start, target]) # index needs to be hashable
        self.computed_shortests_paths[nodes_set] = list

    def get_precomputed_shortest_paths(
            self, start: Tuple[int, int], target: Tuple[int, int]
    ) -> Optional[List[Tuple[Tuple[int, int], Direction]]]:
        """
        Returns:
            - List (=shortest path) if there is already a precomputed one between start and target
            - None if there is no precomputed path btw start and target
        """
        node_id = frozenset([start, target]) # see structure of self.self.computed_shortests_paths for why
        if node_id in self.computed_shortests_paths.keys():
            return self.computed_shortests_paths[node_id]

        return None

    def update_shortest_paths(
            self, start: Tuple[int, int], start_dir: Direction,
            target: Tuple[int, int], target_dir: Direction
        ):
        """
        Updates self.computed_shortest_path with new path if node is one that wasn't explored before

        Note: By design the start node should already be known!
        """
        if not self.is_node_known(start):
            raise ValueError("Start node is not known, but should be :(")

        if self.is_node_known(target):
            # node is known and hence there must already exist a shortest path to it
            current_weight = self.computed_shortests_paths

    def is_path_explored(self, node: Tuple[int, int], dir: Direction):
        if self.is_node_known(node):
            return True
        elif dir in self.paths[node]:
            return True

        return False

    def add_unexplored_path(self, node: Tuple[int, int], dir: Direction):
        """
        Tracks unexplored path
        """
        self.unexplored[node] = dir

    def get_next_path(self, current_node: Tuple[int, int]=(0, 0)) -> Optional[Direction]:
        """
        WARNING: Make sure to mark the node as explored once it has been reached!!!

        Continue exploring planet using dfs, chooses next node based on distances from current pos

        1. get next node to be explored (if there is one!!!)
        2. drive to that node and continue exploring it in that direction

        Returns:
            - direction in which exploration should be started (from currentnode)
            - None if whole map has been explored

        """
        if not self.unexplored:
            # planet is fully explored!!!
            return None

        # compute node which is next to current pos->based on weights (check shprtest path)



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



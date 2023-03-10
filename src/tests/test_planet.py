#!/usr/bin/env python3
# import sys

# # sys.path.insert(0, 'planet')
# sys.path.append('ROBOLAB-GROUP-046/src')

import unittest
import logging
import pdb
from planet import Direction, Planet

class ExampleTestPlanet(unittest.TestCase):
    def setUp(self):
        """
        Instantiates the planet data structure and fills it with paths

        +--+
        |  |
        +-0,3------+
           |       |
          0,2-----2,2 (target)
           |      /
        +-0,1    /
        |  |    /
        +-0,0-1,0
           |
        (start)

        """
        # Initialize your data structure here
        self.planet = Planet()
        self.planet.add_path(((0, 0), Direction.NORTH), ((0, 1), Direction.SOUTH), 1)
        self.planet.add_path(((0, 1), Direction.WEST), ((0, 0), Direction.WEST), 1)

    @unittest.skip('Example test, should not count in final test results')
    def test_target_not_reachable_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target not reachable nearby

        Result: Target is not reachable
        """
        self.assertIsNone(self.planet.shortest_path((0, 0), (1, 2)))


class TestRoboLabPlanet(unittest.TestCase):
    def setUp(self):
        """
        Instantiates the planet data structure and fills it with paths

        MODEL YOUR TEST PLANET HERE (if you'd like): Planet Candle

        """
        # Initialize your data structure here
        self.planet = Planet()
        self.node_coords = [
            (19, -2), (18, -2), (18, 0), (19, 1), (20, -2), (20, 0),
            (19, 1), (19, 3)
        ]

        self.planet.add_path(((19, -2), Direction.WEST), ((18, -2), Direction.EAST), 1)
        self.planet.add_path(((18, -2), Direction.NORTH), ((18, 0), Direction.SOUTH), 1)
        self.planet.add_path(((18, 0), Direction.NORTH), ((19, 1), Direction.WEST), 2)

        self.planet.add_path(((19, -2), Direction.EAST), ((20, -2), Direction.WEST), 1)
        self.planet.add_path(((20, -2), Direction.NORTH), ((20, 0), Direction.SOUTH), 1)
        self.planet.add_path(((20, 0), Direction.NORTH), ((19, 1), Direction.EAST), 2)

        self.planet.add_path(((19, 1), Direction.NORTH), ((19, 2), Direction.SOUTH), 1)
        self.planet.add_path(((19, 2), Direction.EAST), ((19, 3), Direction.SOUTH), 1)
        self.planet.add_path(((19, 2), Direction.WEST), ((19, 3), Direction.WEST), 2)

        # logging.basicConfig(level=logging.DEBUG)

    def test_integrity(self):
        """
        This test should check that the dictionary returned by "planet.get_paths()" matches the expected structure
        """
        # TODO: check paths_should with https://robolab.inf.tu-dresden.de/planets/Candle.png
        # TODO: add paths so there are unreachable points and paths with same weight between two nodes
        paths_should = {
            (19, -2): {
                Direction.EAST: ((20, -2), Direction.WEST, 1),
                Direction.WEST: ((18, -2), Direction.EAST, 1)
            },
            (18, -2): {
                Direction.EAST: ((19, -2), Direction.WEST, 1),
                Direction.NORTH: ((18, 0), Direction.SOUTH, 1)
            },
            (18, 0): {
                Direction.SOUTH: ((18, -2), Direction.NORTH, 1),
                Direction.NORTH: ((19, 1), Direction.WEST, 2)
            },

            (20, -2): {
                Direction.WEST: ((19, -2), Direction.EAST, 1),
                Direction.NORTH: ((20, 0), Direction.SOUTH, 1)
            },
            (20, 0): {
                Direction.SOUTH: ((20, -2), Direction.NORTH, 1),
                Direction.NORTH: ((19, 1), Direction.EAST, 2)
            },

            (19, 1): {
                Direction.EAST: ((20, 0), Direction.NORTH, 2),
                Direction.WEST: ((18, 0), Direction.NORTH, 2),
                Direction.NORTH: ((19, 2), Direction.SOUTH, 1)
            },
            (19, 2): {
                Direction.SOUTH: ((19, 1), Direction.NORTH, 1),
                Direction.EAST: ((19, 3), Direction.SOUTH, 1),
                Direction.WEST: ((19, 3), Direction.WEST, 2)
            },
            (19, 3): {
                Direction.WEST: ((19, 2), Direction.WEST, 2),
                Direction.SOUTH: ((19, 2), Direction.EAST, 1)
            }

        }
        # print(paths_should)
        # print(self.planet.get_paths())

        # for coords in self.node_coords:
        #     equal = paths_should[coords] == self.planet.get_paths()[coords]
        #     print(equal, " ", coords)

        # pdb.set_trace()
        # inp = input("Coords:") # input as e.g. "19 1"
        # while inp != "q":
        #     coords = inp.split(" ")
        #     coords = (int(coords[0]), int(coords[1]))
        #     print(paths_should[coords])
        #     print(self.planet.get_paths()[coords])
        #     inp = input("Coords:")

        self.assertDictEqual(paths_should, self.planet.get_paths())
        # self.fail('implement me!')

    def test_empty_planet(self):
        """
        This test should check that an empty planet really is empty
        """
        self.fail('implement me!')

    def test_target(self):
        """
        This test should check that the shortest-path algorithm implemented works.

        Requirement: Minimum distance is three nodes (two paths in list returned)
        """
        self.fail('implement me!')

    def test_target_not_reachable(self):
        """
        This test should check that a target outside the map or at an unexplored node is not reachable
        """
        self.fail('implement me!')

    def test_same_length(self):
        """
        This test should check that the shortest-path algorithm implemented returns a shortest path even if there
        are multiple shortest paths with the same length.

        Requirement: Minimum of two paths with same cost exists, only one is returned by the logic implemented
        """
        self.fail('implement me!')

    def test_target_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target nearby

        Result: Target is reachable
        """
        self.fail('implement me!')

    def test_target_not_reachable_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target not reachable nearby

        Result: Target is not reachable
        """
        self.fail('implement me!')

    def test_sorting_triple_set(self):
        """
        Sorts a given set of triples based on their 2nd elem
        using the python function sorted()
        - sorted: returns sorted LIST
        """
        d = set([
            (9,5,3), (4,1,6), (7,89,5)
        ])
        d_sorted = sorted(d, key=lambda x: x[1])
        self.assertEqual(d_sorted, [(4,1,6), (9,5,3), (7,89,5)])


if __name__ == "__main__":
    unittest.main()

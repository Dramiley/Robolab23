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

        self.empty_planet = Planet()

        self.set_up_schoko_till_148_120()

    def set_up_schoko_till_148_120(self):
        self.schoko = Planet()

        self.schoko.add_path(((150, 120), Direction.SOUTH), ((150, 120), Direction.SOUTH), -1)
        # simulate scan of (150, 120)
        self.schoko.add_possible_unexplored_path((150, 120), Direction.WEST)

        # go to (149, 120)
        self.schoko.add_path(((150, 120), Direction.WEST), ((149, 120), Direction.EAST), 1)

        # simulate scan of (149, 120)
        self.schoko.add_possible_unexplored_path((149, 120), Direction.EAST)
        self.schoko.add_possible_unexplored_path((149, 120), Direction.WEST)
        self.schoko.add_possible_unexplored_path((149, 120), Direction.NORTH)

        # get Path C
        self.schoko.add_path(((148, 120), Direction.NORTH), ((149, 121), Direction.WEST), 1)
        # go to (148, 120)
        self.schoko.add_path(((149, 120), Direction.WEST), ((148, 120), Direction.EAST), 2)

        # simulate scan at (148, 120)
        self.schoko.add_possible_unexplored_path((148, 120), Direction.NORTH)

        # Path C is now blocked (A)
        self.schoko.add_path(((148, 120), Direction.NORTH), ((148, 120), Direction.NORTH), -1)
        self.schoko.add_path(((149, 121), Direction.WEST), ((149, 121), Direction.WEST), -1)

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

        self.assertDictEqual(paths_should, self.planet.get_paths())
        # self.fail('implement me!')

    def test_empty_planet(self):
        """
        This test should check that an empty planet really is empty
        """
        self.assertEqual(self.empty_planet.get_paths(), {})
        self.assertEqual(self.empty_planet.nodes, [])
        # self.fail('implement me!')

    def test_target(self):
        """
        This test should check that the shortest-path algorithm implemented works.

        Requirement: Minimum distance is three nodes (two paths in list returned)
        """
        start = (19, -2)
        target = (19, 2)
        shortest_path = self.planet.get_shortest_path(start, target)

        shortest_path_should = [
            ((19, -2), Direction.EAST), ((20, -2), Direction.NORTH), ((20, 0), Direction.NORTH),
            ((19, 1), Direction.NORTH), ((19, 2), None)
        ]
        self.assertEqual(shortest_path, shortest_path_should)

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
        # candle has two paths of same length 5 from (19, -2) to (19, 2)
        start = (19, -2)
        target = (19, 2)
        shortest_path = self.planet.get_shortest_path(start, target)

        shortest_path_should = [
            ((19, -2), Direction.EAST), ((20, -2), Direction.NORTH), ((20, 0), Direction.NORTH),
            ((19, 1), Direction.NORTH), ((19, 2), None)
        ]
        self.assertEqual(shortest_path, shortest_path_should)

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

    def test_next_exploration_dir(self):
        """
        Checks that next exploration target is handed over correctly
        """
        current_node = (148, 120)
        next_dir = self.schoko.get_next_exploration_dir(current_node)
        self.assertEqual(next_dir, Direction.EAST)

if __name__ == "__main__":
    unittest.main()

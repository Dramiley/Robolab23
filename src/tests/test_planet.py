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

        MODEL YOUR TEST PLANET HERE (if you'd like): Planet Candle - was removed from website later on :'((

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

        self.setup_schoko_till_148_120()
        self.setup_chadwick()

    def setup_schoko_till_148_120(self):
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

        # Add unveiled paths given at communication point A
        self.schoko.add_path(((148, 120), Direction.NORTH), ((148, 120), Direction.NORTH), -1)
        self.schoko.add_path(((149, 121), Direction.WEST), ((149, 121), Direction.WEST), -1)
        self.schoko.add_path(((149, 121), Direction.NORTH), ((149, 122), Direction.SOUTH), 2)
        self.schoko.add_path(((149, 122), Direction.EAST), ((150, 122), Direction.WEST), 2)
        self.schoko.add_path(((149, 122), Direction.WEST), ((149, 122), Direction.WEST), -1)

    def simulate_chadwick_exploration(self):
        self.chadwick = Planet()

        # block start path
        self.chadwick.add_path(((1, 10), Direction.SOUTH), ((1, 10), Direction.SOUTH), -1)
        # simulate check_explorable_paths on (1, 10)
        self.chadwick.add_possible_unexplored_path((1, 10), Direction.NORTH)
        # drive to (1,12)
        self.chadwick.add_path(((1, 10), Direction.NORTH), ((1, 12), Direction.SOUTH), 9)
        # simulate station scan on (1,12)
        self.chadwick.add_possible_unexplored_path((1, 12), Direction.WEST)
        self.chadwick.add_possible_unexplored_path((1, 12), Direction.NORTH)

        # drive to (1, 13)
        self.chadwick.add_path(((1, 12), Direction.NORTH), ((1, 13), Direction.SOUTH), 12)
        # scan (1, 13)
        self.chadwick.add_possible_unexplored_path((1, 13), Direction.NORTH)
        self.chadwick.add_possible_unexplored_path((1, 13), Direction.WEST)

        # mothership sends paths B
        self.chadwick.add_path(((-1, 12), Direction.EAST), ((0, 12), Direction.WEST), 5)
        self.chadwick.add_path(((0, 11), Direction.NORTH), ((0, 12), Direction.SOUTH), 7)

        # drive to (0, 14)
        self.chadwick.add_path(((1, 13), Direction.NORTH), ((0, 14), Direction.EAST), 7)
        # mothership sends us C
        self.chadwick.add_path(((1, 13), Direction.EAST), ((0, 12), Direction.NORTH), 6)
        # scan (0, 14)
        self.chadwick.add_possible_unexplored_path((0, 14), Direction.SOUTH)
        self.chadwick.add_possible_unexplored_path((0, 14), Direction.WEST)

        # drive loop in SOUTH dir
        self.chadwick.add_path( ((0, 14), Direction.SOUTH), ((0, 14), Direction.SOUTH), 1)
        self.chadwick.add_path( ((0, 14), Direction.WEST), ((0, 14), Direction.WEST), -1)
        # now we should return to (0, 14) and continue exploring (0, 12) in Direction.EAST bc thé path to (0, 12) is shorter than the one to (1, 12)
        # TODO: check the get_next_exploration_dir returns (0, 12) and not (1, 12)

    def setup_chadwick(self):
        self.chadwick = Planet()
        self.chadwick.add_path(((1, 10), Direction.SOUTH), ((1, 10), Direction.SOUTH), -1)
        self.chadwick.add_path(((1, 10), Direction.NORTH), ((1, 12), Direction.SOUTH), 9)

        self.chadwick.add_path(((1, 12), Direction.NORTH), ((1, 13), Direction.SOUTH), 12)
        self.chadwick.add_path(((1, 12), Direction.WEST), ((0, 12), Direction.EAST), 20)

        self.chadwick.add_path(((1, 13), Direction.WEST), ((0, 12), Direction.NORTH), 6)
        self.chadwick.add_path(((1, 13), Direction.NORTH), ((0, 14), Direction.EAST), 7)

        self.chadwick.add_path(((0, 14), Direction.SOUTH), ((0, 14), Direction.SOUTH), 1)
        self.chadwick.add_path(((0, 14), Direction.WEST), ((1, 14), Direction.WEST), -1)

        self.chadwick.add_path(((0, 12), Direction.WEST), ((-1, 12), Direction.EAST), 5)
        self.chadwick.add_path(((0, 12), Direction.SOUTH), ((0, 11), Direction.NORTH), 7)

        self.chadwick.add_path(((0, 11), Direction.WEST), ((-1, 11), Direction.EAST), 3)
        self.chadwick.add_path( ((0, 11), Direction.SOUTH), ((-1, 10), Direction.EAST), 1)

        self.chadwick.add_path( ((-1, 11), Direction.SOUTH), ((-1, 10), Direction.NORTH), 8)
        self.chadwick.add_path(((-1, 11), Direction.NORTH), ((-1, 12), Direction.SOUTH), 1)

        self.chadwick.add_path(((-1, 12), Direction.NORTH), ((-1, 12), Direction.NORTH), -1)

    def setup_anin(self):

        self.anin = Planet()

        self.anin.add_path(((15, 2), Direction.SOUTH), ((15, 2), Direction.SOUTH), -1)

        # simulate station scan on (15, 2)
        self.anin.add_possible_unexplored_path(((15, 2), Direction.NORTH))
        self.anin.add_possible_unexplored_path(((15, 2), Direction.EAST))
        self.anin.add_possible_unexplored_path(((15, 2), Direction.WEST))

        self.anin.add_path(((15, 2), Direction.NORTH), ((15, 2), Direction.EAST), 1)

        # simulate station scan on (15, 2) - since our robo doesnt store already scanned nodes
        self.anin.add_possible_unexplored_path(((15, 2), Direction.NORTH))
        self.anin.add_possible_unexplored_path(((15, 2), Direction.EAST))
        self.anin.add_possible_unexplored_path(((15, 2), Direction.WEST))

        # drive to (13, 2)
        self.anin.add_path(((15, 2), Direction.WEST), ((13, 2), Direction.EAST), 2)

        # station scan at (13, 2)
        self.anin.add_possible_unexplored_path((13, 2), Direction.NORTH)
        self.anin.add_possible_unexplored_path((13, 2), Direction.WEST)
        # mothership unveals paths D
        self.anin.add_path(((13, 2), Direction.SOUTH), ((13, 2), Direction.SOUTH), -1)
        self.anin.add_path(((13, 4), Direction.SOUTH), ((14, 4), Direction.SOUTH), 4)
        self.anin.add_path(((13, 4), Direction.SOUTH), ((14, 4), Direction.SOUTH), 1)
        self.anin.add_path(((14, 4), Direction.NORTH), ((15, 5), Direction.SOUTH), 1)

        # drive to (13, 4)
        self.anin.add_path(((13, 2), Direction.WEST), ((13, 4), Direction.WEST), 2)
        # scan (13, 4)
        self.anin.add_possible_unexplored_path((13, 4), Direction.EAST)
        self.anin.add_possible_unexplored_path((13, 4), Direction.SOUTH)
        self.anin.add_possible_unexplored_path((13, 4), Direction.NORTH)

        # TODO: mothership unveals E
    def setup_loop(self):
        self.loop = Planet()
        # (0,0)
        self.loop.add_path(((0, 0), Direction.NORTH), ((0, 1), Direction.SOUTH), 1)
        self.loop.add_path(((0, 0), Direction.EAST), ((1, 0), Direction.WEST), 1)
        # (0,1)
        self.loop.add_path(((0, 1), Direction.SOUTH), ((0, 0), Direction.NORTH), 1)
        self.loop.add_path(((0, 1), Direction.EAST), ((1, 1), Direction.WEST), 1)
        # (1,1)
        self.loop.add_path(((1, 1), Direction.WEST), ((0, 1), Direction.EAST), 1)
        self.loop.add_path(((1, 1), Direction.SOUTH), ((1, 0), Direction.NORTH), 1)
        self.loop.add_path(((1, 1), Direction.NORTH), ((1, 2), Direction.SOUTH), 1)
        # (1,0)
        self.loop.add_path(((1, 0), Direction.NORTH), ((1, 1), Direction.SOUTH), 1)
        self.loop.add_path(((1, 0), Direction.WEST), ((0, 0), Direction.EAST), 1)
        # (1,2)
        self.loop.add_path(((1, 2), Direction.SOUTH), ((1, 1), Direction.NORTH), 1)
        self.loop.add_path(((1, 2), Direction.NORTH), ((1, 3), Direction.SOUTH), 1)
        # (1,3)
        self.loop.add_path(((1, 3), Direction.SOUTH), ((1, 2), Direction.NORTH), 1)

    def setup_john(self):
        """
        Inits planet John
        """
        self.john = Planet()

        self.add_path

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
        self.__test_target_chadwick()

    def __test_target_chadwick(self):
        """
        call self.planet._Planet__djikstra() to get weight of shortest path
        """

        # 1st test case(easy):
        start = (1, 10)
        target = (0, 14)

        shortest_path1 = self.chadwick.get_shortest_path(start, target)

        shortest_path_should1 = [
            ((1, 10), Direction.NORTH), ((1, 12), Direction.NORTH),
            ((1, 13), Direction.NORTH), ((0, 14), None)
        ]
        self.assertEqual(shortest_path1, shortest_path_should1)

        # 2nd test case(medium):
        start = (-1, 10)
        target = (1, 13)

        shortest_path2 = self.chadwick.get_shortest_path(start, target)
        shortest_path_should2 = [
            ((-1, 10), Direction.EAST), ((0, 11), Direction.NORTH),
            ((0, 12), Direction.NORTH), ((1, 13), None)
        ]
        self.assertEqual(shortest_path2, shortest_path_should2)

    def test_target_not_reachable(self):
        """
        This test should check that a target outside the map or at an unexplored node is not reachable
        """
        self.planet_unreachable = Planet()
        self.planet_unreachable.add_path(((0, 0), Direction.NORTH), ((0, 0), Direction.NORTH), -1)
        self.planet_unreachable.add_path(((0, 0), Direction.SOUTH), ((0, 0), Direction.SOUTH), -1)

        self.planet_unreachable.add_path(((0, 1), Direction.SOUTH), ((0, 1), Direction.SOUTH), -1)

        start = (0, 0)
        target = (0, 1)
        shortest_path = self.planet_unreachable.get_shortest_path(start, target)

        self.assertIsNone(shortest_path)

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
        self.setup_loop()
        start = (0, 0)
        target = (1, 3)
        shortest_path = self.loop.get_shortest_path(start, target)
        
        shortest_path_should1 = [
            ((0, 0), Direction.NORTH), ((0, 1), Direction.EAST), ((1, 1, Direction.NORTH)), ((1, 2), Direction.NORTH), ((1, 3), None)
        ]
        shortest_path_should2 = [
            ((0, 0), Direction.EAST), ((1, 0), Direction.NORTH), ((1, 1), Direction.NORTH), ((1, 2), Direction.NORTH), ((1, 3), None)
        ]
        self.assertEqual(shortest_path, shortest_path_should1)
        self.assertEqual(shortest_path, shortest_path_should2)
        
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

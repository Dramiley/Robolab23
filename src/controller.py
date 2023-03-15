"""
OUR VERSION:
At every communication point:
    0. check whether missed an incoming target request
        ->if yes, set self.target to received target
    1. check if target is set
        -> if it is, compute shortest path and select next path based on that shortest path
        -> else: get_next_exploration_dir
            ->if None->finished!!!
    2. contact station and tell chosen next path
    3. drive the path we are told by the mothership

COMPLEX:
- advantage: no unneccasry djikstra computation
At every communication point:
    0. check whether missed an incoming target request
    1. select next path
        - if no target, currently not following a path and not exploring -> finished!!!
        ->if new target came in: compute shortest_path and choose next path based on it
        - if are currently following a path: choose the path we need to take to follow that path
        - else: choose a dir to continue exploring in (first get_next_exploring path if not already at an unexplored node)
    2. contact station and tell chosen next path
    3. receive path given by station and check with selected one
        - if i am in target mode: if given one != selected one -> recompute shortest path (for the next node we'll drive to)
        - follow given path to next communication point

TODO: register unexplored dirs (when robot turns around on a node) on __get_unexplored_paths()

TODO: add odometry into robot's movement??
TODO: update dir of self.last_position everytime we tell the robot to rotate
"""

import time
import os
import sys
import math
import pdb
import logging

from communication import Communication
from communication_logger import CommunicationLogger
from odometry import Odometry
from robot import Robot
from robot_dummy import RobotDummy
from planet import Planet, Direction

from typing import List, Tuple
from threading import Thread

# DONT CHANGE ANYTHING HERE, ONLY IN .env
# Bitte nicht hierdrinne verändern, sondern in der src/.env setzen.
# siehe https://se-gitlab.inf.tu-dresden.de/robolab-spring/ws2022/group-046/-/blob/master/README.md#example-for-development-purposes
env = {"SIMULATOR": False, "DEBUG": False, "GITLAB_RUNNER": False}

if os.path.exists(".env"):
    with open(".env") as f:
        for line in f:
            key, value = line.split("=")
            value = value.replace("\n", "")
            if value == "True" or value == "False":
                env[key] = value == "True"
            else:
                env[key] = value

# if script was called with a parameter, use it as the environment
if len(sys.argv) > 1 and sys.argv[1] == "ci":
    print("Running in CI mode")
    env["GITLAB_RUNNER"] = True
    env["SIMULATOR"] = True
    env["DEBUG"] = True

"""
TODO: self.odometry.stop()
"""


class Position:
    x, y, direction = 0, 0, 0

    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction


class Controller:
    robot = None
    communication = None
    odometry = None
    planet = None
    last_position = Position(0, 0, 0)  # updated by received msg from mothership or rotations by rob

    given_new_target = False  # tracks whether we have a target to drive to by the mothership
    target_pos = None

    path_to_drive = []  # stores the path we have to drive (drive path->pop first elem->ask mothership whether path should be followed on)
    history = []

    def __init__(self, client):

        # setup communication
        self.communication = Communication(client, CommunicationLogger()).facade

        # setup error handling
        self.communication.set_callback('error', lambda message: print("COMM. FEHLER GEMELDET: " + message))

        self.communication.test_planet('Fassaden-M1')

        # for our Simulator
        if env["SIMULATOR"]:
            self.robot = RobotDummy()
        else:
            self.robot = Robot()
        self.robot.set_controller(self)

        # setup callbacks
        self.__init_callbacks()

    def begin(self):
        print("Controller started")

        # Euer Roboter wird vom Mutterschiff auf einem fernen Planeten nahe einer beliebigen Versorgungsstation
        # abgesetzt, Anfahrtsweg fahren
        self.robot.drive_until_communication_point()

        # teilt dem Mutterschiff mit, dass er bereit zur Erkundung ist
        self.communication.ready()

        # then we wait for planet msg->ready() only exits when everything is over

        # as long as the programm is not exited, wait for callbacks
        # but if we are in CI mode, exit right away since we tested everything
        if not env["GITLAB_RUNNER"]:
            while True:
                time.sleep(1)

    def run(self):
        """
        Runs the actual robot
        ->decision-making

        Called arrive at a communication point

        At every communication point:
            0. check whether missed an incoming target request (done implicitly by communication which then calls .receive_target(), right?? @ Dominik)
                ->if yes, set self.target to received target
            1. check if target is set
                -> if it is, compute shortest path and select next path based on that shortest path
                -> else: get_next_exploration_dir
                    ->if None->finished!!!
            2. contact station and tell chosen next path
            3. drive the path we are told by the mothership
        """
        self.__check_explorable_paths()

        selected_dir_next = 0
        if self.target_pos != None:
            # we have a given target we need to drive to
            last_pos = (self.last_position.x, self.last_position.y)
            shortest_path = self.planet.get_shortest_path(last_pos, self.target)  # =List[Tuple[pos, dir]]

            if shortest_path == []:
                # we are already at target
                # TODO: check whether programs really ends here (see https://robolab.inf.tu-dresden.de/spring/task/communication/msg-complete/)
                self.__target_reached()
            elif shortest_path == None:
                # target is unreachable
                # TODO: what if we had a target and received an unreachable one->we don't have any target anymore, right?
                target = None
                next_dir = self.__explore()
            else:
                next_dir = shortest_path[0][1]
        else:
            next_dir = self.__explore()

        self.communication.path_select(self.last_position.x, self.last_position.y, next_dir)
        # actual movement is performed on receive_path_select :)

    def __explore(self) -> Direction:
        """
        Let the robo have some fun and explore the planet on it's own
        """
        next_dir = self.planet.get_next_exploration_dir()

        if next_dir == None:
            # planet has been explored completely->there is nothing to explore anymore
            self.communication.exploration_completed()
            return

        return next_dir

    def __init_callbacks(self):
        # bei einer Antwort des Mutterschiffs mit dem Typ "planet" wird der Name des Planeten ausgegeben
        self.communication.set_callback('planet', self.receive_planet)

        # bei einer Antwort des Mutterschiffs mit dem Typ "path" wird der Pfad ausgegeben
        self.communication.set_callback('path', self.receive_path)

        # bei einer Antwort des Mutterschiffs mit dem Typ "path-unveiled" wird der Pfad ausgegeben
        self.communication.set_callback('pathUnveiled', self.receive_path_unveiled)

        # In einigen Fällen kann es vorkommen, dass dem Mutterschiff günstigere Routen oder Hindernisse bekannt sind.
        # In diesem Fall weist das Mutterschiff den Roboter an, einen anderen Pfad zu befahren
        self.communication.set_callback('pathSelect', self.receive_path_select)

        # Zusätzlich zu den Planetennachrichten empfängt der Roboter an Kommunikationspunkten auch Befehle vom
        # Mutterschiff.
        self.communication.set_callback('target', self.receive_target)

        # Wurde das Ziel tatsächlich erreicht bzw. die gesamte Karte aufgedeckt, antwortet der Server mit einer
        # Bestätigung vom Typ done (3) und dem Ende der Erkundung.
        self.communication.set_callback('done', self.receive_done)

    def receive_planet(self, planetName, startX, startY, startOrientation):
        """
        Called when we have received the planet from the mothership (only once!)
        """

        # remember last position
        self.last_position = Position(startX, startY, startOrientation)

        # setup planet
        self.planet = Planet()

        # setup odometry
        self.odometry = Odometry(self.robot)
        self.odometry.set_coords((startX, startY))
        self.odometry.set_dir(startOrientation)

        # aktuelle position um 180 grad gedreht als blockiert merken
        # ->because we always start from a dead end
        self.planet.add_path((startX, startY), (startX, startY), int(startOrientation) + 180)

        # los gehts
        self.run()

    def __check_explorable_paths(self):
        """
        Explores all paths from the current node

        Registers unexplored paths in planet

        TODO: don't scan nodes which are already explored completely
        """
        start_dir = self.last_position.direction  # the direction we came from
        current_dir = (start_dir+180) % 360 # sensor is no on opposite path since we drove forward
        self.last_position.direction = current_dir

        logging.debug(f("Started scan from {start_dir}, set scan dir to {current_dir} due to driving forward."))
        # check all paths
        for i in range(0, 3):  # 1 because there must be a path on the one we came from
            # TODO: 2nd rotation scans the path we came from (not needed!)

            # update current orientation by 90deg
            current_dir = (current_dir + 90) % 360
            # check whether there is a path
            possible_path = self.robot.station_scan()

            if possible_path:
                self.planet.add_possible_unexplored_path((self.last_position.x, self.last_position.y), current_dir)
            logging.debug(f"Checking {current_dir}")
        pdb.set_trace()

    def communication_point_reached(self):
        """
        An jedem weiteren Kommunikationspunkt übermittelt der Roboter zu Beginn der Übertragung den gefahrenen Pfad.
        Dieser besteht aus Start- und Zielkoordinaten sowie den jeweiligen Himmelsrichtungen.
        Mithilfe der Odometrie schätzt er dabei seine neue Position ab.
        :return: void
        """
        # only track when following a line
        self.odometry.stop()
        # calculate start and end position
        start_position = self.last_position
        end_position = self.odometry.get_coords()

        is_path_blocked = self.robot.was_path_blocked

        if is_path_blocked:
            path_status = "blocked"
        else:
            path_status = "free"

        # send path to mothership for verification
        self.communication.path(start_position.x, start_position.y, start_position.direction, end_position.x,
                                end_position.y, end_position.direction, path_status)

    def __target_reached(self):
        """
        Wird von der Odometrie aufgerufen, wenn das Ziel erreicht wurde
        """
        self.communication.target_reached("Target reached.")

    def __exploration_complete(self):
        """
        Wird von der Odometrie aufgerufen, wenn die Erkundung abgeschlossen ist
        """
        self.communication.exploration_completed("Exploration completed.")

    def receive_path(self, startX, startY, startOrientation, endX, endY, endOrientation, pathStatus, pathWeight):
        """
        Das Mutterschiff bestätigt die Nachricht des Roboters, wobei es gegebenenfalls eine Korrektur in den Zielkoordinaten vornimmt (2). Es berechnet außerdem das Gewicht eines Pfades und hängt es der Nachricht an.
        siehe https://robolab.inf.tu-dresden.de/spring/task/communication/msg-path/
        """

        # init odometry
        self.odometry.set_coords((startX, startY))
        self.odometry.set_dir(startOrientation)

        # update odometry inside planet
        self.planet.add_path(((startX, startY), startOrientation), ((endX, endY), endOrientation), pathWeight)

        # update last position and path status
        self.last_position = Position(endX, endY, endOrientation)

        # don't drive to next communication point yet, because we want to receive path select messages first
        # instead find paths and ask mothership to select one
        # TODO: drive into received direction!

    def receive_path_unveiled(self, startX, startY, startOrientation, endX, endY, endOrientation, pathStatus,
                              pathWeight):
        """
        Zusätzlich zur immer gesendeten Bestätigung bzw. Korrektur mit Gewichtung können weitere Nachrichten empfangen werden. Hierbei werden neue Pfade aufgedeckt, die durch andere Roboter bereits erkundet wurden, oder auch bereits erkundete Strecken gesperrt (bspw. durch einen Meteoriteneinschlag).
        Dies ermöglicht es Eurem Roboter, schneller mit der Erkundung fertig zu werden, da er die empfangenen Pfade direkt in seine Karte aufnimmt und nicht erkunden muss.
        siehe https://robolab.inf.tu-dresden.de/spring/task/communication/msg-unveiled/
        """

        # TODO: check
        self.planet.add_path(((startX, startY), startOrientation), ((endX, endY), endOrientation), pathWeight)
        # self.odometry.receive_path_unveiled(startX, startY, startOrientation, endX, endY, endOrientation, pathStatus, pathWeight)

    def receive_path_select(self, startDirection: Direction):
        """
        Drive into given dir

        Das Mutterschiff bestätigt die Nachricht des Roboters, wobei es gegebenenfalls eine Korrektur in den Zielkoordinaten vornimmt (2). Es berechnet außerdem das Gewicht eines Pfades und hängt es der Nachricht an.
        siehe https://robolab.inf.tu-dresden.de/spring/task/communication/msg-select/
        """

        # update last position and path status
        self.odometry.set_dir(startDirection)

        self.__rotate_robo_in_dir(startDirection)

        # now we can finally drive to the next communication point
        self.odometry.start()
        self.robot.drive_until_communication_point()

    def receive_target(self, x, y):
        """
        Zusätzlich zu den Planetennachrichten empfängt der Roboter an Kommunikationspunkten auch Befehle vom Mutterschiff.
        Eine Nachricht vom Typ target (1) erteilt dem Roboter den Auftrag, auf kürzestem Weg die angegebenen Koordinaten anzufahren, sofern er diesen anhand seiner aktuellen Karte berechnen kann. Sollte dies nicht möglich sein, wird das Ziel vermerkt und die Erkundung normal fortgesetzt, bis eine solche Berechnung möglich ist oder das Ziel erreicht wurde.
        Falls das Ziel ausserhalb der erkundbaren Karte liegt, kann bereits nach erfolgreicher Planetenerkundung eine Erfolgsmeldung an das Mutterschiff gesendet werden.
        siehe https://robolab.inf.tu-dresden.de/spring/task/communication/msg-target/
        """

        # get last position
        last_position = self.last_position

        # store received info
        self.target = (x, y)

    def __rotate_robo_in_dir(self, target_dir: Direction):
        """
        Tells the robo which way to rotate in order to be oriented in target_dir
        """
        # TODO: make sure robot.turn_deg deals appropriately with neg. values
        current_dir = self.last_position.direction
        # TODO: robot currently would rotate 270° instead of -90°->unefficient!!!!
        deg_to_rotate = current_dir - target_dir
        self.robot.turn_deg(deg_to_rotate)

    def receive_done(self, message):
        """
        Wurde das Ziel tatsächlich erreicht bzw. die gesamte Karte aufgedeckt, antwortet der Server mit einer Bestätigung vom Typ done (3) und dem Ende der Erkundung.
        """
        print("Done.")
        print("Message: " + message)
        self.robot.__stop()
        self.communication.done()

    def __tuple_to_position(self, tuple):
        x, y = tuple[0]
        direction = tuple[1]
        return Position(x, y, direction)

    def __position_to_tuple(self, position):
        return ((position.x, position.y), int(position.direction))

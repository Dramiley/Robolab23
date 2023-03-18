"""
OUR VERSION:
At every communication point:
    0. check whether missed an incoming target request
        ->if yes, set self.target_pos to received target
    1. check if target is set
        -> if it is, compute shortest path and select next path based on that shortest path
        -> else: get_next_exploration_dir
            ->if None->finished!!!
    2. contact station and tell chosen next path
    3. drive the path we are told by the mothership
"""
import json
import threading
import time
import os
import sys
import logging
import pdb
from typing import Optional

from ev3dev.core import Sound

from communication import Communication
from odometry import Odometry
from planet import Planet, Direction


class Position:
    x, y, direction = 0, 0, 0

    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction


class Controller:

    def __init__(self, client):
        self.next_dir = None

        self.robot = None
        self.communication = None
        self.odometry = None
        self.planet = None
        self.last_position = None  # stores the last position we were at
        self.target_pos = None

        # setup communication
        self.communication = Communication(client, None).facade

        # setup error handling
        self.communication.set_callback('error', lambda message: print("COMM. FEHLER GEMELDET: " + message))

        test_planet = "Schoko"
        self.communication.test_planet(test_planet)

        from robot import Robot
        self.robot = Robot()
        self.robot.calibrate()
        self.robot.set_controller(self)

        # setup callbacks
        self.__init_callbacks()

    def begin(self):

        # Euer Roboter wird vom Mutterschiff auf einem fernen Planeten nahe einer beliebigen Versorgungsstation
        # abgesetzt, Anfahrtsweg fahren
        self.robot.begin()

        self.communication.ready()

        while True:
            time.sleep(1)

    def select_next_dir(self):
        print("select_next_dir")
        """
        Runs the actual robot
        ->decision-making

        Called arrive at a communication point

        At every communication point:
            0. check whether missed an incoming target request (done implicitly by communication which then calls .receive_target(), right?? @ Dominik)
                ->if yes, set self.target_pos to received target
            1. check if target is set
                -> if it is, compute shortest path and select next path based on that shortest path
                -> else: get_next_exploration_dir
                    ->if None->finished!!!
            2. contact station and tell chosen next path
            3. drive the path we are told by the mothership
        """

        # let robot check paths on the node he is on and register it in planet.unexplored
        print("will call check_explorable_paths")
        self.__check_explorable_paths()
        # pdb.set_trace()

        print("now evaluating after check_explorable_paths")
        next_dir = None
        if self.target_pos != None:
            # we have a given target we need to drive to
            last_pos = (self.last_position.x, self.last_position.y)
            shortest_path = self.planet.get_shortest_path(last_pos, self.target_pos)  # =List[Tuple[pos, dir]]

            if shortest_path == []:
                # we are already at target
                # TODO: check whether programs really ends here (see https://robolab.inf.tu-dresden.de/spring/task/communication/msg-complete/)
                self.__target_reached()
            elif shortest_path == None:
                # target is unreachable
                # TODO: what if we had a target and received an unreachable one->we don't have any target anymore, right?
                self.target_pos = None
                next_dir = self.__explore()
            else:
                next_dir = shortest_path[0][1]
        else:
            next_dir = self.__explore()

        print("Next dir: " + str(next_dir))
        print("Last pos: " + str(self.last_position.x) + " " + str(self.last_position.y))

        # NOTE: check that robo selected right path here!
        # pdb.set_trace()

        print("will publish path_select/")
        self.communication.path_select(self.last_position.x, self.last_position.y, next_dir)
        # actual movement is performed on receive_path_select :)

        self.next_dir = next_dir
        time.sleep(3.2)
        self.drive_to_next_dir()


    def __explore(self) -> Optional[Direction]:

        # TODO fix it
        """
        Let the robo have some fun and explore the planet on it's own
        """
        print("self.planet.unexplored: " + str(self.planet.unexplored))
        next_dir = self.planet.get_next_exploration_dir((self.last_position.x, self.last_position.y))

        if next_dir == None:
            # planet has been explored completely->there is nothing to explore anymore
            self.communication.exploration_completed()
            return None

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

    def receive_planet(self, planetName: str, startX: int, startY: int, startOrientation: Direction):
        """
        Called when we have received the planet from the mothership (only once!)
        """

        # remember last position
        print("settings last position to " + str(startX) + " " + str(startY) + " " + str(startOrientation))
        self.last_position = Position(startX, startY, startOrientation)

        # setup planet
        self.planet = Planet()

        # setup odometry
        self.odometry = Odometry(self.robot)
        self.odometry.set_coords((startX, startY))
        self.odometry.set_dir(startOrientation)

        print("Init position: " + str(startX) + " " + str(startY) + " " + str(startOrientation))
        # aktuelle position um 180 grad gedreht als blockiert merken
        # ->because we always start from a dead end
        self.__handle_received_planet(startX, startY, Direction(startOrientation))

        # TODO Robin Change: Wurde bereits in Begin aufgerufen. Dadurch hat der Roboter drive_until_communication_point() 2 mal ausgeführt
        # los gehts

        self.select_next_dir()  # undo alex's change to begin()

    def __handle_received_planet(self, startX: int, startY: int, startOrientation: Direction):

        # startOrientation is the dir the robot is pointing towards after entering the node
        came_from_dir = Direction((startOrientation + 180) % 360)
        # came_from_dir = Direction((startOrientation) % 360)
        # mark start path as blocked (is always a dead end)
        self.planet.add_path(((startX, startY), came_from_dir), ((startX, startY), came_from_dir), -1)

    def __check_explorable_paths(self):
        """
        Explores all paths from the current node

        Registers unexplored paths in planet

        WARNING: make sure self.last_position.direction is updated before calling this func!
        TODO: don't scan nodes which are already explored completely
        """
        print("last_position.direction: " + str(self.last_position.direction))
        start_dir = self.last_position.direction  # the direction we came from

        print(f"Started scan from {start_dir}, set scan dir to {self.last_position.direction} due to driving forward.")
        # check all paths
        for i in range(0, 4):  # 1 because there must be a path on the one we came from

            # TODO: 2nd rotation scans the path we came from (not needed!)
            # update current orientation by 90deg
            self.last_position.direction = (self.last_position.direction + 90) % 360
            current_dir = self.last_position.direction
            # check whether there is a path
            possible_path = self.robot.station_scan()

            time.sleep(3)

            if i == 1:
                # we already know that there is a path on the one we came from
                continue

            if possible_path:
                print("found possible path in dir " + str(current_dir))
                try:
                    self.planet.add_possible_unexplored_path((self.last_position.x, self.last_position.y),
                                                             current_dir)
                except Exception as e:
                    print(f"Error while adding path to planet: {e}")
            else:
                print("found no path in dir " + str(current_dir))

        print(f"Currently unexplored: {self.planet.unexplored}")

    def communication_point_reached(self):
        """
        An jedem weiteren Kommunikationspunkt übermittelt der Roboter zu Beginn der Übertragung den gefahrenen Pfad.
        Dieser besteht aus Start- und Zielkoordinaten sowie den jeweiligen Himmelsrichtungen.
        Mithilfe der Odometrie schätzt er dabei seine neue Position ab.
        :return: void
        """

        if (self.last_position is None):
            return

        # calculate start and end position
        start_position = self.last_position

        end_position = None
        self.odometry.calculate(self.robot.motor_pos_list)
        end_coords = self.odometry.get_coords()
        print("Odometrie says we are at " + str(end_coords[0]) + " " + str(end_coords[1]))
        end_position = Position(self.odometry.get_coords()[0], self.odometry.get_coords()[1],
                                self.odometry.get_dir())

        is_path_blocked = self.robot.was_path_blocked

        if is_path_blocked:
            path_status = "blocked"
        else:
            path_status = "free"

        # send path to mothership for verification
        print("will publish path/")
        self.communication.path(start_position.x, start_position.y, start_position.direction, end_position.x,
                                end_position.y, end_position.direction, path_status)

    def __target_reached(self):
        """
        Wird aufgerufen, wenn das Ziel erreicht wurde
        """
        self.communication.target_reached("Target reached.")
        self.target_pos = None

    def receive_path(self, startX, startY, startDirection, endX, endY, endDirection, pathStatus, pathWeight):
        # pass onto handler, forget pathStatus
        # self.__handle_received_path(startX, startY, startDirection, endX, endY, endDirection, pathWeight)
        # call __handle_received_path in own thread
        threading.Thread(target=self.__handle_received_path,
                         args=(startX, startY, startDirection, endX, endY, endDirection, pathWeight)).start()

    def __handle_received_path(self, startX, startY, startDirection, endX, endY, endDirection, pathWeight):
        """
         Das Mutterschiff bestätigt die Nachricht des Roboters, wobei es gegebenenfalls eine Korrektur in den Zielkoordinaten vornimmt (2). Es berechnet außerdem das Gewicht eines Pfades und hängt es der Nachricht an.
         siehe https://robolab.inf.tu-dresden.de/spring/task/communication/msg-path/
         """

        # init odometry
        self.odometry.set_coords((startX, startY))
        self.odometry.set_dir(startDirection)

        # update odometry inside planet
        self.planet.add_path(((startX, startY), Direction(startDirection)), ((endX, endY), Direction(endDirection)),
                             pathWeight)
        print(f"Added a path, now we know the following paths: {self.planet.paths}")

        # update last position and path status
        print("last_position: " + str(self.last_position.x) + " " + str(self.last_position.y) + " " + str(
            self.last_position.direction))
        print("__handle_received_path: " + str(endX) + " " + str(endY) + " " + str(endDirection))
        current_dir = (endDirection + 180) % 360  # we now look at to the opposite direction than we entered the node
        print("calculation of current_dir: (" + str(endDirection) + " + 180) % 360 = " + str(current_dir))
        self.last_position = Position(endX, endY, current_dir)
        print("last_position set to: " + str(self.last_position.x) + " " + str(self.last_position.y) + " " + str(
            self.last_position.direction))

        # don't drive to next communication point yet, because we want to receive path select messages first
        # instead find paths and ask mothership to select one
        self.select_next_dir()

    def receive_path_unveiled(self, startX, startY, startDirection, endX, endY, endDirection, pathStatus,
                              pathWeight):
        """
        Zusätzlich zur immer gesendeten Bestätigung bzw. Korrektur mit Gewichtung können weitere Nachrichten empfangen werden. Hierbei werden neue Pfade aufgedeckt, die durch andere Roboter bereits erkundet wurden, oder auch bereits erkundete Strecken gesperrt (bspw. durch einen Meteoriteneinschlag).
        Dies ermöglicht es Eurem Roboter, schneller mit der Erkundung fertig zu werden, da er die empfangenen Pfade direkt in seine Karte aufnimmt und nicht erkunden muss.
        siehe https://robolab.inf.tu-dresden.de/spring/task/communication/msg-unveiled/
        """

        # TODO: check
        self.planet.add_path(((startX, startY), startDirection), ((endX, endY), endDirection), pathWeight)

    def receive_path_select(self, startDirection: Direction):
        self.next_dir = startDirection

    def drive_to_next_dir(self):
        startDirection = self.next_dir

        print("received path select: " + str(startDirection) + " at current time: " + str(time.time()))

        """
        Drive into given dir

        Das Mutterschiff bestätigt die Nachricht des Roboters, wobei es gegebenenfalls eine Korrektur in den Zielkoordinaten vornimmt (2). Es berechnet außerdem das Gewicht eines Pfades und hängt es der Nachricht an.
        siehe https://robolab.inf.tu-dresden.de/spring/task/communication/msg-select/
        """
        self.communication.communication.received_since_last_path_select = 1
        # NOTE: Make sure robo received the right path_select (ESPECIALLY NOT the fake server response)

        print(f"Driving to {startDirection}")

        # update last position and path status
        self.odometry.set_dir(startDirection)

        print(f"Start dir: {self.last_position.direction}, Rotating to: {startDirection}")

        self.rotate_robo_in_dir(Direction(startDirection))
        print(startDirection)
        self.robot.drive_until_communication_point()

        print("Done with receive_path_select")

    """
        self.__handle_receive_path_select(startDirection)

    def __handle_receive_path_select(self, startDirection):
        def async_please():
            self.rotate_robo_in_dir(startDirection)
            print(startDirection)
            self.robot.drive_until_communication_point()
            print("Done with receive_path_select > async_please")

        self.thread = threading.Thread(target=async_please, args=())
        self.thread.start()
    """

    def receive_target(self, targetX, targetY):
        """
        Zusätzlich zu den Planetennachrichten empfängt der Roboter an Kommunikationspunkten auch Befehle vom Mutterschiff.
        Eine Nachricht vom Typ target (1) erteilt dem Roboter den Auftrag, auf kürzestem Weg die angegebenen Koordinaten anzufahren, sofern er diesen anhand seiner aktuellen Karte berechnen kann. Sollte dies nicht möglich sein, wird das Ziel vermerkt und die Erkundung normal fortgesetzt, bis eine solche Berechnung möglich ist oder das Ziel erreicht wurde.
        Falls das Ziel ausserhalb der erkundbaren Karte liegt, kann bereits nach erfolgreicher Planetenerkundung eine Erfolgsmeldung an das Mutterschiff gesendet werden.
        siehe https://robolab.inf.tu-dresden.de/spring/task/communication/msg-target/
        """
        # store received info
        self.target_pos = (targetX, targetY)

    def rotate_robo_in_dir(self, target_dir: Direction):
        """
        Tells the robo which way to rotate in order to be oriented in target_dir
        """
        # TODO: make sure robot.turn_deg deals appropriately with neg. values
        current_dir = self.last_position.direction
        # TODO: robot currently would sometimes rotate more than necessary (e.g. target_dir=270, current_dir=0)
        deg_to_rotate = (target_dir - current_dir) % 360

        while deg_to_rotate > 0:
            # use station scan for rotating bc turn_deg is VERY buggy
            self.robot.station_scan()
            deg_to_rotate -= 90

        self.last_position.direction = target_dir

    def receive_done(self, message):
        """
        Wurde das Ziel tatsächlich erreicht bzw. die gesamte Karte aufgedeckt, antwortet der Server mit einer Bestätigung vom Typ done (3) und dem Ende der Erkundung.
        """
        print("Done.")
        print("Message: " + message)
        self.robot.__stop()
        self.communication.done()

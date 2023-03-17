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
import json
import time
import os
import sys
import logging
import pdb
from typing import Optional

# DONT CHANGE ANYTHING HERE, ONLY IN .env
# Bitte nicht hierdrinne verändern, sondern in der src/.env setzen.
# siehe https://se-gitlab.inf.tu-dresden.de/robolab-spring/ws2022/group-046/-/blob/master/README.md#example-for-development-purposes
env = {"SIMULATOR": False, "DEBUG": False, "GITLAB_RUNNER": False, "ODOMETRY": True, "ROBIN_MODE": False}

__current_dir = os.path.dirname(os.path.realpath(__file__))
print(__current_dir)
if os.path.exists(__current_dir + "/.env"):
    with open(__current_dir + "/.env") as f:
        for line in f:
            # if line is empty, skip it
            if line == "\n":
                continue
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

__current_dir = os.path.dirname(os.path.realpath(__file__))


def simulator_log(log_type, log_dict):
    if not env["SIMULATOR"]:
        return

    # set payload type
    log_dict["type"] = log_type

    # append to history file (which contains an array of positions)
    from lockfile import LockFile
    lock = LockFile(__current_dir + "/simulator/history.json.lock")
    with lock:
        time.sleep(0.001)

    lock.acquire()
    with open(__current_dir + '/simulator/history.json', 'r+') as outfile:
        try:
            data = json.load(outfile)
        except:
            data = []

        # append to array
        data.append(log_dict)

        # write to file
        outfile.seek(0)
        json.dump(data, outfile)
    lock.release()


class Position:
    x, y, direction = 0, 0, 0

    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction


from communication import Communication
from communication_logger import CommunicationLogger
from odometry import Odometry
from planet import Planet, Direction


class Controller:
    robot = None
    communication = None
    odometry = None
    planet = None
    last_position = None  # stores the last position we were at

    given_new_target = False  # tracks whether we have a target to drive to by the mothership
    target_pos = None

    path_to_drive = []  # stores the path we have to drive (drive path->pop first elem->ask mothership whether path should be followed on)
    history = []

    def __init__(self, client):

        # setup communication
        self.communication = Communication(client, CommunicationLogger()).facade

        # setup error handling
        self.communication.set_callback('error', lambda message: print("COMM. FEHLER GEMELDET: " + message))

        # load test planet name from planets/current.txt
        __current_dir = os.path.dirname(os.path.realpath(__file__))
        with open(__current_dir + '/simulator/planets/current.txt') as f:
            self.communication.test_planet(f.read().replace("\n", ""))

        # for our Simulator
        if env["SIMULATOR"]:
            from robot_dummy import RobotDummy
            self.robot = RobotDummy()
            self.robot.calibrate()
        else:
            from robot import Robot
            self.robot = Robot()
        self.robot.set_controller(self)

        # setup callbacks
        self.__init_callbacks()

        # self.logger = logging.getLogger(__name__)
        self.logger = self.communication.communication.logger

        self.logger.setLevel(logging.DEBUG)

    def begin(self):
        print("controller.begin()")

        # Euer Roboter wird vom Mutterschiff auf einem fernen Planeten nahe einer beliebigen Versorgungsstation
        # abgesetzt, Anfahrtsweg fahren
        if not env["SIMULATOR"]:
            self.robot.begin()
        else:
            print(
                "Simulator: skipping drive_until_communication_point(), because we'll already be at an communication point")

        self.communication.ready()
        time.sleep(1)
        self.select_next_dir()

        if not env["GITLAB_RUNNER"]:
            while True:
                time.sleep(1)

    def select_next_dir(self):
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
        self.logger.debug("Entering run")

        # let robot check paths on the node he is on and register it in planet.unexplored
        self.__check_explorable_paths()

        next_dir = None
        self.logger.debug("Selecting the next dir to take...")
        if self.target_pos != None:
            self.logger.debug(f"I have to drive to target at {self.target_pos}")
            # we have a given target we need to drive to
            last_pos = (self.last_position.x, self.last_position.y)
            shortest_path = self.planet.get_shortest_path(last_pos, self.target_pos)  # =List[Tuple[pos, dir]]

            if shortest_path == []:
                # we are already at target
                # TODO: check whether programs really ends here (see https://robolab.inf.tu-dresden.de/spring/task/communication/msg-complete/)
                self.logger.debug("We are already at the target")
                self.__target_reached()
            elif shortest_path == None:
                # target is unreachable
                # TODO: what if we had a target and received an unreachable one->we don't have any target anymore, right?
                self.logger.debug(f"The given target at {self.target_pos} is unreachable.")
                self.target_pos = None
                next_dir = self.__explore()
            else:
                next_dir = shortest_path[0][1]
                self.logger.debug(f"Continuing driving towards target at {self.target_pos} in dir {next_dir}")
        else:
            self.logger.debug("No target to drive to - continuing exploration")
            next_dir = self.__explore()

        self.logger.debug(f"I decided to drive into dir {next_dir}")
        print("Next dir: " + str(next_dir))
        print("Last pos: " + str(self.last_position.x) + " " + str(self.last_position.y))

        # NOTE: check that robo selected right path here!
        pdb.set_trace()

        self.communication.path_select(self.last_position.x, self.last_position.y, next_dir)
        # actual movement is performed on receive_path_select :)
        self.communication.communication.prepare_fallback_path_select_message()

    def __explore(self) -> Optional[Direction]:
        """
        Let the robo have some fun and explore the planet on it's own
        """
        self.logger.debug("---Entering __explore")
        next_dir = self.planet.get_next_exploration_dir((self.last_position.x, self.last_position.y))

        if next_dir == None:
            # planet has been explored completely->there is nothing to explore anymore
            self.logger.debug(
                "I have explored everything and as this method is only called of there was no target I'm finished:)")
            self.communication.exploration_completed()
            self.logger.warning("THIS SHOULDNT BE EXECUTED, program should quit once the exploration is completed")
            return None

        self.logger.debug(f"Decide to continue exploration in dir {next_dir}")
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
        # if not env["SIMULATOR"]:
            # drive from start to first communication point
            # self.robot.drive_until_communication_point()

        self.select_next_dir()  # undo alex's change to begin()

    def __handle_received_planet(self, startX: int, startY: int, startOrientation: Direction):

        # startOrientation is the dir the robot is pointing towards after entering the node
        came_from_dir = Direction((startOrientation + 180) % 360)
        # mark start path as blocked (is always a dead end)
        self.planet.add_path(((startX, startY), came_from_dir), ((startX, startY), came_from_dir), -1)

    def __check_explorable_paths(self):
        """
        Explores all paths from the current node

        Registers unexplored paths in planet

        WARNING: make sure self.last_position.direction is updated before calling this func!
        TODO: don't scan nodes which are already explored completely
        """
        start_dir = self.last_position.direction  # the direction we came from

        print(f"Started scan from {start_dir}, set scan dir to {self.last_position.direction} due to driving forward.")
        # check all paths
        for i in range(0, 4):  # 1 because there must be a path on the one we came from
            # TODO: 2nd rotation scans the path we came from (not needed!)
            # update current orientation by 90deg
            self.last_position.direction = (self.last_position.direction + 90) % 360
            # check whether there is a path
            possible_path = self.robot.station_scan()

            if possible_path:
                try:
                    self.planet.add_possible_unexplored_path((self.last_position.x, self.last_position.y),
                                                             self.last_position.direction)
                except Exception as e:
                    print(f"Error while adding path to planet: {e}")
            self.logger.debug(f"Checking {self.last_position.direction}")

    def communication_point_reached(self):
        """
        An jedem weiteren Kommunikationspunkt übermittelt der Roboter zu Beginn der Übertragung den gefahrenen Pfad.
        Dieser besteht aus Start- und Zielkoordinaten sowie den jeweiligen Himmelsrichtungen.
        Mithilfe der Odometrie schätzt er dabei seine neue Position ab.
        :return: void
        """

        self.communication.communication.logger.debug("paths: " + str(self.planet.paths))
        self.communication.communication.logger.debug("unexplored: " + str(self.planet.unexplored))

        if (self.last_position is None):
            self.logger.debug("last_position is None")
            return

        self.logger.debug("---Robo entered a communication point---")
        # calculate start and end position
        start_position = self.last_position

        end_position = None
        if env["ODOMETRY"]:
            self.odometry.calculate(self.robot.motor_pos_list)
            end_coords = self.odometry.get_coords()
            end_position = Position(self.odometry.get_coords()[0], self.odometry.get_coords()[1],
                                    self.odometry.get_dir())
        else:
            end_position = self.last_position
            # when there is no odometry, better send something than nothing
            # but doesnt matter, the server will correct it anyways
            # if (env["SIMULATOR"]):
            # end_position.direction = self.robot.getOrientation()

        is_path_blocked = self.robot.was_path_blocked
        self.logger.debug(f"The driven path was blocked?: {is_path_blocked}")

        if is_path_blocked:
            self.logger.warning(f"Sending path from {start_position} to {end_position} with status {is_path_blocked}")
            path_status = "blocked"
        else:
            path_status = "free"

        # send path to mothership for verification
        self.communication.path(start_position.x, start_position.y, start_position.direction, end_position.x,
                                end_position.y, end_position.direction, path_status)

    def __target_reached(self):
        """
        Wird aufgerufen, wenn das Ziel erreicht wurde
        """
        self.logger.success("I have reached my target!!!")
        self.communication.target_reached("Target reached.")
        self.target_pos = None

    def receive_path(self, startX, startY, startDirection, endX, endY, endDirection, pathStatus, pathWeight):
        # pass onto handler, forget pathStatus
        print("incremented received_since_last_path_select to " + str(
            self.communication.communication.received_since_last_path_select))
        self.__handle_received_path(startX, startY, startDirection, endX, endY, endDirection, pathWeight)

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

        # update last position and path status
        current_dir = (endDirection + 180) % 360  # we now look at to the opposite direction than we entered the node
        self.last_position = Position(endX, endY, current_dir)

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
        """
        Drive into given dir

        Das Mutterschiff bestätigt die Nachricht des Roboters, wobei es gegebenenfalls eine Korrektur in den Zielkoordinaten vornimmt (2). Es berechnet außerdem das Gewicht eines Pfades und hängt es der Nachricht an.
        siehe https://robolab.inf.tu-dresden.de/spring/task/communication/msg-select/
        """
        self.communication.communication.received_since_last_path_select = 1
        # NOTE: Make sure robo received the right path_select (ESPECIALLY NOT the fake server response)
        pdb.set_trace()

        # update last position and path status
        self.odometry.set_dir(startDirection)

        self.__rotate_robo_in_dir(startDirection)

        self.robot.drive_until_communication_point()

        self.communication.communication.received_since_last_path_select = 0

    def receive_target(self, targetX, targetY):
        """
        Zusätzlich zu den Planetennachrichten empfängt der Roboter an Kommunikationspunkten auch Befehle vom Mutterschiff.
        Eine Nachricht vom Typ target (1) erteilt dem Roboter den Auftrag, auf kürzestem Weg die angegebenen Koordinaten anzufahren, sofern er diesen anhand seiner aktuellen Karte berechnen kann. Sollte dies nicht möglich sein, wird das Ziel vermerkt und die Erkundung normal fortgesetzt, bis eine solche Berechnung möglich ist oder das Ziel erreicht wurde.
        Falls das Ziel ausserhalb der erkundbaren Karte liegt, kann bereits nach erfolgreicher Planetenerkundung eine Erfolgsmeldung an das Mutterschiff gesendet werden.
        siehe https://robolab.inf.tu-dresden.de/spring/task/communication/msg-target/
        """
        # store received info
        self.target_pos = (targetX, targetY)

    def __rotate_robo_in_dir(self, target_dir: Direction):
        """
        Tells the robo which way to rotate in order to be oriented in target_dir
        """
        # TODO: make sure robot.turn_deg deals appropriately with neg. values
        current_dir = self.last_position.direction
        logging.debug(f"Rotating: From {current_dir} to {target_dir}")
        # TODO: robot currently would sometimes rotate more than necessary (e.g. target_dir=270, current_dir=0)
        deg_to_rotate = target_dir - current_dir
        self.last_position.direction = target_dir
        self.robot.turn_deg(deg_to_rotate)

        # NOTE: make sure robo rotate into right direction
        pdb.set_trace()

    def receive_done(self, message):
        """
        Wurde das Ziel tatsächlich erreicht bzw. die gesamte Karte aufgedeckt, antwortet der Server mit einer Bestätigung vom Typ done (3) und dem Ende der Erkundung.
        """
        print("Done.")
        print("Message: " + message)
        self.robot.__stop()
        self.communication.done()

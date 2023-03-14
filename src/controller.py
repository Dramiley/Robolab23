import time

from communication import Communication
from communication_logger import CommunicationLogger
from odometry import Odometry
from robot import Robot
from robot_dummy import RobotDummy
from planet import Planet
from controller_webview import Webview

from typing import List


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
    last_position = Position(0, 0, 0)
    history = []

    def __init__(self, client):

        # setup communication
        self.communication = Communication(client, CommunicationLogger()).facade

        # setup error handling
        self.communication.set_callback('error', lambda message: print("COMM. FEHLER GEMELDET: " + message))

        # replace with robot.run_robot()
        self.robot = RobotDummy()
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

        # as long as the programm is not exited, wait
        while True:
            time.sleep(1)

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
        self.communication.set_callback('target', self.queue_received_target)

        # Wurde das Ziel tatsächlich erreicht bzw. die gesamte Karte aufgedeckt, antwortet der Server mit einer
        # Bestätigung vom Typ done (3) und dem Ende der Erkundung.
        self.communication.set_callback('done', self.receive_done)

    def receive_planet(self, planetName, startX, startY, startOrientation):

        # remember last position
        self.last_position = Position(startX, startY, startOrientation)
        # setup planet
        self.planet = Planet()

        # setup odometry
        self.odometry = Odometry(self.robot)
        self.odometry.set_pos((startX, startY))
        self.odometry.set_coords(startOrientation)

        # aktuelle position um 180 grad gedreht als blockiert merken
        # ->because we always start from a dead end
        self.planet.add_path((startX, startY), (startX, startY), int(startOrientation) + 180)

        # los gehts
        self.__explore()

    def __explore(self):

        # flush queued targets
        self.__flush_received_target_queue()

        # starte odometrie
        self.odometry.start()

        # wenn es nichts mehr zu erkunden gibt, dann ist die erkundung beendet
        if self.planet.is_exploration_complete():
            self.__exploration_complete("alles erkundet.")
            return

        # erstmal nach norden stellen
        alte_richtung = self.odometry.current_dir
        # TODO: change->calc dir to turn to into
        self.robot.turn_deg(-1 * alte_richtung)

        # in welche richtungen beginnen schwarze linien?
        possible_explore_paths = self.__get_possible_explore_paths()

        # welche richtungen sind noch nicht erkundet worden und nicht blockiert?
        for i in range(0, 3):
            if not possible_explore_paths[i]:
                continue
            is_blocked = self.planet.is_path_blocked((self.last_position.x, self.last_position.y), i * 90)
            is_explored = self.planet.is_path_explored((self.last_position.x, self.last_position.y), i * 90)

            # ist es weiterhin möglich diesen pfad zu erkunden?
            possible_explore_paths[i] = not is_blocked and not is_explored

        # wenn alle richtungen blockiert sind, dann ist der pfad zu Ende
        if not any(possible_explore_paths):

            # pop last history entry
            last_history_entry = self.history.pop()
            self.__receive_target(last_history_entry[0], last_history_entry[1])

        else:

            # append history entry
            if sum(possible_explore_paths) > 2:
                # there are other dirs to explore on this node
                self.history.append((self.last_position.x, self.last_position.y))

            # entscheide dich für die erste möglichkeit (DFS)
            for i in range(0, 3):
                if possible_explore_paths[i]:
                    # teile die entscheidung dem mutterschiff mit
                    self.communication.path_select(self.last_position.x, self.last_position.y, i * 90)

                    # das mutterschiff wird uns dann beauftragen diesen oder einen anderen Pfade zu nehmen
                    break

        self.odometry.stop()

    def __get_possible_explore_paths(self) -> List[bool]:
        """
        Explores all paths from the current node
        @return: list of directions to nodes that have not been explored yet
        true if path exists, false otherwise
        """
        possible_explore_paths: List[bool] = [False, False, False, False]

        # check all paths
        for i in range(0, 3):
            # check if there is a black line beginning
            possible_explore_paths[i] = self.robot.has_path_ahead()

            # turn to next path
            self.robot.turn_deg(90)

        return possible_explore_paths

    def communication_point_reached(self):
        """
        An jedem weiteren Kommunikationspunkt übermittelt der Roboter zu Beginn der Übertragung den gefahrenen Pfad.
        Dieser besteht aus Start- und Zielkoordinaten sowie den jeweiligen Himmelsrichtungen.
        Mithilfe der Odometrie schätzt er dabei seine neue Position ab.
        :return: void
        """

        # calculate start and end position
        start_position = self.last_position
        end_position = self.odometry.get_coords()

        if (start_position.x == end_position.x and start_position.y == end_position.y):
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

        # starte odometry
        self.odometry.set_coords((startX, startY))
        self.odometry.set_dir(startOrientation)

        # update odometry inside planet
        self.planet.add_path(((startX, startY), startOrientation), ((endX, endY), endOrientation), pathWeight)

        # update last position and path status
        self.last_position = Position(endX, endY, endOrientation)

        # don't drive to next communication point yet, because we want to receive path select messages first
        # instead find paths and ask mothership to select one
        self.__explore()

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

    def receive_path_select(self, startDirection):
        """
        Das Mutterschiff bestätigt die Nachricht des Roboters, wobei es gegebenenfalls eine Korrektur in den Zielkoordinaten vornimmt (2). Es berechnet außerdem das Gewicht eines Pfades und hängt es der Nachricht an.
        siehe https://robolab.inf.tu-dresden.de/spring/task/communication/msg-select/
        """

        # update last position and path status
        self.odometry.set_dir(startDirection)

        # now we can finally drive to the next communication point
        self.robot.notify_at_communication_point()

    __receive_target_queue = []

    def queue_received_target(self, x, y):
        self.__receive_target_queue.append((x, y))

    def __flush_received_target_queue(self, x, y):
        for (x, y) in self.__receive_target_queue:
            self.__receive_target(x, y)
        self.__receive_target_queue = []

    def __receive_target(self, x, y):
        """
        Zusätzlich zu den Planetennachrichten empfängt der Roboter an Kommunikationspunkten auch Befehle vom Mutterschiff.
        Eine Nachricht vom Typ target (1) erteilt dem Roboter den Auftrag, auf kürzestem Weg die angegebenen Koordinaten anzufahren, sofern er diesen anhand seiner aktuellen Karte berechnen kann. Sollte dies nicht möglich sein, wird das Ziel vermerkt und die Erkundung normal fortgesetzt, bis eine solche Berechnung möglich ist oder das Ziel erreicht wurde.
        Falls das Ziel ausserhalb der erkundbaren Karte liegt, kann bereits nach erfolgreicher Planetenerkundung eine Erfolgsmeldung an das Mutterschiff gesendet werden.
        siehe https://robolab.inf.tu-dresden.de/spring/task/communication/msg-target/
        """

        # get last position
        last_position = self.last_position

        # prüfen, ob wir einen pfad finden
        path = self.planet.get_shortest_path((last_position.x, last_position.y), (x, y))

        if path is None:
            # es gibt keinen shortest path, also erkunden wir weiter
            self.__explore()
        else:
            # es gibt einen shortest path, liste von positionen mit richtung.
            # fahre zuerst zum ersten punkt, dann zum zweiten, dann zum dritten, ...
            for position in path:
                self.robot.turn_deg(position[1] - last_position.direction)
                self.robot.drive_until_communication_point()
            self.__target_reached("Target reached.")

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

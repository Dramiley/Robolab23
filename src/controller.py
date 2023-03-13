import time

from communication import Communication
from communication_logger import CommunicationLogger
from odometry import Odometry, Position
from robot import Robot
from webview import Webview


class Controller:
    robot = None
    communication = None
    odometry = None
    planet = None
    last_position = Position(0, 0, 0)

    def __init__(self, client):
        # start webview for debugging
        self.webview = Webview(self)

        # setup communication
        self.communication = Communication(client, CommunicationLogger()).facade

        # setup error handling
        self.communication.set_callback('error', lambda message: print("COMM. FEHLER GEMELDET: " + message))

        # replace with robot.run_robot()
        self.robot = Robot()
        self.robot.set_controller(self)

        # setup callbacks
        self.init_callbacks()

        time.sleep(1)

    def init_callbacks(self):
        # bei einer Antwort des Mutterschiffs mit dem Typ "planet" wird der Name des Planeten ausgegeben
        self.communication.set_callback('planet', self.receive_planet)

        # bei einer Antwort des Mutterschiffs mit dem Typ "path" wird der Pfad ausgegeben
        self.communication.set_callback('path', self.receive_path)

        # bei einer Antwort des Mutterschiffs mit dem Typ "path-unveiled" wird der Pfad ausgegeben
        self.communication.set_callback('pathUnveiled', self.receive_path_unveiled)

        #  In einigen Fällen kann es vorkommen, dass dem Mutterschiff günstigere Routen oder Hindernisse bekannt sind. In diesem Fall weist das Mutterschiff den Roboter an, einen anderen Pfad zu befahren
        self.communication.set_callback('pathSelect', self.receive_path_select)

        # Zusätzlich zu den Planetennachrichten empfängt der Roboter an Kommunikationspunkten auch Befehle vom Mutterschiff.
        self.communication.set_callback('target', self.receive_target)

        # Wurde das Ziel tatsächlich erreicht bzw. die gesamte Karte aufgedeckt, antwortet der Server mit einer Bestätigung vom Typ done (3) und dem Ende der Erkundung.
        self.communication.set_callback('done', self.receive_done)

    def begin(self):
        print("Controller started")

        # Euer Roboter wird vom Mutterschiff auf einem fernen Planeten nahe einer beliebigen Versorgungsstation abgesetzt
        # Anfahrtsweg fahren
        self.robot.drive_until_start()

        # teilt dem Mutterschiff mit, dass er bereit zur Erkundung ist
        self.communication.ready()

    def receive_planet(self, planetName, startX, startY, startOrientation):
        # setup odometry
        self.odometry = Odometry(self.robot, (startX, startY), int(startOrientation))
        self.odometry.set_communication(self.communication)

        # remember last position
        self.last_position = Position(startX, startY, startOrientation)

        # setup planet
        self.planet = Planet(planetName, startX, startY, startOrientation)

    def communication_point_reached(self):
        """
        An jedem weiteren Kommunikationspunkt übermittelt der Roboter zu Beginn der Übertragung den gefahrenen Pfad.
        Dieser besteht aus Start- und Zielkoordinaten sowie den jeweiligen Himmelsrichtungen.
        Mithilfe der Odometrie schätzt er dabei seine neue Position ab.
        :return: void
        """

        # calculate start and end position
        start_position = self.last_position
        end_position = self.odometry.get_position()

        if (start_position.x == end_position.x and start_position.y == end_position.y):
            path_status = "blocked"
        else:
            path_status = "free"

        # send path to mothership for verification
        self.communication.path(start_position.x, start_position.y, start_position.direction, end_position.x,
                                end_position.y, end_position.direction, path_status)

    @staticmethod
    def tuple_to_position(self, tuple):
        x, y = tuple[0]
        direction = tuple[1]
        return Position(x, y, direction)

    @staticmethod
    def position_to_tuple(position):
        return ((position.x, position.y), int(position.direction))

    def receive_path(self, startX, startY, startOrientation, endX, endY, endOrientation, pathStatus, pathWeight):
        """
        Das Mutterschiff bestätigt die Nachricht des Roboters, wobei es gegebenenfalls eine Korrektur in den Zielkoordinaten vornimmt (2). Es berechnet außerdem das Gewicht eines Pfades und hängt es der Nachricht an.
        siehe https://robolab.inf.tu-dresden.de/spring/task/communication/msg-path/
        """

        # update odometry inside planet
        self.planet.add_path(((startX, startY), startOrientation), ((endX, endY), endOrientation), pathWeight)

        # update last position and path status
        self.last_position = Position(endX, endY, endOrientation)

        # don't drive to next communication point yet, because we want to receive path select messages first
        # instead find paths and ask mothership to select one
        self.robot.find_paths()
        next_path = self.tuple_to_position(self.planet.get_next_path())
        self.communication.path_select(next_path.x, next_path.y, next_path.direction)

    def receive_path_unveiled(self, startX, startY, startOrientation, endX, endY, endOrientation, pathStatus,
                              pathWeight):
        """
        Zusätzlich zur immer gesendeten Bestätigung bzw. Korrektur mit Gewichtung können weitere Nachrichten empfangen werden. Hierbei werden neue Pfade aufgedeckt, die durch andere Roboter bereits erkundet wurden, oder auch bereits erkundete Strecken gesperrt (bspw. durch einen Meteoriteneinschlag).
        Dies ermöglicht es Eurem Roboter, schneller mit der Erkundung fertig zu werden, da er die empfangenen Pfade direkt in seine Karte aufnimmt und nicht erkunden muss.
        siehe https://robolab.inf.tu-dresden.de/spring/task/communication/msg-unveiled/
        """

        self.odometry.receive_path_unveiled(startX, startY, startOrientation, endX, endY, endOrientation, pathStatus,
                                            pathWeight)

    def before_entering_path(self, position):
        """
        Bevor ein neuer Pfad befahren wird, sendet der Roboter seine Wahl an das Mutterschiff (1). In einigen Fällen kann es vorkommen, dass dem Mutterschiff günstigere Routen oder Hindernisse bekannt sind. In diesem Fall weist das Mutterschiff den Roboter an, einen anderen Pfad zu befahren (2).
        siehe https://robolab.inf.tu-dresden.de/spring/task/communication/msg-select/
        @param position: Position
        """
        self.communication.path_select(position.x, position.y, position.direction)

    def receive_path_select(self, startDirection):
        """
        Das Mutterschiff bestätigt die Nachricht des Roboters, wobei es gegebenenfalls eine Korrektur in den Zielkoordinaten vornimmt (2). Es berechnet außerdem das Gewicht eines Pfades und hängt es der Nachricht an.
        siehe https://robolab.inf.tu-dresden.de/spring/task/communication/msg-select/
        """

        # update last position and path status
        self.odometry.receive_path_select(startDirection)

        # now we can finally drive to the next communication point
        self.robot.drive_to_next_communication_point()

    def receive_target(self, x, y):
        """
        Zusätzlich zu den Planetennachrichten empfängt der Roboter an Kommunikationspunkten auch Befehle vom Mutterschiff.
        Eine Nachricht vom Typ target (1) erteilt dem Roboter den Auftrag, auf kürzestem Weg die angegebenen Koordinaten anzufahren, sofern er diesen anhand seiner aktuellen Karte berechnen kann. Sollte dies nicht möglich sein, wird das Ziel vermerkt und die Erkundung normal fortgesetzt, bis eine solche Berechnung möglich ist oder das Ziel erreicht wurde.
        Falls das Ziel ausserhalb der erkundbaren Karte liegt, kann bereits nach erfolgreicher Planetenerkundung eine Erfolgsmeldung an das Mutterschiff gesendet werden.
        siehe https://robolab.inf.tu-dresden.de/spring/task/communication/msg-target/
        """
        self.odometry.receive_target(x, y)

    def drive_to(self, x, y):
        """
        Fährt den Roboter zu den angegebenen Koordinaten
        Wird von der Odometrie aufgerufen
        """
        self.robot.drive_to(x, y)

    def target_reached(self):
        """
        Wird von der Odometrie aufgerufen, wenn das Ziel erreicht wurde
        """
        self.communication.target_reached("Target reached.")

    def exploration_complete(self):
        """
        Wird von der Odometrie aufgerufen, wenn die Erkundung abgeschlossen ist
        """
        self.communication.exploration_completed("Exploration completed.")

    def receive_done(self, message):
        """
        Wurde das Ziel tatsächlich erreicht bzw. die gesamte Karte aufgedeckt, antwortet der Server mit einer Bestätigung vom Typ done (3) und dem Ende der Erkundung.
        """
        print("Done.")
        print("Message: " + message)
        self.robot.stop()
        self.communication.done()

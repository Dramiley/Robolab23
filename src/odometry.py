# !/usr/bin/env python3
from communication_facade import CommunicationFacade


class Odometry:
    communication: CommunicationFacade = None

    def __init__(self):
        """
        Initializes odometry module
        """

        # YOUR CODE FOLLOWS (remove pass, please!)
        pass

    def set_communication(self, communication: CommunicationFacade):
        self.communication = communication

    def receive_path(self, startX, startY, startOrientation, endX, endY, endOrientation, pathStatus, pathWeight):
        """
        Das Mutterschiff bestätigt die Nachricht des Roboters, wobei es gegebenenfalls eine Korrektur in den Zielkoordinaten vornimmt (2). Es berechnet außerdem das Gewicht eines Pfades und hängt es der Nachricht an.
        siehe https://robolab.inf.tu-dresden.de/spring/task/communication/msg-path/
        """
        pass

    def receive_path_unveiled(self, startX, startY, startOrientation, endX, endY, endOrientation, pathStatus,
                              pathWeight):
        """
         Zusätzlich zur immer gesendeten Bestätigung bzw. Korrektur mit Gewichtung können weitere Nachrichten empfangen werden. Hierbei werden neue Pfade aufgedeckt, die durch andere Roboter bereits erkundet wurden, oder auch bereits erkundete Strecken gesperrt (bspw. durch einen Meteoriteneinschlag).
         Dies ermöglicht es Eurem Roboter, schneller mit der Erkundung fertig zu werden, da er die empfangenen Pfade direkt in seine Karte aufnimmt und nicht erkunden muss.
         siehe https://robolab.inf.tu-dresden.de/spring/task/communication/msg-unveiled/
         """
        pass

    def receive_target(self, x, y):
        """
        Zusätzlich zu den Planetennachrichten empfängt der Roboter an Kommunikationspunkten auch Befehle vom Mutterschiff.
        siehe https://robolab.inf.tu-dresden.de/spring/task/communication/msg-target/

        Callback controller.drive_to(x, y) to drive to the target?
        """

        """
        Zusätzlich zu den Planetennachrichten empfängt der Roboter an Kommunikationspunkten auch Befehle vom Mutterschiff.
        Eine Nachricht vom Typ target (1) erteilt dem Roboter den Auftrag, auf kürzestem Weg die angegebenen Koordinaten anzufahren, sofern er diesen anhand seiner aktuellen Karte berechnen kann. Sollte dies nicht möglich sein, wird das Ziel vermerkt und die Erkundung normal fortgesetzt, bis eine solche Berechnung möglich ist oder das Ziel erreicht wurde.
        Falls das Ziel ausserhalb der erkundbaren Karte liegt, kann bereits nach erfolgreicher Planetenerkundung eine Erfolgsmeldung an das Mutterschiff gesendet werden.
        """

        pass

    def receive_path_select(self, startDirection):
        """
        Das Mutterschiff bestätigt die Nachricht des Roboters, wobei es gegebenenfalls eine Korrektur in den Zielkoordinaten vornimmt (2). Es berechnet außerdem das Gewicht eines Pfades und hängt es der Nachricht an.
        siehe https://robolab.inf.tu-dresden.de/spring/task/communication/msg-select/
        """

        pass

    def get_next_path(self):
        """
        Returns the next path to drive to
        This path will be checked with the mothership
        @return: Position
        """

        pass


class Position:
    x, y, direction = 0, 0, 0

    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction

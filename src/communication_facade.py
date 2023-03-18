#!/usr/bin/env python3

class CommunicationFacade:

    def __init__(self, communication):
        self.communication = communication

    def test_planet(self, planetName):
        """
        Sets a testPlanet on the server
        :param planetName: The planet name
        :return: void
        """
        self.communication.send_message('testPlanet', '''{
          "from": "client",
          "type": "testPlanet",
          "payload": {
            "planetName": "%s"
          }
        }''' % planetName)

    def ready(self):
        """
        Sends a ready message to the server
        :return: void
        """
        self.communication.send_message('ready', '''{
          "from": "client",
          "type": "ready"
        }''')

    def path(self, startX, startY, startDirection, endX, endY, endDirection, pathStatus):
        """
        Sends a path message to the server
        :param startX: The start x coordinate
        :param startY: The start y coordinate
        :param startDirection: The start direction
        :param endX: The end x coordinate
        :param endY: The end y coordinate
        :param endDirection: The end direction
        :param pathStatus: The path status
        :return: void
        """

        self.communication.send_planet_message('path', '''{
          "from": "client",
          "type": "path",
          "payload": {
            "startX": %s,
            "startY": %s,
            "startDirection": %s,
            "endX": %s,
            "endY": %s,
            "endDirection": %s,
            "pathStatus": "%s"
          }
        }''' % (startX, startY, int(startDirection) % 360, endX, endY, int(endDirection) % 360, pathStatus))

    def path_select(self, startX, startY, startDirection):
        """
        Sends a pathSelect message to the server
        :param startX: The start x coordinate
        :param startY: The start y coordinate
        :param startDirection: The start direction
        :return: void
        """

        self.communication.send_planet_message('pathSelect', '''{
          "from": "client",
          "type": "pathSelect",
          "payload": {
            "startX": %s,
            "startY": %s,
            "startDirection": %s
          }
        }''' % (startX, startY, int(startDirection) % 360))

        self.communication.prepare_fallback_path_select_message(int(startDirection) % 360)

    def path_unveiled(self, startX, startY, startDirection, endX, endY, endDirection, pathStatus, pathWeight):
        """
        Sends a pathUnveiled message to the server
        :param startX: The start x coordinate
        :param startY: The start y coordinate
        :param startDirection: The start direction
        :param endX: The end x coordinate
        :param endY: The end y coordinate
        :param endDirection: The end direction
        :param pathStatus: The path status
        :param pathWeight: The path weight
        :return: void
        """
        self.communication.send_planet_message('pathUnveiled', '''{
          "from": "client",
          "type": "pathUnveiled",
          "payload": {
            "startX": %s,
            "startY": %s,
            "startDirection": %s,
            "endX": %s,
            "endY": %s,
            "endDirection": %s,
            "pathStatus": "%s",
            "pathWeight": %s
          }
        }''' % (startX, startY, int(startDirection) % 360, endX, endY, int(endDirection) % 360, pathStatus, pathWeight))

    def target_reached(self, message):
        """
        Sends a targetReached message to the server
        :param message: The message
        :return: void
        """
        self.communication.send_message('targetReached', '''{
          "from": "client",
          "type": "targetReached",
          "payload": {
            "message": "%s"
          }
        }''' % message)

    def exploration_completed(self, message: str = "Take me home pleeaaasse :'("):
        """
        Sends a explorationCompleted message to the server
        :param message: The message
        :return: void
        """
        self.communication.send_message('explorationCompleted', '''{
          "from": "client",
          "type": "explorationCompleted",
          "payload": {
            "message": "%s"
          }
        }''' % message)

    def set_callback(self, message_type, callback):
        """
        Sets a callback for a specific message type
        :param message_type: The type to set the callback for
        :param callback: The callback to set
        :return: void
        """
        self.communication.set_callback(message_type, callback)

    def set_controller(self, controller):
        """
        Sets the controller
        :param controller: The controller
        :return: void
        """
        self.communication.set_controller(controller)

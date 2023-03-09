#!/usr/bin/env python3

class CommunicationFacade:
    # bidirectional association
    communication = None

    def __init__(self, communication):
        self.communication = communication

    def testPlanet(self, planet):
        """
        Sends a testPlanet message to the server
        :param planet: The planet to test
        :return: void
        """
        self.communication.send_message('testPlanet', '''{
          "from": "client",
          "type": "testPlanet",
          "payload": {
            "planetName": "%s"
          }
        }''' % planet)

    def ready(self):
        """
        Sends a ready message to the server
        :return: void
        """
        self.communication.send_message('ready', '''{
          "from": "client",
          "type": "ready"
        }''')

    def set_callback(self, message_type, callback):
        """
        Sets a callback for a specific message type
        :param message_type: The type to set the callback for
        :param callback: The callback to set
        :return: void
        """
        self.communication.set_callback(message_type, callback)

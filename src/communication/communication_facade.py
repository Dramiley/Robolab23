#!/usr/bin/env python3

class CommunicationFacade:

    # bidirectional association
    communication = None

    def __init__(self, communication):
        self.communication = communication

    def testPlanet(self, planet):
        self.communication.send_message('testPlanet', '''{
          "from": "client",
          "type": "testPlanet",
          "payload": {
            "planetName": "%s"
          }
        }''' % planet)


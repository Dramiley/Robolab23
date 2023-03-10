#!/usr/bin/env python3
from paho import mqtt

from communication_logger import CommunicationLogger
from communication import Communication


class CommunicationTest:

    def react_to_ready(self, planetName, startX, startY, startOrientation):
        print('got reaction to ready')
        print('planetName: ' + planetName)
        print('startX: ' + str(startX))

    def react_to_error(self, message):
        print('got reaction to error')
        print('error: ' + message)

    def run_tests(self):
        import paho.mqtt.client as mqtt
        import time

        # have the print command as logger
        logger = CommunicationLogger()

        # create connection
        connection = Communication(mqtt_client=mqtt.Client(), logger=logger)

        # send message
        connection.facade.ready()
        connection.facade.set_callback('planet', self.react_to_ready)

        # wait for message
        time.sleep(1)

        # send path
        connection.facade.path(1, 4, 90, 34, 3, 90, "free")
        connection.facade.set_callback('error', self.react_to_error)

        # wait for message
        time.sleep(1)

        # pretend we're at the target
        connection.facade.targetReached("we're at the target")

        # wait for messages
        time.sleep(1)

        # delete connection
        del connection

        # done
        print('done')

if __name__ == '__main__':
    CommunicationTest().run_tests()

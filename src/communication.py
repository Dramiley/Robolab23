#!/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
import json
import ssl
import paho.mqtt.client as mqtt

import sys

sys.path.insert(0, 'communication')

# import communication_facade from communication/communication_facade.py
from communication_facade import CommunicationFacade

"""
We're using MQTT auf QoS Level 2 (exactly once) to communicate with the server.
"""


class Communication:
    # setup secrets
    group_id = '046'
    password = 'PwQ3lFHkEl'

    # setup MQTT client
    client = None
    facade = None  # use the facade to send messages more eloquently

    # short term memory
    planet_name = None

    # callbacks
    """
    Dictionary to hold the callbacks for the different message types
    """
    callbacks = {}

    """
    Class to hold the MQTT client communication
    Feel free to add functions and update the constructor to satisfy your requirements and
    thereby solve the task according to the specifications
    """

    # DO NOT EDIT THE METHOD SIGNATURE
    def __init__(self, mqtt_client, logger):
        """
        Initializes communication module, connect to server, subscribe, etc.
        :param mqtt_client: paho.mqtt.client.Client
        :param logger: logging.Logger
        """

        # save client
        self.client = mqtt_client

        # configure client
        self.client.on_message = self.safe_on_message_handler  # Register callback function
        self.client.tls_set(tls_version=ssl.PROTOCOL_TLS)
        self.client.username_pw_set(self.group_id,
                                    password=self.password)  # Your group credentials, see the python skill-test for your group password
        self.client.connect('mothership.inf.tu-dresden.de', port=8883)

        # inital subscribe
        self.client.subscribe('explorer/{}'.format(self.group_id), qos=2)  # Subscribe to topic explorer/xxx
        self.client.loop_start()

        # save logger
        self.logger = logger

        # create facade
        self.facade = CommunicationFacade(self)

    # destructor
    def __del__(self):
        """
        Disconnects from the server
        """
        self.client.loop_stop()
        self.client.disconnect()

    # DO NOT EDIT THE METHOD SIGNATURE
    def on_message(self, client, data, message):
        """
        Handles the callback if any message arrived
        :param client: paho.mqtt.client.Client
        :param data: Object
        :param message: Object
        :return: void
        """
        payload = json.loads(message.payload.decode('utf-8'))
        self.logger.debug(json.dumps(payload, indent=2))

        # check if message type is set
        if 'type' not in payload:
            self.logger.error('Message type is not set')
            return

        # if the type is planet, we need to subscribe to the planet channel
        if payload['type'] == 'planet':
            # save planet name
            self.planet_name = payload['payload']['planetName']
            # subscribe to planet channel
            self.client.subscribe('planet/{}/{}'.format(self.planet_name, self.group_id), qos=2)
            self.logger.debug('Subscribed to planet/{}/{}'.format(self.planet_name, self.group_id))

        # check if message type has a callback registered and call it
        if payload['type'] in self.callbacks:
            self.callback(payload['type'], payload['payload'])
        else:
            self.logger.error('No callback for message type ' + payload['type'] + ' registered')

    # In order to keep the logging working you must provide a topic string and
    # an already encoded JSON-Object as message.

    def send_planet_message(self, topic, message):
        """
        Sends given message to the current planet
        :param topic: String
        :param message: Object
        :return: void
        """
        # we must have a planet name
        if self.facade.planet_name is None:
            self.logger.error('No planet name set')
            return

        # send message
        self.client.publish('planet/{}/{}'.format(self.planet_name, self.group_id), payload=message, qos=2)

    def send_explorer_message(self, topic, message):
        """
        Sends given message for the current explorer without planet context
        :param topic: String
        :param message: Object
        :return: void
        """

        # send message
        self.client.publish('explorer/{}'.format(self.group_id), payload=message, qos=2)

    def send_message(self, topic, message):
        self.send_explorer_message(topic, message)

    # This helper method encapsulated the original "on_message" method and handles
    # exceptions thrown by threads spawned by "paho-mqtt"
    def safe_on_message_handler(self, client, data, message):
        """
        Handle exceptions thrown by the paho library
        :param client: paho.mqtt.client.Client
        :param data: Object
        :param message: Object
        :return: void
        """

        try:
            self.on_message(client, data, message)
        except:
            import traceback
            traceback.print_exc()
            raise

    def set_callback(self, message_type, callback):
        self.callbacks[message_type] = callback

    def callback(self, message_type, payload):
        # load payload definitions from json file
        with open('communication/payload_definitions.json') as json_file:
            payload_definitions = json.load(json_file)

        # check if payload is valid
        if message_type in payload_definitions:
            # check if payload is valid
            if not self.validate_payload(payload, payload_definitions[message_type]):
                self.logger.error('Payload is not valid')
                return

        """
        call callback function and pass each payload definition as argument 
        so e.g. 
        payload_definition = ['x', 'y']
        call
        callback(x, y)
        """

        # call callback
        # check if callback function signature matches the payload definition
        if len(self.callbacks[message_type].__code__.co_varnames) == len(payload):
            self.callbacks[message_type](**payload)
        else:
            self.logger.error('Callback function signature does not match payload definition')

    def validate_payload(self, payload, payload_definition):
        # check if all keys are set
        for key in payload_definition:
            if key not in payload:
                return False

        # check if all keys are valid
        for key in payload:
            if key not in payload_definition:
                return False

        # payload is valid
        return True


class CommunicationLogger:
    """
    Dummy logger class to replace the logger from the server
    """

    def debug(self, message):
        print("==> CommunicationLog: " + message)

    def error(self, message):
        print("==> CommunicationError: " + message)


def react_to_ready(planetName, startX, startY, startOrientation):
    print('got reaction to ready')
    print('planetName: ' + planetName)
    print('startX: ' + str(startX))


def dev_test():
    import time

    # have the print command as logger
    logger = CommunicationLogger()

    # create connection
    connection = Communication(mqtt_client=mqtt.Client(), logger=logger)

    # send message
    connection.facade.ready()
    connection.facade.set_callback('planet', react_to_ready)

    # wait for message
    time.sleep(5)

    # delete connection
    del connection

    # done
    print('done')


if __name__ == '__main__':
    dev_test()

#!/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
import json
import os
import ssl
import threading
import time

# import communication_facade
from communication_facade import CommunicationFacade


class Communication:

    def __init__(self, mqtt_client, logger):

        # setup secrets
        self.group_id = '046'
        self.password = 'PwQ3lFHkEl'

        # setup MQTT client
        self.client = None
        self.facade = None  # use the facade to send messages more eloquently

        # short term memory
        self.planet_name = None

        # callbacks
        """
        Dictionary to hold the callbacks for the different message types
        """
        self.callbacks = {}

        """
        Class to hold the MQTT client communication_scripts
        Feel free to add functions and update the constructor to satisfy your requirements and
        thereby solve the task according to the specifications
        """

        self.received_since_last_path_select = 0
        """
        Initializes communication_scripts module, connect to server, subscribe, etc.
        :param mqtt_client: paho.mqtt.client.Client
        :param logger: logging.Logger
        """

        # save client
        self.controller = None
        self.client = mqtt_client

        # configure client
        self.client.on_message = self.safe_on_message_handler  # Register callback function
        self.client.tls_set(tls_version=ssl.PROTOCOL_TLS)
        self.client.username_pw_set(self.group_id,
                                    password=self.password)  # Your group credentials, see the python skill-test for your group password
        self.client.connect('mothership.inf.tu-dresden.de', port=8883)

        # inital subscribe
        self.client.subscribe('explorer/{}'.format(self.group_id), qos=2)  # Subscribe to topic explorer/xxx
        self.client.subscribe('comtest/{}'.format(self.group_id), qos=2)  # Subscribe to topic explorer/xxx
        self.client.loop_start()

        # create facade
        self.facade = CommunicationFacade(self)

    # destructor
    def __del__(self):
        """
        Disconnects from the server
        """
        self.client.loop_stop()
        self.client.disconnect()

    def __publish(self, topic, payload: str, qos=2):

        """
        Publishes a message to the given topic while replacing all None values with null
        :param topic: String
        :param payload: String
        :return: void
        """

        payload_dict = None
        try:
            payload_dict = json.loads(payload)
        except:
            raise ValueError('payload is not a valid json string')

        # if the payload has the key startDirection and the value is None, raise an error
        if 'startDirection' in payload_dict and payload_dict['startDirection'] is None:
            raise ValueError('startDirection in payload is None')

        # in the payload, replace all None values with the string "None"
        payload = payload.replace('None', '"None"')

        # publish the message
        self.client.publish(topic, payload=payload, qos=2)

    def on_message(self, client, data, message):
        """
        Handles the callback if any message arrived
        :param client: paho.mqtt.client.Client
        :param data: Object
        :param message: Object
        :return: void
        """

        # log the data
        # get client id
        client_id = client._client_id.decode('utf-8')

        if client_id != data:
            return

        payload = ""
        try:
            if message.payload is not None:
                payload = json.loads(message.payload.decode('utf-8'))
        except:
            raise ValueError('payload is not a valid json string')

        # if "from" is the client itself, ignore the message
        if 'from' in payload and payload['from'] == "client":
            return

        # check if message type is set
        if 'type' not in payload:
            raise ValueError('Message type not set')

        # if the type is planet, we need to subscribe to the planet channel
        if payload['type'] == 'planet':
            # save planet name
            self.planet_name = payload['payload']['planetName']
            # subscribe to planet channel
            self.client.subscribe('planet/{}/{}'.format(self.planet_name, self.group_id), qos=2)

        # check if message type has a callback registered and call it
        if payload['type'] in self.callbacks:
            self.callback(payload['type'], payload['payload'])

    def send_planet_message(self, topic, payload):
        """
        Sends given message to the current planet
        :param topic: String
        :param payload: Object
        :return: void
        """
        # we must have a planet name
        if self.planet_name is None:
            raise ValueError('No planet name set')

        # send message
        self.__publish('planet/{}/{}'.format(self.planet_name, self.group_id), payload=payload, qos=2)

    def send_explorer_message(self, topic, payload):
        """
        Sends given message for the current explorer without planet context
        :param topic: String
        :param payload: Object
        :return: void
        """

        # send message
        self.__publish('explorer/{}'.format(self.group_id), payload=payload, qos=2)

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

    def set_callback(self, message_type, callback):
        self.callbacks[message_type] = callback

    def callback(self, message_type, payload):
        # load payload definitions from json file
        # in the current directory

        __current_dir = os.path.dirname(os.path.realpath(__file__))
        with open(__current_dir + '/communication_definitions.json') as json_file:
            payload_definitions = json.load(json_file)

        # check if payload is valid
        if message_type in payload_definitions:
            # check if payload is valid
            if not self.validate_payload(payload, payload_definitions[message_type]):
                raise ValueError('Payload is not valid')

        # call callback
        # check if callback function signature matches the payload definition
        if len(self.callbacks[message_type].__code__.co_varnames) == len(payload) or \
                len(self.callbacks[message_type].__code__.co_varnames) == len(payload) + 1:
            self.callbacks[message_type](**payload)
        else:
            raise ValueError('Callback function signature for "' + message_type + '" does not match payload '
                                                                                  'definition. Has ' + str(len(
                self.callbacks[message_type].__code__.co_varnames)) + ' arguments (' + str(self.callbacks[
                                                                                               message_type].__code__.co_varnames) + '), but payload has ' + str(
                len(payload)) + ' arguments.' +
                             '\r\nPayload: ' + str(payload))

    def validate_payload(self, payload, payload_definition):

        unexpected_keys = []

        # check if all keys are set
        for key in payload_definition:
            if key not in payload:
                raise ValueError('Key ' + key + ' is not set')

        # check if all keys are valid
        for key in payload:
            if key not in payload_definition:
                unexpected_keys.append(key)

        # delete all keys that are not expected so that the signature matches
        for key in unexpected_keys:
            del payload[key]

        # payload is valid
        return True

    def done(self):
        print("Disconnecting from broker")
        self.client.disconnect()
        self.client.loop_stop()

    def set_controller(self, controller):
        self.controller = controller

    def prepare_fallback_path_select_message(self, startDirection):

        print("ignoring prepare_fallback_path_select_message")

        """
        # reset counter
        self.received_since_last_path_select = 0

        time.sleep(3.2)

        # checking if there was a path select message in the meantime
        if self.received_since_last_path_select > 0:
            return

        # faking callback
        self.callback('pathSelect', {'startDirection': startDirection})
        """


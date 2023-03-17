#!/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
import json
import os
import ssl
import threading
import time

# import communication_facade
from communication_facade import CommunicationFacade
from controller import env


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
    Class to hold the MQTT client communication_scripts
    Feel free to add functions and update the constructor to satisfy your requirements and
    thereby solve the task according to the specifications
    """

    received_since_last_path_select = 0

    def __init__(self, mqtt_client, logger):
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

    def __setattr__(self, attr, value):
        if attr == 'facade' and self.__dict__.get('facade', None) is not None:
            self.logger.warning('Facade is already set. Refusing to overwrite it.')

        self.__dict__[attr] = value

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
            self.logger.debug("json.loads(payload) failed")

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
            self.logger.error('Client id does not match data')
            return
        else:
            self.logger.debug('Client id matches data')

        payload = ""
        try:
            if message.payload is not None:
                payload = json.loads(message.payload.decode('utf-8'))
            else:
                self.logger.error('no payload')
        except:
            self.logger.error("json.loads failed")

        # if type notice, just print the message but do not handle it
        types_notice = ['notice', 'syntax', 'adjust']
        if 'type' in payload and payload['type'] in types_notice:
            if 'message' in payload['payload']:
                self.logger.info(payload['payload']['message'])
            else:
                self.logger.info(str(payload['payload']))
            return

        # if "from" is the client itself, ignore the message
        if 'from' in payload and payload['from'] == "debug":
            self.logger.error(str(payload['payload']))
            return

        # log on_message event, please dont remove this line, its probably the most useful debug line
        self.logger.info(message.payload.decode('utf-8'))

        # if "from" is the client itself, ignore the message
        if 'from' in payload and payload['from'] == "client":
            return

        # if "from" is debug and the message type is syntax, check if the syntax is correct
        if 'from' in payload and payload['from'] == "debug" and payload['type'] == "syntax":
            if payload['payload']['message'] == 'Incorrect':
                self.logger.info("Syntax check errors: " + str(str(payload['payload']['errors'])))
            return

        # log message
        # self.logger.debug(json.dumps(payload, indent=2))

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
            self.logger.success('Subscribed to planet/{}/{}'.format(self.planet_name, self.group_id))

        # check if message type has a callback registered and call it
        if payload['type'] in self.callbacks:
            self.callback(payload['type'], payload['payload'])
        else:
            self.logger.error('No callback for message type ' + payload['type'] + ' registered')

    # In order to keep the logging working you must provide a topic string and
    # an already encoded JSON-Object as message.

    def send_planet_message(self, topic, payload):
        """
        Sends given message to the current planet
        :param topic: String
        :param payload: Object
        :return: void
        """
        # we must have a planet name
        if self.planet_name is None:
            self.logger.error('No planet name set')
            return

        # send message
        self.check_syntax(topic, payload)
        self.__publish('planet/{}/{}'.format(self.planet_name, self.group_id), payload=payload, qos=2)

    def send_explorer_message(self, topic, payload):
        """
        Sends given message for the current explorer without planet context
        :param topic: String
        :param payload: Object
        :return: void
        """

        # send message
        self.check_syntax(topic, payload)
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
            raise

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
                self.logger.error('Payload is not valid')
                return

        # call callback
        # check if callback function signature matches the payload definition
        if len(self.callbacks[message_type].__code__.co_varnames) == len(payload) or \
                len(self.callbacks[message_type].__code__.co_varnames) == len(payload) + 1:
            # self.logger.success('Calling callback for message type ' + message_type)
            # self.logger.debug('with payload: ' + str(payload))
            # self.logger.debug('Required arguments: ' + str(self.callbacks[message_type].__code__.co_varnames))
            # self.logger.debug('Provided arguments: ' + str(payload))
            self.callbacks[message_type](**payload)
        else:
            self.logger.error('Callback function signature for "' + message_type + '" does not match payload '
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
                self.logger.error('Key ' + key + ' is missing')
                return False

        # check if all keys are valid
        for key in payload:
            if key not in payload_definition:
                self.logger.warning('Key ' + key + ' is not expected')
                unexpected_keys.append(key)
                # return False

        # delete all keys that are not expected so that the signature matches
        for key in unexpected_keys:
            self.logger.warning('Deleting key ' + key)
            del payload[key]

        # payload is valid
        return True

    def check_syntax(self, topic, payload):
        # self.__publish('comtest/{}'.format(self.group_id), payload=payload, qos=2)
        pass

    def done(self):
        print("Disconnecting from broker")
        self.client.disconnect()
        self.client.loop_stop()

    def set_controller(self, controller):
        self.controller = controller

    def prepare_fallback_path_select_message(self, startDirection):

        # reset counter
        self.received_since_last_path_select = 0

        print("received_since_last_path_select: " + str(self.received_since_last_path_select))

        # send message
        print("waiting 3s before faking server response")

        if env["SIMULATOR"]:
            time.sleep(1)  # TODO: change to 3s
        else:
            time.sleep(3.2)  # TODO: change to 3s

        print("waited 3s before faking server response")

        print("received_since_last_path_select: " + str(self.received_since_last_path_select))

        # checking if there was a path select message in the meantime
        if self.received_since_last_path_select > 0:
            print("received a path select message in the meantime, not sending fake server response")
            return
        else:
            print("sending fake server response")
            self.callback('pathSelect', {'startDirection': startDirection})
            print(str(startDirection) + " " + str(type(startDirection)))


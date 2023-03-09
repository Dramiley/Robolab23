#!/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
import json
import ssl
import paho.mqtt.client as mqtt

"""
We're using MQTT auf QoS Level 2 (exactly once) to communicate with the server.
"""

class Communication:

    # setup secrets
    group_id = '046'
    password = 'PwQ3lFHkEl'

    # setup MQTT client
    client = mqtt.Client(client_id=group_id, clean_session=False, protocol=mqtt.MQTTv31)

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

        self.client.on_message = self.safe_on_message  # Assign pre-defined callback function to MQTT client
        self.client.tls_set(tls_version=ssl.PROTOCOL_TLS)
        self.client.username_pw_set(self.group_id, password=self.password)  # Your group credentials, see the python skill-test for your group password
        self.client.connect('mothership.inf.tu-dresden.de', port=8883)

        # inital subscribe
        self.client.subscribe('explorer/{}'.format(self.group_id), qos=2)  # Subscribe to topic explorer/xxx
        self.client.loop_start()

        # save logger
        self.logger = logger

    # destructor
    def __del__(self):
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

        # YOUR CODE FOLLOWS (remove pass, please!)
        pass

    # DO NOT EDIT THE METHOD SIGNATURE
    #
    # In order to keep the logging working you must provide a topic string and
    # an already encoded JSON-Object as message.
    def send_message(self, topic, message):
        """
        Sends given message to specified channel
        :param topic: String
        :param message: Object
        :return: void
        """
        self.logger.debug('Send to: ' + topic)
        self.logger.debug(json.dumps(message, indent=2))

        # send message
        self.client.publish('explorer/{}'.format(self.group_id), payload=message, qos=2)

    # DO NOT EDIT THE METHOD SIGNATURE OR BODY
    #
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

        # debug info
        print('Got message with topic "{}":'.format(message.topic))

        try:
            self.on_message(client, data, message)
        except:
            import traceback
            traceback.print_exc()
            raise


print("communication.py loaded")

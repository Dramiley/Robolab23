#!/usr/bin/env python3

# Suggestion: Do not import the ev3dev.ev3 module in this file


class Communication:
    """
        Class to hold the MQTT client
        Feel free to add functions, change the constructor and the example send_message() to satisfy your requirements and thereby solve the task according to the specifications
    """

    def __init__(self, mqtt_client):
        """ Initializes communication module, connect to server, subscribe, etc. """
        # THESE TWO VARIABLES MUST NOT BE CHANGED
        self.client = mqtt_client
        self.client.on_message = self.on_message

        # ADD YOUR VARIABLES HERE

    # THIS FUNCTIONS SIGNATURE MUST NOT BE CHANGED
    def on_message(self, client, data, message):
        """ Handles the callback if any message arrived """
        pass

    # Example
    def send_message(self, topic, message):
        """ Sends given message to specified channel """
        pass

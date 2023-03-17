#!/usr/bin/env python3
import os
import logging
import sys

import paho.mqtt.client as mqtt
import uuid
import signal

from controller import Controller

"""
SETUP COMMUNICATION
"""
client = None  # DO NOT EDIT

"""
SETUP PROGRAM
"""

print("Starting program...")


def init_client():
    # The deploy-script uses the variable "client" to stop the mqtt-client after your program stops or crashes.
    # Your script isn't able to close the client after crashing.
    global client

    client_id = '046-' + str(uuid.uuid4())  # Replace YOURGROUPID with your group ID
    client = mqtt.Client(client_id=client_id,  # Unique Client-ID to recognize our program
                         clean_session=True,  # We want a clean session after disconnect or abort/crash
                         protocol=mqtt.MQTTv311,  # Define MQTT protocol version
                         userdata=client_id  # Pass client_id to on_connect callback
                         )
    # Setup logging directory and file
    return client


def run():
    # DO NOT CHANGE THESE VARIABLES
    #
    client = init_client()

    # THE EXECUTION OF ALL CODE SHALL BE STARTED FROM WITHIN THIS FUNCTION.
    # ADD YOUR OWN IMPLEMENTATION HEREAFTER.

    controller = Controller(client)
    controller.begin()


# DO NOT EDIT
def signal_handler(sig=None, frame=None, raise_interrupt=True):
    if client and client.is_connected():
        client.disconnect()
    if raise_interrupt:
        try:
            from robot import Robot
            robot = Robot()
            robot.stop()
            print("Stopped robot.")
        except:
            print("Could not stop robot. (This is normal if you are not running on the robot.)")
            pass

        raise KeyboardInterrupt()


"""
RUN PROGRAM
"""

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    try:
        run()
        signal_handler(raise_interrupt=False)
    except Exception as e:
        signal_handler(raise_interrupt=False)
        raise

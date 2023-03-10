#!/usr/bin/env python3

import logging
import os
import time

import paho.mqtt.client as mqtt
import uuid
import signal
import motor as m
import measurements as ms
from communication import Communication
from communication_logger import CommunicationLogger

client = None  # DO NOT EDIT


def react_to_error(message):
    print('got reaction to error')
    print('error: ' + message)


def run():
    # DO NOT CHANGE THESE VARIABLES
    #
    # The deploy-script uses the variable "client" to stop the mqtt-client after your program stops or crashes.
    # Your script isn't able to close the client after crashing.
    global client

    client_id = '046-' + str(uuid.uuid4())  # Replace YOURGROUPID with your group ID
    client = mqtt.Client(client_id=client_id,  # Unique Client-ID to recognize our program
                         clean_session=True,  # We want a clean session after disconnect or abort/crash
                         protocol=mqtt.MQTTv311  # Define MQTT protocol version
                         )
    # Setup logging directory and file
    curr_dir = os.path.abspath(os.getcwd())
    if not os.path.exists(curr_dir + '/../logs'):
        os.makedirs(curr_dir + '/../logs')
    log_file = curr_dir + '/../logs/project.log'
    logging.basicConfig(filename=log_file,  # Define log file
                        level=logging.DEBUG,  # Define default mode
                        format='%(asctime)s: %(message)s'  # Define default logging format
                        )
    logger = logging.getLogger('RoboLab')

    # THE EXECUTION OF ALL CODE SHALL BE STARTED FROM WITHIN THIS FUNCTION.
    # ADD YOUR OWN IMPLEMENTATION HEREAFTER.
    
    m.followline()
    print("Station erreicht")
    # Initialize communication_scripts, use a different logger if you want to display the communication_scripts rightaway
    communication = Communication(client, CommunicationLogger()).facade

    # setup error handling
    communication.set_callback('error', lambda message: print("FEHLER: " + message))

    # setup planet handling
    communication.ready()
    communication.set_callback('planet',
                               lambda planetName, startX, startY, startOrientation: print(
                                   'got planet %s at %s/%s/%s' % (
                                       planetName, startX, startY, startOrientation)))
    time.sleep(1)

    # setup path handling
    communication.path(0, 0, 90, 2, 4, 270, "free")
    communication.set_callback('path', lambda startX, startY, startOrientation, endX, endY, endOrientation, pathStatus,
                                              pathWeight: print(
        'got path from %s/%s/%s to %s/%s/%s with status %s and weight %s' % (
            startX, startY, startOrientation, endX, endY, endOrientation, pathStatus, pathWeight)))
    time.sleep(1)


# DO NOT EDIT
def signal_handler(sig=None, frame=None, raise_interrupt=True):
    if client and client.is_connected():
        client.disconnect()
    if raise_interrupt:
        raise KeyboardInterrupt()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    try:
        run()
        signal_handler(raise_interrupt=False)
    except Exception as e:
        signal_handler(raise_interrupt=False)
        raise

#!/usr/bin/env python3

import json
import platform

import paho.mqtt.client as mqtt
import ssl

# because we are on mac
if all(platform.mac_ver()):
    from OpenSSL import SSL


# this is a helper method that catches errors and prints them
# it is necessary because on_message is called by paho-mqtt in a different thread and exceptions
# are not handled in that thread
#
# you don't need to change this method at all
def on_message_excepthandler(client, data, message):
    print('Got message with topic "{}":'.format(message.topic))
    try:
        on_message(client, data, message)
    except:
        import traceback
        traceback.print_exc()
        raise


# Callback function for receiving messages
def on_message(client, data, message):
    print('Got message with topic "{}":'.format(message.topic))
    data = json.loads(message.payload.decode('utf-8'))
    print(json.dumps(data, indent=2))
    print("\n")


# Basic configuration of MQTT
group_id = '046'
password = 'PwQ3lFHkEl'

client = mqtt.Client(client_id=group_id, clean_session=False, protocol=mqtt.MQTTv31)

client.on_message = on_message_excepthandler  # Assign pre-defined callback function to MQTT client
client.tls_set(tls_version=ssl.PROTOCOL_TLS)
client.username_pw_set(group_id, password=password)  # Your group credentials, see the python skill-test for your group password
client.connect('mothership.inf.tu-dresden.de', port=8883)

# Start listening to incoming messages in the background
client.subscribe('explorer/{}'.format(group_id), qos=2)  # Subscribe to topic explorer/xxx
client.loop_start()

while True:
    user_input = input('Enter disconnect to close the connection...\n')

    if user_input == 'q':
        break

    # Set current planet for mothership
    msg = '''{"from":"client","type":"testPlanet","payload":{"planetName":"Mars"}}'''
    # publish message
    client.publish('explorer/{}'.format(group_id), payload=msg, qos=2)

    print('Published message to topic explorer/{}:'.format(group_id))

client.loop_stop()
client.disconnect()
print("Connection closed, program ended!")

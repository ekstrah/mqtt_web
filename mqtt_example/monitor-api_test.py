#Import essential libraries
from datetime import datetime
import argparse
import paho.mqtt.client as mqtt
import pymongo


def on_connect(client, userdata, flags, rc):
    #Connecting to existing MQTT Server
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("#")

def on_message(client, userdata, msg):
    #When Message is received
    print(msg.topic+" "+str(msg.payload))
    col = mqttDB[CTName]
    data = {'log': "Custom Messages"}
    col.insert_one(data)


PORT = 22135
USER_NAME = "ekstrah"
IP_ADDR = "127.0.0.1"
CTName = "distracted_agnesi"

client = pymongo.MongoClient("mongodb://172.17.0.1:27019/")
mqttDB = client[USER_NAME]


#Start MQTT Subscribe API
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(IP_ADDR, PORT, 60)

client.loop_forever()

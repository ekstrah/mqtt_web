import paho.mqtt.client as mqtt
import argparse
import pymongo
from datetime import datetime

topic_channel = ""
port = 1883
ip_addr = "127.0.0.1"
user_name = ""

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(topic_channel)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    col = mqttDB[CTName]
    data = {'topic': str(msg.topic), 'message': str(msg.payload.decode('utf-8')), 'time-stamp': str(datetime.now())}
    col.insert_one(data)


parser = argparse.ArgumentParser(description='MQTT Subscriber API that handles mongodb and mqtt-sub')
group1 = parser.add_argument_group("Handling Topic Words")
parser.add_argument('--topic', help="topic words eg; foo/bar", type=str)
parser.add_argument('--user', help="specify username to access database", type=str, required=True)
parser.add_argument('--ip', help="specify the ip address of container", type=str, required=True)
parser.add_argument('--ctname', help="specify the container name", type=str, required=True)
parser.add_argument('--cred', help="Provide mqtt user authentication option", type=int, required=True)
parser.add_argument('--mqttU', help="provide mqtt User Name", type=str)
parser.add_argument('--mqttP', help="provide mqtt User Password", type=str)

args = parser.parse_args()
if args.topic == None:
    topic_channel = "#"
else:
    topic_channel = args.topic
##Initializing the environment variable
port = 1883
user_name = args.user
ip_addr = args.ip
CTName = args.ctname

client = pymongo.MongoClient("mongodb://172.17.0.1:27018/")
mqttDB = client[user_name]


#Start MQTT Subscribe API
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
if args.cred == 1:
    client.username_pw_set(username=args.mqttU, password=args.mqttP)
client.connect(ip_addr, port, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()

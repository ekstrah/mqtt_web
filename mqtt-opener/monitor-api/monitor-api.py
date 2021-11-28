#Import essential libraries
from datetime import datetime
import argparse
import paho.mqtt.client as mqtt
import pymongo



#Essential Global Variable
TOPIC_CHANNEL = ""
PORT = 1883
IP_ADDR = "127.0.0.1"
USER_NAME = ""

def on_connect(client, userdata, flags, rc):
    #Connecting to existing MQTT Server
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(TOPIC_CHANNEL)

def on_message(client, userdata, msg):
    #When Message is received
    print(msg.topic+" "+str(msg.payload))
    col = mqttDB[CTName]
    data = {'log': "just customize the log", 'time-stamp': str(datetime.now())}
    col.insert_one(data)

    msg_col = msgDB[CTName]
    msgdata = {'topic': str(msg.topic), 'message': str(msg.payload.decode('utf-8')), 'time-stamp': str(datetime.now())}
    msg_col.insert_one(msgdata)

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
if args.topic is None:
    TOPIC_CHANNEL = "#"
else:
    TOPIC_CHANNEL = args.topic
##Initializing the environment variable
PORT = 1883
USER_NAME = args.user
IP_ADDR = args.ip
CTName = args.ctname

client = pymongo.MongoClient("mongodb://172.17.0.1:27019/")
mqttDB = client[USER_NAME]
msgclient = pymongo.MongoClient("mongodb://172.17.0.1:27018/")
msgDB = msgclient[USER_NAME]

#Start MQTT Subscribe API
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
if args.cred == 1:
    client.username_pw_set(username=args.mqttU, password=args.mqttP)
client.connect(IP_ADDR, PORT, 60)

client.loop_forever()
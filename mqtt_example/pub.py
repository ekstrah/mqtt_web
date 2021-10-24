# import paho.mqtt.client as mqtt #import the client1
# broker_address="127.0.0.1" 
# #broker_address="iot.eclipse.org" #use external broker
# client = mqtt.Client() #create new instance
# # client.username_pw_set(username="ekstrah", password="ulsan2015")
# client.connect(broker_address, port=20838) #connect to broker
# client.publish("house/main-light","I am testing testing")#publish

import paho.mqtt.client as mqtt #import the client1
import json
import time
import random
broker_address="127.0.0.1" 
#broker_address="iot.eclipse.org" #use external broker
client = mqtt.Client() #create new instance
# client.username_pw_set(username="ekstrah", password="ulsan2015")
client.connect(broker_address, port=24950) #connect to broker
data = {}
data['temp'] = random.randint(1, 500)
data['location'] = "Ulsan"
data['time'] = "00:00:00"
data['author'] = "Dongho Kim"


client.publish("house/office-light", json.dumps(data))#publish
print("yes published")


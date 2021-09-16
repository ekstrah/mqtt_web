import paho.mqtt.client as mqtt #import the client1
broker_address="127.0.0.1" 
#broker_address="iot.eclipse.org" #use external broker
client = mqtt.Client() #create new instance
# client.username_pw_set(username="ekstrah", password="ulsan2015")
client.connect(broker_address, port=29485) #connect to broker
client.publish("house/main-light","I am testing testing")#publish

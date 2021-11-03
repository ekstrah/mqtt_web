os_dict = {"Darwin": 0, "Windows": 1, "Linux": 2}
import os

def initialie_database(): 
    import docker
    """
        This initialize all the database that is required for hosting mqtt_web
    """
    client = docker.from_env()
    #Run credDB
    container = client.containers.run("mongo:latest", name="credDB", ports={'27017/tcp': '27017'}, detach=True)
    #Run msgDB
    container = client.containers.run("mongo:latest", name="msgDB", ports={'27017/tcp': "27018"}, detach=True)
    #Run monitorDB
    container = client.containers.run("mongo:latest", name="monitorDB", ports={'27017/tcp': "27019"}, detach=True)

    #Mosquitto Broker for Free Tier
    port_dict = {'1883/tcp' : ('0.0.0.0', 20450)}

    ABS_PATH = os.environ['PWD']
    BASIC_MQTT_CONFIG = ABS_PATH + "/config/."
    vol = {BASIC_MQTT_CONFIG: {'bind' : '/mosquitto/config/', 'mode': 'rw'}}
    container = client.containers.run(image='eclipse-mosquitto:latest', detach=True, ports=port_dict, volumes=vol)
if __name__ == "__main__":
    initialie_database()


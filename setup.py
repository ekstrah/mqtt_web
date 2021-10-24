os_dict = {"Darwin": 0, "Windows": 1, "Linux": 2}


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
if __name__ == "__main__":
    initialie_database()


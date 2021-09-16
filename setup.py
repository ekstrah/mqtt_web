import docker

client = docker.from_env()

#Run credDB
container = client.containers.run("mongo:latest", name="credDB", ports={'27017/tcp': '27017'}, detach=True)
#Run msgDB
container = client.containers.run("mongo:latest", name="msgDB", ports={'27017/tcp': "27018"}, detach=True)


import docker

client = docker.DockerClient()
arg_cmd =  "--user ekstrah --ip 172.17.0.3"
container = client.containers.run("ekstrah/mqtt_sub:0.1", arg_cmd, detach=True)
print(container.name)
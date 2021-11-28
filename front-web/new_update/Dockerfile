FROM ekstrah/ubuntu_mqtt_front:latest

WORKDIR /tmp

COPY . .

EXPOSE 20450

RUN pip3 install -r ./requirements.txt

ENTRYPOINT [ "python3" ]

CMD [ "app_docker.py" ]
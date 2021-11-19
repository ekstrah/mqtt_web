FROM ekstrah/ubuntu_mqtt_back:latest

WORKDIR /tmp

COPY . .

EXPOSE 20451

RUN pip3 install -r ./requirements.txt

ENTRYPOINT [ "bash" ]
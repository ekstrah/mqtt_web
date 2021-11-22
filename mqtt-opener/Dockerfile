FROM ubuntu:latest

WORKDIR /tmp

COPY . .

RUN apt update

RUN apt install -y software-properties-common

RUN add-apt-repository ppa:mosquitto-dev/mosquitto-ppa

RUN apt update

RUN apt install -y python3 python3-pip mosquitto docker.io

RUN pip3 install -r ./requirements.txt

EXPOSE 20451

ENTRYPOINT ["tail"]

CMD ["-f","/dev/null"]
FROM debian:latest

RUN apt update && apt upgrade -y
RUN apt install git python3-pip -y
RUN pip3 install -U pip
RUN cd /
RUN git clone https://github.com/athulser/mortyser
RUN cd mortyser
WORKDIR /mortyser
RUN pip3 install -r requirements.txt
CMD python3 bot.py
FROM ubuntu:18.04
RUN apt update && apt upgrade -y
RUN apt install -y python3-pip
COPY app /log_generator/
RUN pip3 install -r /log_generator/requirements.txt
ENV SYSLOG_TARGET=127.0.0.1
ENV TEMPLATE_NAME=cisco_asa
ENV CONFIG_MODE=environment
CMD ["/log_generator/main.py"]

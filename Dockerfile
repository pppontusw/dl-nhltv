FROM python:3.12-slim-bookworm

COPY requirements.txt requirements.txt
RUN apt-get update && apt-get install ffmpeg -y
RUN pip3 install -r requirements.txt

RUN adduser --home /home/nhltv nhltv

WORKDIR /home/nhltv

COPY nhltv_lib nhltv_lib
COPY setup.py setup.py
RUN pip3 install ./ --upgrade

RUN chown -R nhltv /home/nhltv

USER nhltv

CMD ["/bin/sh"]

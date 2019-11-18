FROM python:3.8-alpine3.10

COPY requirements.txt requirements.txt
RUN apk add --update python3 python3-dev gcc aria2 ffmpeg openssl musl-dev
RUN pip3 install -r requirements.txt

RUN adduser -D nhltv

WORKDIR /home/nhltv

COPY nhltv_lib nhltv_lib
COPY setup.py setup.py
RUN pip3 install ./ --upgrade

RUN chown -R nhltv /home/nhltv

USER nhltv

CMD ["/bin/sh"]

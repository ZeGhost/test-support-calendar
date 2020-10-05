FROM debian:stable

RUN apt-get update -yq && apt-get install -yq python3 && apt-get clean -y

RUN mkdir /app

ADD ./test.py /app

WORKDIR /app

CMD "/app/test.py"


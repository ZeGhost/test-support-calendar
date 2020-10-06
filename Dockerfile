FROM debian:stable

RUN apt-get update -yq && apt-get install -yq python3 python3-pip && apt-get clean -y

RUN pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

RUN mkdir /app

ADD ./test.py /app

WORKDIR /app

CMD "/app/test.py"


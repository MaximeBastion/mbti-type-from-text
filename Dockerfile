FROM python:3.8

COPY . /root/mbti-type-from-text/
WORKDIR /root/mbti-type-from-text/

RUN pip install -r requirements.txt
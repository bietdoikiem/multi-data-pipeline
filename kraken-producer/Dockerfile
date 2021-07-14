FROM python:3.8.8-slim-buster

WORKDIR /usr/app

ADD ./requirements.txt ./
RUN pip install -r requirements.txt
ADD ./ ./

CMD ["python3", "-u", "kraken_producer.py"]

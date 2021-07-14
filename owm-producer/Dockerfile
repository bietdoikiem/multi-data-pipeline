FROM python:3.8.8-slim-buster

WORKDIR /usr/app

RUN apt-get -y update && apt-get -y install gcc

ADD ./requirements.txt ./
RUN pip install -r requirements.txt
ADD ./ ./

CMD ["python3", "-u", "openweathermap_producer.py"]

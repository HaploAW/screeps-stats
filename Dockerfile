FROM python:3.6
MAINTAINER patryk.perduta@gmail.com

COPY screeps_etl /screeps-stats
COPY .screeps_settings.yaml /screeps-stats
COPY requirements.txt /screeps-stats
WORKDIR /screeps-stats
RUN pip install -r requirements.txt
ENV ELASTICSEARCH 1

RUN git clone https://github.com/vishnubob/wait-for-it

CMD python /screeps-stats/screepsstats.py

#!/usr/bin/env python
from bs4 import BeautifulSoup
from datetime import datetime
from elasticsearch import Elasticsearch
import getopt
import screepsapi
from settings import getSettings
import sys
import time

## Python before 2.7.10 or so has somewhat broken SSL support that throws a warning; suppress it
import warnings; warnings.filterwarnings('ignore', message='.*true sslcontext object.*')

class ScreepsConsole(screepsapi.Socket):

    es = Elasticsearch()

    def set_subscriptions(self):
        self.subscribe_user('console')
        self.subscribe_user('cpu')

    def process_log(self, ws, message):

        message_soup = BeautifulSoup(message,  "lxml")

        body = {
            'timestamp': datetime.now(),
            'mtype': 'log'
        }

        if message_soup.log:
            tag = message_soup.log
        elif message_soup.font:
            tag = message_soup.font
        else:
            tag = false

        if tag:
            for key,elem in tag.attrs.items():
                if key == 'color':
                    continue
                body[key] = elem

        message_text = message_soup.get_text()

        if ':' in message_text:
            parts = message_text.partition(':')
            message_text = parts[2]

        message_text.strip()
        body['message'] = message_text.replace("\t", ' ')

        res = self.es.index(index="screeps-console-" + time.strftime("%Y_%d"), doc_type="log", body=body)
        print res

    def process_results(self, ws, message):
        body = {
            'timestamp': datetime.now(),
            'message': message,
            'mtype': 'results'
        }
        res = self.es.index(index="screeps-console-" + time.strftime("%Y_%d"), doc_type="log", body=body)
        print res


    def process_error(self, ws, message):
        body = {
            'timestamp': datetime.now(),
            'message': message,
            'mtype': 'error',
            'severity': 5
        }
        res = self.es.index(index="screeps-console-" + time.strftime("%Y_%d"), doc_type="log", body=body)
        print res

    def process_cpu(self, ws, data):
        body = {
            'timestamp': datetime.now()
        }

        if 'cpu' in data:
            body['cpu'] = data['cpu']

        if 'memory' in data:
            body['memory'] = data['memory']

        if 'cpu' in data or 'memory' in data:
            res = self.es.index(index="screeps-performance-" + time.strftime("%Y_%d"), doc_type="performance", body=body)
            print res



if __name__ == "__main__":

    opts, args = getopt.getopt(sys.argv[1:], "hi:o:",["ifile=","ofile="])
    settings = getSettings()
    screepsconsole = ScreepsConsole(user=settings['screeps_username'], password=settings['screeps_password'], ptr=settings['screeps_ptr'])
    screepsconsole.start()

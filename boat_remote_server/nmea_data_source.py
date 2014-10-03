#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

import threading
import pynmea2
import json
import logging
from socket import *
 
class NmeaDataSource(threading.Thread):
    lock = threading.Lock()

    def __init__(self, host, port, watch_fields):
        self.logger = logging.getLogger(__name__)
        self.host = host
        self.port = port
        self.watch_fields = watch_fields
        self.connected = False
        self.sentence = ""
        self.sentences = {}
        super(NmeaDataSource, self).__init__()

    def connect(self):
        try:
            self.socket = socket(AF_INET, SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            self.logger.info("Connected to %s:%d" % (self.host, self.port))
        except AttributeError as error:
            self.logger.error("Unable to connect:", error)
            self.connected = False
            
    def close(self):
        self.logger.info("called nmeaDataSource.close())")
        self.connected = False
        
    def run(self):
        while (self.connected):
            c = self.socket.recv(1)
            if (c=='$' or c=='!'): # beginning
                self.sentence = c
            else:
                self.sentence += c
            if c=='\n': # end of sentence
            # should check checksum...
                if (self.sentence[0]=='$'):
                    self.logger.debug("Received sentence: %s" % self.sentence)
                    sentence_header, comma, sentence_body = self.sentence.partition(',')
                    sentence_header = sentence_header.lstrip('$')
                    self.sentences[sentence_header] = self.sentence
                    try:
                        msg = pynmea2.parse(self.sentence)
                        self.logger.debug("Sentence type: %s" % msg.sentence_types)
                        if not NmeaDataSource.lock.acquire(False):
                            self.logger.error("Lock failed writing watchField")
                        else:
                            try:
                                for watchField in self.watch_fields:
                                    watchField.update_value_from_message(msg)
                            finally:
                                NmeaDataSource.lock.release()
                    except ValueError as e:
                        self.logger.debug("Unknown message type received")
                    except:
                        self.logger.error("Something shitty has happened. Offender is:")
                        self.logger.error(self.sentence)
                        raise
        self.socket.close()

    def print_all_sentences(self):
        result = "<pre>"
        for sentence in self.sentences.values():
            result += sentence + "<BR>"
        result += "</pre>"
        return result

    def print_watch_data(self):
        watch_data = {}
        if not NmeaDataSource.lock.acquire(False):
            self.logger.error("Lock failed reading watch data")
        else:
            try:
                for watch_field in self.watch_fields:
                    self.logger.debug(watch_field.get_name())
                    watch_data[watch_field.get_name()] = watch_field.get_value()
                    self.logger.debug(watch_data[watch_field.get_name()])
            finally:
                NmeaDataSource.lock.release()
        result = json.dumps(watch_data)
        return result

    def get_watch_field(self, field):
        for watch_field in self.watch_fields:
            if (watch_field.get_name() == field):
                return watch_field


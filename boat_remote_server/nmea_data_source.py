#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

import threading
import pynmea2
import json
import logging
from socket import *
 
class NmeaDataSource(threading.Thread):
    lock = threading.Lock()

    def __init__(self, host, port, watchFields):
        self.logger = logging.getLogger(__name__)
        self.host = host
        self.port = port
        self.watchFields = watchFields
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
            self.logger.info("Unable to connect:", error)
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
                    #print self.sentence
                    #print self.connected
                    sentence_header, comma, sentence_body = self.sentence.partition(',')
                    sentence_header = sentence_header.lstrip('$')
                    self.sentences[sentence_header] = self.sentence
                    try:
                        msg = pynmea2.parse(self.sentence)
                        #print self.sentence
                        #print msg.type
                        #try:
                        #    print msg.temperature
                        #except:
                        #    pass
                        if not NmeaDataSource.lock.acquire(False):
                            print "lock failed writing watchField"
                        else:
                            try:
                            #NmeaDataSource.lock.acquire()
                                for watchField in self.watchFields:
                                    watchField.updateValueFromMessage(msg)
                            finally:
                                NmeaDataSource.lock.release()
                        #NmeaDataSource.lock.release()
                    except ValueError as e:
                        # catches unknown message types
                        pass
                    except:
                        self.logger.info("Something shitty has happened. Offender is:")
                        self.logger.info(self.sentence)
                        raise

        self.socket.close()

    def printAllSentences(self):
        result = "<pre>"
        for sentence in self.sentences.values():
            result += sentence + "<BR>"
        result += "</pre>"
        return result

    def printWatchData(self):
        watchData = {}
        self.logger.info("before lock")
        #NmeaDataSource.lock.acquire(0)
        if not NmeaDataSource.lock.acquire(False):
            print "lock failed reading watch data"
        else:
            try:
                self.logger.info("printing watch data")
                for watchField in self.watchFields:
                    self.logger.debug(watchField.getName())
                    watchData[watchField.getName()] = watchField.getValue()
                    self.logger.debug(watchData[watchField.getName()])
            finally:
                NmeaDataSource.lock.release()
        #NmeaDataSource.lock.release()
        #print watchData
        result = json.dumps(watchData)
        return result

    def getWatchField(self, field):
        for watchField in self.watchFields:
            if (watchField.getName() == field):
                return watchField;


#!/usr/bin/python
# -*- coding: utf-8 -*-

## Web server for providing NMEA data to a Pebble watch
# Teresa Roberts (c) 2014
# http://www.codewithasmile.co.uk
#
# Based on the excellent work of Mike Holden
# http://www.holdentechnology.com/

from socket import *
from select import *
import time, sys
import json
import BaseHTTPServer
import urlparse
import os
import logging.config

import pynmea2

from helper_functions import *
from nmea_data_source import NmeaDataSource
from config import *

def setup_logging():
    """Setup logging configuration

    """
    logging.basicConfig(level=default_level)

def set_anchor_watch():
    print "setting anchor watch"
    awf = nmeaDataSource.getWatchField("drift")
    awf.__class__ = AnchorWatchField
    awf.setAnchor()

def set_anchor_watch(lat,lon):
    print "setting anchor watch to %s %s" % (lat, lon)
    awf = nmeaDataSource.getWatchField("drift")
    awf.__class__ = AnchorWatchField
    awf.setAnchor(lat,lon)

def reset_anchor_watch():
    print "resetting anchor watch"
    awf = nmeaDataSource.getWatchField("drift")
    awf.__class__ = AnchorWatchField
    awf.resetAnchor()

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self):
        """Respond to a GET request."""
        # Send response headers
        logger.info("GET: %s" % self.path)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()
        path = self.path.lstrip('/')
        if (path == "watch"):
            if test:
                # Get mocked up data from helper_functions
                data = json.dumps(testWatchData)
            else:
                # Get the latest data from the nmeaDataSource
                logger.info("Printing watch data")
                data = nmeaDataSource.printWatchData()
        elif (path in approved_files):
            f=open(fname.lstrip('/'),'r')
            data = f.read()
            f.close()
        elif (path=="NMEA"):
            data = nmeaDataSource.printAllSentences()     
        else:
            f = open("index.html",'r')
            data = f.read()
            f.close()
        self.wfile.write(data)

    def do_POST(self):
        """Respond to a POST request."""
        # Send response headers
        logger.info("POST: %s" % self.path)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        path = self.path.lstrip('/')
        if (path == "set_anchor_watch"):
            logger.debug("Setting Anchor Watch!")
            length = int(self.headers['Content-Length'])
            post_data = urlparse.parse_qs(self.rfile.read(length).decode('utf-8'))
            if ((post_data.has_key("lat")) and (post_data.has_key("lon"))):
                set_anchor_watch(post_data["lat"][0],post_data["lon"][0])
            else:
                set_anchor_watch()
        if (path == "reset_anchor_watch"):
            logger.debug("Resetting Anchor Watch!")
            reset_anchor_watch()
            
        

if __name__ == '__main__':
    setup_logging()
    logger = logging.getLogger(__name__)
    # initialize tcp port
    nmeaDataSource = NmeaDataSource(NMEA_HOST, NMEA_PORT, watchFields)
    if not test:
        nmeaDataSource.connect()
        nmeaDataSource.start()

    approved_files = ("speeddepth.html","index.html","info.html")

    httpd = BaseHTTPServer.HTTPServer((HTTP_HOST, HTTP_PORT), MyHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HTTP_HOST, HTTP_PORT)
    try:
        logger.info("serving forever")
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("interrupted")
    nmeaDataSource.close()
    nmeaDataSource.join()
    httpd.server_close()
    logger.info(time.asctime(), "Server Stops - %s:%s" % (HTTP_HOST, HTTP_PORT))

    ##===================================

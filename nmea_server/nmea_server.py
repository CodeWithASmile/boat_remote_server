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

import BV4111
import pynmea2

from helper_functions import *
from nmea_data_source import NmeaDataSource
from config import *

sp = BV4111.sv3clV2_2.Connect("/dev/ttyAMA0",115200)
Devd = BV4111.bv4111(sp,'d')

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def get_relay_state(self):
        Devd.send("i\r")
        return Devd.read()

    def toggle_lights(self):
        

        print "Current relay state(?): %b" + get_relay_state()
        Devd.Rly(8,1,0)
        time.sleep(0.2)
        print "New relay state(?): %b" + get_relay_state()
        Devd.Rly(8,0,0)
        time.sleep(0.2)
        Devd.Rly(8,1,0)


    def do_GET(self):
        """Respond to a GET request."""
        # Send response headers
        print "GET: %s" % self.path
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
        print "POST: %s" % self.path
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        path = self.path.lstrip('/')
        if (path == "toggle_lights"):
            print "Toggling lights!"
            self.toggle_lights()
            
        

if __name__ == '__main__':
    # initialize tcp port
    nmeaDataSource = NmeaDataSource(NMEA_HOST, NMEA_PORT, watchFields)
    if not test:
        nmeaDataSource.connect()
        nmeaDataSource.start()

    approved_files = ("speeddepth.html","index.html","info.html")

    httpd = BaseHTTPServer.HTTPServer((HTTP_HOST, HTTP_PORT), MyHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HTTP_HOST, HTTP_PORT)
    try:
        print "serving forever"
        httpd.serve_forever()
    except KeyboardInterrupt:
        print "interrupted"
    nmeaDataSource.close()
    nmeaDataSource.join()
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HTTP_HOST, HTTP_PORT)

    ##===================================

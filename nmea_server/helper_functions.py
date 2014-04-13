#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

from datetime import datetime
import pynmea2
import re

ERROR_STRING = "~"

class WatchField(object):
    """Represents a field which will be displayed on a pebble watch"""
    
    def __init__(self, name, value=ERROR_STRING, formatFunction=None, timeout=5):
        self.name = name;
        self.value = value;
        self.formatFunction = formatFunction;
        self.lastUpdated = datetime.now();
        self.timeout = timeout;

    def getValue(self):
        if ((datetime.now()-self.lastUpdated).seconds > self.timeout):
            return ERROR_STRING
        elif (self.formatFunction is not None):
            return self.formatFunction(self.value)
        else:
            return self.value
            
    def setValue(self, value):
        self.value = value;
        self.lastUpdated = datetime.now();

    def getName(self):
        return self.name;

class NmeaWatchField(WatchField):
    """Represents an NMEA field which will be displayed on a pebble watch"""

    def __init__(self, name, properties, value=ERROR_STRING, formatFunction=None,
                 timeout=5):
        self.properties=properties;
        super(NmeaWatchField, self).__init__(name, value=value,
                                             formatFunction=formatFunction,
                                             timeout=timeout);

    def getSentences(self):
        return self.properties.keys();

    def getProperty(self, sentence):
        return self.properties[sentence];

    def updateValueFromMessage(self, msg):
        if (getattr(msg,"sentence_type",None) in self.properties.keys()):
            prop = self.properties[msg.sentence_type]
            value = getattr(msg, prop, ERROR_STRING)
            self.setValue(str(value))

    def getValue(self):
        if (self.value == "None"):
            return ERROR_STRING;
        else:
            return super(NmeaWatchField, self).getValue();

# Formatting functions for watch fields

def deg_to_dms(deg):
    d = int(float(deg))
    m = abs(float(deg) - d) * 60
    return d, m

def formatLatitude(deg):
    try:
        d, m = deg_to_dms(deg)
        if (d < 0):
            c = "S"
        else:
            c = "N"
        result = "%02d%s%.3f%s" % (d, u'\N{DEGREE SIGN}', m, c)
        return result
    except ValueError:
        return deg

def formatLat(deg):
    try:
        d, m = re.match('^(\d+)(\d\d\.\d+)$', deg).groups()
        result = "%02d%s%.3f" % (int(d), u'\N{DEGREE SIGN}', float(m))
        return result
    except AttributeError, TypeError:
        return deg
    

def formatLongitude(deg):
    try:
        d, m = deg_to_dms(deg)
        if (d < 0):
            c = "W"
        else:
            c = "E"
        result = "%03d%s%.3f%s" % (d, u'\N{DEGREE SIGN}', m, c)
        return result
    except ValueError:
        return deg

def formatLon(deg):
    try:
        d, m = re.match('^(\d+)(\d\d\.\d+)$', deg).groups()
        result = "%03d%s%.3f" % (int(d), u'\N{DEGREE SIGN}', float(m))
        return result
    except AttributeError, TypeError:
        return deg

def formatSog(sog):
    try:
        return "%.1f kts" % float(sog);
    except ValueError:
        return sog;

def formatAngle(angle):
    try:
        return "%03d%s" % (int(float(angle)),u'\N{DEGREE SIGN}');
    except ValueError:
        return angle;

def formatDistanceUnit(unit):
    if unit == "N":
        return "NM";
    return unit;

def formatDepth(depth):
    try:
        return "%.1f m" % float(depth);
    except ValueError:
        return depth;

def formatDistanceNM(distance):
    try:
        return "%.1f NM" % float(distance);
    except ValueError:
        return distance

def formatWindAngle(angle):
    try:
        a = int(float(angle))
        if (a > 180):
            return "%03d P" % (360-a)
        else:
            return "%03d S" % a
    except ValueError:
        return angle

def formatType(t):
    return "(" + t + ")"

# Test data

testWatchData = { 'lat': '66°33.123N',
                  'lon': '001°33.123E',
                  'sog': '4.5 kts',
                  'cog': '102°',
                  'boat_speed': '4.2 kts',
                  'depth': '15.2 m',
                  'wind_speed': '12.7 kts',
                  'wind_angle': '54° P',
                  'dtw': '1.4',
                  'dtw_unit': 'NM',
                  'btw': '256°',
                  'xte': '0.02',
                  'xte_unit': 'NM',
                  'dir_to_steer': 'L',
                  'heading_to_steer': '256°',
                  'heading_to_steer_type': '(M)',
                  'waypoint': 'Waypoint 1',
                  'wpt_lat': '21°34.105',
                  'wpt_lat_dir': 'S',
                  'wpt_lon': '311°22.543',
                  'wpt_lon_dir': 'W',
                  'temp': '24.2',
                  'temp_unit': '°C',
                  'heading': '102°',
                  'distance_total': '102 NM',
                  'distance_reset': '57 NM'};
        

            
        
        
            
        
    

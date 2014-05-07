#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

from datetime import datetime
import pynmea2
import re

ERROR_STRING = "~"

class WatchField(object):
    """Represents a field which will be displayed on a pebble watch"""
    
    def __init__(self, name, value=ERROR_STRING, formatFunction=None, timeout=5):
        self.name = name
        self.values = [value]
        self.formatFunction = formatFunction
        self.lastUpdated = datetime.now()
        self.timeout = timeout

    def getValue(self):
        if ((datetime.now()-self.lastUpdated).seconds > self.timeout):
            return ERROR_STRING
        elif (self.formatFunction is not None):
            return self.formatFunction(self.values)
        else:
            return ' '.join(self.values)
            
    def setValues(self, values):
        self.values = values;
        self.lastUpdated = datetime.now();

    def getName(self):
        return self.name;

class NmeaWatchField(WatchField):
    """Represents an NMEA field which will be displayed on a pebble watch"""

    def __init__(self, name, sentence, fields, value=ERROR_STRING, formatFunction=None,
                 timeout=5):
        self.sentence=sentence
        self.fields = fields
        super(NmeaWatchField, self).__init__(name, value=value,
                                             formatFunction=formatFunction,
                                             timeout=timeout);

    def getSentence(self):
        return self.sentence;

    def getFields(self):
        return self.fields;

    def updateValueFromMessage(self, msg):
        values = []
        if (getattr(msg,"sentence_type",None) == self.sentence):
            for field in self.fields:
                values.append(str(getattr(msg, field, ERROR_STRING)))
            self.setValues(values)

    def getValue(self):
        if (len(self.values) == 0):
            return ERROR_STRING;
        else:
            return super(NmeaWatchField, self).getValue();

# Formatting functions for watch fields

def deg_to_dms(deg):
    d = int(float(deg))
    m = abs(float(deg) - d) * 60
    return d, m

def formatLatitude(values):
    deg = values[0]
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

def formatLat(values):
    deg = values[0]
    try:
        d, m = re.match('^(\d+)(\d\d\.\d+)$', deg).groups()
        result = "%02d%s%.3f" % (int(d), u'\N{DEGREE SIGN}', float(m))
        return result
    except AttributeError, TypeError:
        return deg
    

def formatLongitude(values):
    deg = values[0]
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

def formatLon(values):
    deg = values[0]
    try:
        d, m = re.match('^(\d+)(\d\d\.\d+)$', deg).groups()
        result = "%03d%s%.3f" % (int(d), u'\N{DEGREE SIGN}', float(m))
        return result
    except AttributeError, TypeError:
        return deg

def formatSog(values):
    sog = values[0]
    try:
        return "%.1f kts" % float(sog);
    except ValueError:
        return sog;

def formatAngle(values):
    angle = values[0]
    try:
        return "%03d%s" % (int(float(angle)),u'\N{DEGREE SIGN}');
    except ValueError:
        return angle;

def formatDistanceUnit(values):
    unit = values[0]
    if unit == "N":
        return "NM";
    return unit;

def formatDepth(values):
    depth = values[0]
    offset = values[1]
    try:
        return "%.1f m" % float(depth+offset);
    except ValueError, IndexError:
        return depth;

def formatDistanceNM(values):
    distance = values[0]
    try:
        return "%.1f NM" % float(distance);
    except ValueError:
        return distance

def formatWindAngle(values):
    angle = values[0]
    try:
        a = int(float(angle))
        if (a > 180):
            return "%03d P" % (360-a)
        else:
            return "%03d S" % a
    except ValueError:
        return angle

def formatType(values):
    t = values[0]
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
        

            
        
        
            
        
    

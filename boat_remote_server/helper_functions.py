#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

from datetime import datetime
import pynmea2
import re
import math

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
            #print self.sentence
            for field in self.fields:
                #print field
                values.append(str(getattr(msg, field, ERROR_STRING)))
            #print values
            self.setValues(values)

    def getValue(self):
        if (len(self.values) == 0):
            return ERROR_STRING
        else:
            return super(NmeaWatchField, self).getValue()

class AnchorWatchField(NmeaWatchField):
    """Represents how far boat is from its anchor"""

    def __init__(self, name, sentence, fields, value=ERROR_STRING,
                 timeout=5):
        self.resetAnchor()
        self.current_lat = None
        self.current_lon = None
        super(AnchorWatchField, self).__init__(name, sentence=sentence, fields=fields, value=value, 
                                               formatFunction=None, timeout=5)
    
    def setAnchor(self):
        print "called set anchor"
        self.anchor_lat = self.current_lat
        self.anchor_lon = self.current_lon

    def resetAnchor(self):
        self.anchor_lat = None
        self.anchor_lon = None

    def updateValueFromMessage(self, msg):
        super(AnchorWatchField, self).updateValueFromMessage(msg)
        try:
            self.current_lat = float(self.values[0])
            self.current_lon = float(self.values[1])
        except IndexError:
            self.current_lat = None
            self.current_lon = None

    def getValue(self):
        if ((datetime.now()-self.lastUpdated).seconds > self.timeout):
            return ERROR_STRING
        if self.anchor_lat is not None:
            self.drift = self.calculateDrift()
            return self.drift;
        else:  
            return ERROR_STRING
            

    def calculateDrift(self):
        # Convert latitude and longitude to 
        # spherical coordinates in radians.
        degrees_to_radians = math.pi/180.0
        
        # phi = 90 - latitude
        phi1 = (90.0 - self.anchor_lat)*degrees_to_radians
        phi2 = (90.0 - self.current_lat)*degrees_to_radians
        
        # theta = longitude
        theta1 = self.anchor_lon*degrees_to_radians
        theta2 = self.current_lon*degrees_to_radians
        
        # Compute spherical distance from spherical coordinates.
        
        # For two locations in spherical coordinates 
        # (1, theta, phi) and (1, theta, phi)
        # cosine( arc length ) = 
        #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
        # distance = rho * arc length
    
        cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
               math.cos(phi1)*math.cos(phi2))
        arc = math.acos( cos )

        # Remember to multiply arc by the radius of the earth 
        # in your favorite set of units to get length.
        result = "%d m" % math.floor(arc *6373000) #returns result in meters.
        return result

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
    try:
        deg = values[0]
        dir = values[1]
        d, m = re.match('^(\d+)(\d\d\.\d+)$', deg).groups()
        result = "%02d%s%.3f %s" % (int(d), u'\N{DEGREE SIGN}', float(m), dir)
        return result
    except (AttributeError, TypeError, IndexError):
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
    try:
        deg = values[0]
        dir = values[1]
        d, m = re.match('^(\d+)(\d\d\.\d+)$', deg).groups()
        result = "%03d%s%.3f %s" % (int(d), u'\N{DEGREE SIGN}', float(m), dir)
        return result
    except (AttributeError, TypeError, IndexError):
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
        return angle

def formatDistance(values):
    try:
        distance = values[0]
        unit = values[1]
        if unit == "N":
            unit == "NM"
        return "%s %s" % (distance, unit)
    except IndexError:
        return distance

def formatDepth(values):
    try:
        depth = values[0]
        offset = values[1]
        return "%.1f m" % (float(depth) + float(offset));
    except (ValueError, IndexError):
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
            return "%d P" % (360-a)
        else:
            return "%d S" % a
    except ValueError:
        return angle

def formatWindSpeed(values):
    try:
        speed = values[0]
        unit = values[1]
        if (unit == "N"):
            unit = "kts"
        elif (unit == "K"):
            unit = "kph"
        elif (unit == "M"):
            unit = "m/s"
        return "%s %s" % (speed, unit)
    except (ValueError, IndexError):
        return values

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
        

            
        
        
            
        
    

#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

from datetime import datetime
import pynmea2
import re
import math
import logging
import json
import os

ERROR_STRING = "~"

class WatchField(object):
    """Represents a field which will be displayed on a pebble watch"""
    
    def __init__(self, name, value=ERROR_STRING, format_function=None, timeout=5):
        self.name = name
        self.values = [value]
        self.format_function = format_function
        self.last_updated = datetime.now()
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)

    def get_value(self):
        if ((datetime.now()-self.last_updated).seconds > self.timeout):
            self.logger.debug("Field timeout: %s" % self.name)
            return ERROR_STRING
        elif (self.format_function is not None):
            return self.format_function(self.values)
        else:
            return ' '.join(self.values)
            
    def set_values(self, values):
        self.values = values;
        self.last_updated = datetime.now();

    def get_name(self):
        return self.name;

class NmeaWatchField(WatchField):
    """Represents an NMEA field which will be displayed on a pebble watch"""

    def __init__(self, name, sentence, fields, value=ERROR_STRING, format_function=None,
                 timeout=5):
        self.sentence=sentence
        self.fields = fields
        super(NmeaWatchField, self).__init__(name, value=value,
                                             format_function=format_function,
                                             timeout=timeout);

    def get_sentence(self):
        return self.sentence;

    def get_fields(self):
        return self.fields;

    def update_value_from_message(self, msg):
        values = []
        if (getattr(msg,"sentence_type",None) == self.sentence):
            for field in self.fields:
                values.append(str(getattr(msg, field, ERROR_STRING)))
            self.logger.debug("Setting %s to %s" % (self.name, values))
            self.set_values(values)

    def get_value(self):
        if (len(self.values) == 0):
            return ERROR_STRING
        else:
            return super(NmeaWatchField, self).get_value()

class AnchorWatchField(NmeaWatchField):
    """Represents how far boat is from its anchor"""

    def __init__(self, name, sentence, fields, value=ERROR_STRING,
                 timeout=5):
        self.file_path = "anchor_location.txt"
        self.restore_anchor()
        self.current_loc = []
        super(AnchorWatchField, self).__init__(name, sentence=sentence, fields=fields, value=value, 
                                               formatFunction=None, timeout=5)

    def store_anchor(self):
        with open(self.file_path, 'w') as outfile:
            json.dump(self.anchor_loc, outfile)

    def restore_anchor(self):
        try:
            with open(self.file_path, 'r') as infile:
                self.anchor_loc =json.load(infile)
        except IOError:
            self.anchor_loc = []


    def set_anchor(self):
        self.anchor_loc = self.current_loc
        self.store_anchor()
        self.logger.info("Anchor position = %f,%f" % (self.anchor_loc[0], self.anchor_loc[1]))
        self.logger.info("Drift = %s" % self.calculate_drift())

    def set_anchor_loc(self, lat, lon):
        print "called set anchor"
        self.anchor_loc = [float(lat), float(lon)]
        self.store_anchor()
        self.logger.info("Anchor position = %f,%f" % (self.anchor_loc[0], self.anchor_loc[1]))
        self.logger.info("Current position = %f,%f" % (self.current_loc[0], self.current_loc[1]))
        self.logger.info("Drift = %s" % self.calculate_drift())
                                                   

    def reset_anchor(self):
        self.logger.info("Resetting Anchor")
        self.anchor_loc = []
        os.remove(self.file_path)

    def update_value_from_message(self, msg):
        super(AnchorWatchField, self).update_value_from_message(msg)
        try:
            self.current_loc = [float(self.values[0]), float(self.values[1])]
        except IndexError:
            self.current_loc = []

    def get_value(self):
        if ((datetime.now()-self.last_updated).seconds > self.timeout):
            return ERROR_STRING
        if len(self.anchor_loc) > 0 and len(self.current_loc) > 0:
            self.drift = self.calculate_drift()
            return self.drift;
        else:  
            return ERROR_STRING
            

    def calculate_drift(self):
        # Convert latitude and longitude to 
        # spherical coordinates in radians.
        degrees_to_radians = math.pi/180.0
        
        # phi = 90 - latitude
        phi1 = (90.0 - self.anchor_loc[0])*degrees_to_radians
        phi2 = (90.0 - self.current_loc[0])*degrees_to_radians
        
        # theta = longitude
        theta1 = self.anchor_loc[1]*degrees_to_radians
        theta2 = self.current_loc[1]*degrees_to_radians
        
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

def format_latitude(values):
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

def format_lat(values):
    try:
        deg = values[0]
        dir = values[1]
        d, m = re.match('^(\d+)(\d\d\.\d+)$', deg).groups()
        result = "%02d%s%.3f %s" % (int(d), u'\N{DEGREE SIGN}', float(m), dir)
        return result
    except (AttributeError, TypeError, IndexError):
        return deg
    

def format_longitude(values):
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

def format_lon(values):
    try:
        deg = values[0]
        dir = values[1]
        d, m = re.match('^(\d+)(\d\d\.\d+)$', deg).groups()
        result = "%03d%s%.3f %s" % (int(d), u'\N{DEGREE SIGN}', float(m), dir)
        return result
    except (AttributeError, TypeError, IndexError):
        return deg

def format_SOG(values):
    SOG = values[0]
    try:
        return "%.1f kts" % float(sog);
    except ValueError:
        return SOG

def format_angle(values):
    angle = values[0]
    try:
        return "%03d%s" % (int(float(angle)),u'\N{DEGREE SIGN}');
    except ValueError:
        return angle

def format_distance(values):
    try:
        distance = values[0]
        unit = values[1]
        if unit == "N":
            unit == "NM"
        return "%s %s" % (distance, unit)
    except IndexError:
        return distance

def format_depth(values):
    try:
        depth = values[0]
        offset = values[1]
        return "%.1f m" % (float(depth) + float(offset));
    except (ValueError, IndexError):
        return depth;

def format_distance_NM(values):
    distance = values[0]
    try:
        return "%.1f NM" % float(distance);
    except ValueError:
        return distance

def format_wind_angle(values):
    angle = values[0]
    try:
        a = int(float(angle))
        if (a > 180):
            return "%d P" % (360-a)
        else:
            return "%d S" % a
    except ValueError:
        return angle

def format_wind_speed(values):
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

def format_type(values):
    t = values[0]
    return "(" + t + ")"
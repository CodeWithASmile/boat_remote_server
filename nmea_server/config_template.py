#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

from helper_functions import *

test = False

HTTP_HOST = ''
HTTP_PORT = 8082 # The port that the HTTP data will be output on

NMEA_HOST = '192.168.5.200'     # The host with the NMEA TCP feed
NMEA_PORT = 10110              # The port with the NMEA TCP feed

basePath = "/home/pi/nmea_server/nmea_server";

watchFields = [NmeaWatchField(name="lat", sentence="RMC", fields=["latitude"],
                              formatFunction=formatLatitude),
               NmeaWatchField(name="lon", sentence="RMC", fields=["longitude"],
                              formatFunction=formatLongitude),
               NmeaWatchField(name="cog", sentence="RMC", fields=["true_course"],
                              formatFunction=formatAngle),
               NmeaWatchField(name="sog", sentence="RMC", fields=["spd_over_grnd"],
                              formatFunction=formatSog),
               NmeaWatchField(name="xte", sentence="APB", fields=["cross_track_err_mag", "cross_track_unit"],
                              formatFunction=formatDistance),
               NmeaWatchField(name="waypoint", sentence="BWC", fields=["waypoint_name"]),
               NmeaWatchField(name="wpt_lat", sentence="BWC", fields=["lat_next", "lat_next_direction"],
                              formatFunction=formatLat),
               NmeaWatchField(name="wpt_lon", sentence="BWC", fields=["lon_next", "lon_next_direction"],
                              formatFunction=formatLon),       
               NmeaWatchField(name="dtw", sentence="BWC", fields=["range_next", "range_unit"],
                              formatFunction=formatDistance),
               NmeaWatchField(name="btw", sentence="BWC", fields=["true_track"],
                              formatFunction=formatAngle),
               NmeaWatchField(name="depth", sentence="DPT", fields=["depth", "offset"],
                              formatFunction=formatDepth),
               NmeaWatchField(name="temp", sentence="MTW", fields=["temperature", "units"]),
               NmeaWatchField(name="boat_speed", sentence="VHW", fields=["water_speed_knots"],
                              formatFunction=formatSog),
               NmeaWatchField(name="heading", sentence="VHW", fields=["heading_true"],
                              formatFunction=formatAngle),
               NmeaWatchField(name="distance_total", sentence="VLW", fields=["trip_distance"],
                              formatFunction=formatDistanceNM),
               NmeaWatchField(name="distance_reset", sentence="VLW", fields=["trip_distance_reset"],
                              formatFunction=formatDistanceNM),
               NmeaWatchField(name="wind_angle", sentence="MWV", fields=["wind_angle"],
                              formatFunction=formatWindAngle),
               NmeaWatchField(name="wind_speed", sentence="MWV", fields=["wind_speed", "wind_speed_units"],
                              formatFunction=formatWindSpeed),
               AnchorWatchField(name="drift", sentence="RMC", fields=["latitude", "longitude"])]

control = True

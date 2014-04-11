#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

from helper_functions import *

test = False;

HTTP_HOST = '';
HTTP_PORT = 8082; # The port that the HTTP data will be output on

NMEA_HOST = '192.168.5.200';     # The host with the NMEA TCP feed
NMEA_PORT = 10110;              # The port with the NMEA TCP feed

watchFields = [NmeaWatchField(name="lat", properties={"RMC":"latitude"},
                              formatFunction=formatLatitude),
               NmeaWatchField(name="lon", properties={"RMC":"longitude"},
                              formatFunction=formatLongitude),
               NmeaWatchField(name="cog", properties={"RMC":"true_course"},
                              formatFunction=formatAngle),
               NmeaWatchField(name="sog", properties={"RMC":"spd_over_grnd"},
                              formatFunction=formatSog),
               NmeaWatchField(name="xte", properties={"APB":"cross_track_err_mag"}),
               NmeaWatchField(name="xte_unit", properties={"APB":"cross_track_unit"},
                              formatFunction=formatDistanceUnit),
               NmeaWatchField(name="dir_to_steer", properties={"APB":"dir_steer"}),
               NmeaWatchField(name="heading_to_steer", properties={"APB":"heading_to_dest"},
                              formatFunction=formatAngle),
               NmeaWatchField(name="heading_to_steer_type", properties={"APB":"heading_to_dest_type"},
                              formatFunction=formatType),
               NmeaWatchField(name="waypoint", properties={"BWC":"waypoint_name"}),
               NmeaWatchField(name="wpt_lat", properties={"BWC":"lat_next"},
                              formatFunction=formatLat),
               NmeaWatchField(name="wpt_lat_dir", properties={"BWC":"lat_next_direction"}),
               NmeaWatchField(name="wpt_lon", properties={"BWC":"lon_next"},
                              formatFunction=formatLon),       
               NmeaWatchField(name="wpt_lon_dir", properties={"BWC":"lon_next_direction"}),
               NmeaWatchField(name="dtw", properties={"BWC":"range_next"}),
               NmeaWatchField(name="dtw_unit", properties={"BWC":"range_unit"},
                              formatFunction=formatDistanceUnit),
               NmeaWatchField(name="btw", properties={"BWC":"true_track"},
                              formatFunction=formatAngle),
               NmeaWatchField(name="depth", properties={"DPT":"depth"},
                              formatFunction=formatDepth),
               NmeaWatchField(name="temp", properties={"MTW":"temperature"}),
               NmeaWatchField(name="temp_unit", properties={"MTW":"units"}),
               NmeaWatchField(name="boat_speed", properties={"VHW":"water_speed_knots"},
                              formatFunction=formatSog),
               NmeaWatchField(name="heading", properties={"VHW":"heading_true"},
                              formatFunction=formatAngle),
               NmeaWatchField(name="distance_total", properties={"VLW":"trip_distance"},
                              formatFunction=formatDistanceNM),
               NmeaWatchField(name="distance_reset", properties={"VLW":"trip_distance_reset"},
                              formatFunction=formatDistanceNM),
               NmeaWatchField(name="wind_angle", properties={"MWV":"wind_angle"},
                              formatFunction=formatWindAngle),
               NmeaWatchField(name="wind_speed", properties={"MWV":"wind_speed"})];

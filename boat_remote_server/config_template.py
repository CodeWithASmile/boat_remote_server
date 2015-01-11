#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

from helper_functions import *

HTTP_HOST = ''
HTTP_PORT = 8082 # The port that the HTTP data will be output on

NMEA_HOST = '192.168.5.200'     # The host with the NMEA TCP feed
NMEA_PORT = 10110              # The port with the NMEA TCP feed

watch_fields = [NmeaWatchField(name="lat", sentence="RMC", fields=["latitude"],
                              format_function=format_latitude),
               NmeaWatchField(name="lon", sentence="RMC", fields=["longitude"],
                              format_function=format_longitude),
               NmeaWatchField(name="cog", sentence="RMC", fields=["true_course"],
                              format_function=format_angle),
               NmeaWatchField(name="sog", sentence="RMC", fields=["spd_over_grnd"],
                              format_function=format_SOG),
               NmeaWatchField(name="xte", sentence="APB", fields=["cross_track_err_mag", "cross_track_unit"],
                              format_function=format_distance),
               NmeaWatchField(name="waypoint", sentence="BWC", fields=["waypoint_name"]),
               NmeaWatchField(name="wpt_lat", sentence="BWC", fields=["lat_next", "lat_next_direction"],
                              format_function=format_lat),
               NmeaWatchField(name="wpt_lon", sentence="BWC", fields=["lon_next", "lon_next_direction"],
                              format_function=format_lon),       
               NmeaWatchField(name="dtw", sentence="BWC", fields=["range_next", "range_unit"],
                              format_function=format_distance),
               NmeaWatchField(name="btw", sentence="BWC", fields=["true_track"],
                              format_function=format_angle),
               NmeaWatchField(name="depth", sentence="DPT", fields=["depth", "offset"],
                              format_function=format_depth),
               NmeaWatchField(name="temp", sentence="MTW", fields=["temperature", "units"]),
               NmeaWatchField(name="boat_speed", sentence="VHW", fields=["water_speed_knots"],
                              format_function=format_SOG),
               NmeaWatchField(name="heading", sentence="VHW", fields=["heading_true"],
                              format_function=format_angle),
               NmeaWatchField(name="distance_total", sentence="VLW", fields=["trip_distance"],
                              format_function=format_distance_NM),
               NmeaWatchField(name="distance_reset", sentence="VLW", fields=["trip_distance_reset"],
                              format_function=format_distance_NM),
               NmeaWatchField(name="wind_angle", sentence="MWV", fields=["wind_angle"],
                              format_function=format_wind_angle),
               NmeaWatchField(name="wind_speed", sentence="MWV", fields=["wind_speed", "wind_speed_units"],
                              format_function=format_wind_speed),
               AnchorWatchField(name="drift", sentence="RMC", fields=["latitude", "longitude"])
               ]

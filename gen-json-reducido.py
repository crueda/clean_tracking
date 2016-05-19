#!/usr/bin/env python
#-*- coding: UTF-8 -*-

# autor: Carlos Rueda
# date: 2016-05-19
# version: 1.1

##################################################################################
# version 1.0 release notes: extract data from MySQL and generate json
# Initial version
# Requisites: library python-mysqldb. To install: "apt-get install python-mysqldb"
##################################################################################


import MySQLdb
import logging, logging.handlers
import os
import json
import sys
import datetime
import calendar
import time

from math import radians, cos, sin, asin, sqrt

#### VARIABLES #########################################################
from configobj import ConfigObj
config = ConfigObj('./gen-json.properties')

INTERNAL_LOG_FILE = config['directory_logs'] + "/gen-json.log"
LOG_FOR_ROTATE = 10

MYSQL_IP = config['mysql_host']
MYSQL_PORT = config['mysql_port']
MYSQL_USER = config['mysql_user']
MYSQL_NAME = config['mysql_db_name']
MYSQL_PASSWORD = config['mysql_passwd']

DEVICE_ID = config['device_id']
INIT_DATE = config['init_date']
END_DATE = config['end_date']
FILTER_DISTANCE = config['filter_distance']

from json import encoder
encoder.FLOAT_REPR = lambda o: format(o, '.4f')

 
########################################################################
# definimos los logs internos que usaremos para comprobar errores
try:
	logger = logging.getLogger('wrc-json')
	loggerHandler = logging.handlers.TimedRotatingFileHandler(INTERNAL_LOG_FILE , 'midnight', 1, backupCount=10)
	formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	loggerHandler.setFormatter(formatter)
	logger.addHandler(loggerHandler)
	logger.setLevel(logging.DEBUG)
except:
	print '------------------------------------------------------------------'
	print '[ERROR] Error writing log at %s' % INTERNAL_LOG_FILE
	print '[ERROR] Please verify path folder exits and write permissions'
	print '------------------------------------------------------------------'
	exit()
########################################################################

########################################################################

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r * 1000

def getUTC():
	t = calendar.timegm(datetime.datetime.utcnow().utctimetuple())
	return int(t)


def getTracking():
	dbKyros4 = MySQLdb.connect(MYSQL_IP, MYSQL_USER, MYSQL_PASSWORD, MYSQL_NAME)
	try:
		dbKyros4 = MySQLdb.connect(MYSQL_IP, MYSQL_USER, MYSQL_PASSWORD, MYSQL_NAME)
	except:
		logger.error('Error connecting to database: IP:%s, USER:%s, PASSWORD:%s, DB:%s', MYSQL_IP, MYSQL_USER, MYSQL_PASSWORD, MYSQL_NAME)

	cursor = dbKyros4.cursor()
	cursor.execute("""SELECT 
		round(POS_LATITUDE_DEGREE,5) + round(POS_LATITUDE_MIN/60,5) as LAT, 
		round(POS_LONGITUDE_DEGREE,5) + round(POS_LONGITUDE_MIN/60,5) as LON, 
		round(GPS_SPEED,1) as speed,
		round(HEADING,1) as heading,
		POS_DATE as DATE 
		FROM TRACKING
		WHERE DEVICE_ID = """ + DEVICE_ID +
		""" AND POS_DATE > """ + INIT_DATE +
		""" AND POS_DATE < """ + END_DATE + 
		""" ORDER BY POS_DATE""")
	result = cursor.fetchall()
	
	try:
		return result
	except Exception, error:
		logger.error('Error getting data from database: %s.', error )
		
	cursor.close
	dbFrontend.close

array_list = []
trackingInfo_reducido = []
trackingInfo = getTracking()

lat_anterior = 0
lon_anterior = 0
ntrackings = 0
time_anterior = 0
for tracking in trackingInfo:
	lat = tracking[0]
	lon = tracking[1]
	speed = tracking[2]
	heading = tracking[3]
	time = tracking[4]

	if (lat_anterior == 0):
		lat_anterior = lat
		lon_anterior = lon
		time_anterior = time
		trackingInfo_reducido.append([lat,lon,speed,heading])

	distance = haversine(lon_anterior, lat_anterior, lon, lat)
	diff_time =  (time - time_anterior) / 1000
	#print diff_time

	if ( diff_time> 900):
	#if ( distance> 100):
		trackingInfo_reducido.append([lat,lon,speed,heading])
		ntrackings+=1

		lon_anterior = lon
		lat_anterior = lat
		time_anterior = time

	#else:
		#print distance


print ntrackings

for tracking in trackingInfo_reducido:
	position = {"geometry": {"type": "Point", "coordinates": [ tracking[1] , tracking[0] ]}, "type": "Feature", "properties":{"speed": tracking[2], "heading": tracking[3]}}
	array_list.append(position)

with open('./tracking_reducido_15min.json', 'w') as outfile:
	json.dump(array_list, outfile)

#!/usr/bin/env python
__author__ = "Tobias Bossert"
__copyright__ = "Copyright 2018, Fastpath.ch"
__license__ = "GPL"
__version__ = "1.0"
import web
import json
import minimalmodbus
import time


# RS485 Commands (just for refernce)
# 0x0100 Close
# 0x0200 Open
# 0x0300 Toggle
# 0x0400 Close ??
# 0x0500 Impulse
# 0x0600 Delay open (Seconds) 00 - FF -> (0x06[00-FF]) 

# Define USB to RS485 converter and bus-adress
instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 1)
# Define bitrate
instrument.serial.baudrate = 9600
counter = 0
time.sleep(1)

# Define URL's and map to classes
urls = (
	#/get/{channel}/{password}
    '/get/(.*)/(.*)', 'get_result',
	#/on/{channel}/{password}
    '/on/(.*)/(.*)', 'switch_on',
	#/off/{channel}/{password}
    '/off/(.*)/(.*)', 'switch_off',
	#/toggle/{channel}/{password}
    '/toggle/(.*)/(.*)', 'toggle',
	#/reset/{password}
    '/reset/(.*)','reset_all',
	#/all/{password}
    '/all/(.*)','on_all',
	#/getall/{password}
	'/getall/(.*)','getall',
	#/timed/{channel}/{delay}/{password}
    '/timed/(.*)/(.*)/(.*)','timed',
	#/shutdown/{password}
	'/shutdown/(.*)','shutdown'
    
)

authstring = str('test') # Password

app = web.application(urls, globals())

#Stop server
class shutdown:
	def GET(self,pw):
	#Check
		if pw == authstring:
			app.stop()
			
#Delayed open
class timed:
	def GET(self,id,timeout,pw):
	web.header('Access-Control-Allow-Origin', '*')
	web.header('Content-Type','application/json; charset=utf-8', unique=True) 
	#AUTH
	if pw == authstring:
		id = int(id)
		if (1 <= id <8):
			#convert int to hex
			command = 1536+int(timeout)
			#toggle
			try:
				instrument.write_register(id, command, numberOfDecimals=0, functioncode=6)
				data = {'channel':id, 'result':'ok','msg': 1, 'delay': timeout}
			except IOError as e:
				e = str(e)
				data = {'channel':id, 'result':'fail','msg':e}
		else:
			data = {'channel':id, 'result':'fail','msg':'invalid channel'}
	else:
		#wrong password
		data = {'result':'fail','msg':'auth failed'}
	return json.dumps(data)

#get status of channel
class get_result:
    def GET(self,id,pw):
	web.header('Access-Control-Allow-Origin', '*')
	web.header('Content-Type','application/json; charset=utf-8', unique=True) 
	# AUTH
	if pw == authstring: 
		id = int(id)
		# Check
		if (1 <= id <=8):
			#read status
			try:
				check = instrument.read_register(id, numberOfDecimals=0, functioncode=3)
				data = {'result':'ok', 'msg':check, 'channel':id}
			except IOError as e:
				e = str(e)
				data = {'channel':id, 'result':'fail','msg':e}
		else:
			#invalid channel
			data = {'channel':id, 'result':'fail','msg':'invalid channel'}
	else:
		#wrong password
		data = {'result':'fail','msg':'auth failed'}
	return json.dumps(data)

#reset all channels
class reset_all:        
    def GET(self,pw):
	web.header('Access-Control-Allow-Origin', '*')
	web.header('Content-Type','application/json; charset=utf-8', unique=True) 
	#AUTH
	if pw == authstring: 
		for i in range(1, 9):
			try:
				instrument.write_register(i, 0x0200, numberOfDecimals=0, functioncode=6)
				data = {'result':'ok'}
			except IOError as e:
				e = str(e)
				data = {'result':'fail','msg':e}
	else:
		#wrong password
		data = {'result':'fail','msg':'auth failed'}
	return json.dumps(data)

#get status of all channels
class getall:        
    def GET(self,pw):
	web.header('Access-Control-Allow-Origin', '*')
	web.header('Content-Type','application/json; charset=utf-8', unique=True) 
	#AUTH
	if pw == authstring: 
		data = {}
		for i in range(1, 9):
			try:
				channelname = i
				check = instrument.read_register(i, numberOfDecimals=0, functioncode=3)
				data.update({channelname:check})
				data.update({'result':'ok'})
			except IOError as e:
				e = str(e)
				data = {'result':'fail','msg':e}
	else:
		#wrong password
		data = {'result':'fail','msg':'auth failed'}
	return json.dumps(data)

#activate all channels
class on_all:        
    def GET(self,pw):
	web.header('Access-Control-Allow-Origin', '*')
	web.header('Content-Type','application/json; charset=utf-8', unique=True) 
	#AUTH
	if pw == authstring:
		#loop through channels
		for i in range(1, 9):
			try:
				instrument.write_register(i, 0x0100, numberOfDecimals=0, functioncode=6)
				check = instrument.read_register(i, numberOfDecimals=0, functioncode=3)
			except IOError as e:
				e = str(e)
				data = {'channel':id, 'result':'fail','msg':e}
			# check
			if check != 1:
				data = {'result':'fail','channel':i,'msg':'on failed'}
				break
			else:
				data = {'result':'ok'}
	else:
		#wrong password
		data = {'result':'fail','msg':'auth failed'}
	return json.dumps(data)

#toggle channel
class toggle:        
    def GET(self,id,pw):
	web.header('Access-Control-Allow-Origin', '*')
	web.header('Content-Type','application/json; charset=utf-8', unique=True) 
	#AUTH
	if pw == authstring:
		id = int(id)
		if (1 <= id <8):
			#Toggle
			try:
				instrument.write_register(id, 0x0300, numberOfDecimals=0, functioncode=6)
				check = instrument.read_register(id, numberOfDecimals=0, functioncode=3)
				data = {'channel':id, 'result':'ok','msg':check}
			except IOError as e:
				e = str(e)
				data = {'channel':id, 'result':'fail','msg':e}
		else:
			data = {'channel':id, 'result':'fail','msg':'invalid channel'}
	else:
		#wrong password
		data = {'result':'fail','msg':'auth failed'}
	return json.dumps(data)


#activate channel
class switch_on:        
    def GET(self,id,pw):
	web.header('Access-Control-Allow-Origin', '*')
	web.header('Content-Type','application/json; charset=utf-8', unique=True) 
	#AUTH
	if pw == authstring:
		id = int(id)
		if (1 <= id <8):
			#On
			try:
				instrument.write_register(id, 0x0100, numberOfDecimals=0, functioncode=6)
				data = {'channel':id, 'result':'ok','msg':1}
			except IOError as e:
				e = str(e)
				data = {'channel':id, 'result':'fail','msg':e}
		else:
			data = {'channel':id, 'result':'fail','msg':'invalid channel'}
	else:
		#wrong auth string
		data = {'result':'fail','msg':'auth failed'}
	return json.dumps(data)

#reset channel
class switch_off:        
    def GET(self,id,pw):
	web.header('Access-Control-Allow-Origin', '*')
	web.header('Content-Type','application/json; charset=utf-8', unique=True) 
	#AUTH
	if pw == authstring:
		id = int(id)
		if (1 <= id <8):
			#OFF
			try:
				instrument.write_register(id, 0x0200, numberOfDecimals=0, functioncode=6)
				data = {'channel':id, 'result':'ok','msg':0}
			except IOError as e:
				e = str(e)
				data = {'channel':id, 'result':'fail','msg':e}
		else:
			data = {'channel':id, 'result':'fail','msg':'invalid channel'}
	else:
		#wrong auth string
		data = {'result':'fail','msg':'auth failed'}
	return json.dumps(data)

if __name__ == "__main__":
    app.run()

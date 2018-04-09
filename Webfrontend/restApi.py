#!/usr/bin/env python
import web
import json
import minimalmodbus
import time

# Define Environment
 

# Befehle
# 0x0100 Schliessen
# 0x0200 Oeffnen
# 0x0300 Schritschalter
# 0x0400 Schliessen ?
# 0x0500 Taster
# 0x0600 Abfallverzoegert 00 - FF -> (0x06[00-FF])

# Definiere Busteilnehmer
instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 1)
# Definiere Baudrate
instrument.serial.baudrate = 9600
counter = 0
time.sleep(1)

# Definiere URLS
urls = (
    '/get/(.*)/(.*)', 'get_result',
    '/on/(.*)/(.*)', 'switch_on',
    '/off/(.*)/(.*)', 'switch_off',
    '/toggle/(.*)/(.*)', 'toggle',
    '/reset/(.*)','reset_all',
    '/all/(.*)','on_all',
	'/getall/(.*)','getall',
	'/shutdown/(.*)','shutdown'
    
)

authstring = str('test') # Passwort

app = web.application(urls, globals())

class shutdown:
	def GET(self,pw):
	#Check
		if pw == authstring:
			app.stop()
	

class get_result:        
    def GET(self,id,pw):
	web.header('Access-Control-Allow-Origin', '*')
	web.header('Content-Type','application/json; charset=utf-8', unique=True) 
	# AUTH
	if pw == authstring: 
		id = int(id)
		# Check
		if (1 <= id <=8):
			#Lese result
			try:
				check = instrument.read_register(id, numberOfDecimals=0, functioncode=3)
				data = {'result':'ok', 'msg':check, 'channel':id}
			except IOError as e:
				e = str(e)
				data = {'channel':id, 'result':'fail','msg':e}
		else:
			# Ungluetiger Channel
			data = {'channel':id, 'result':'fail','msg':'invalid channel'}
	else:
		# Falscher auth string
		data = {'result':'fail','msg':'auth failed'}
	return json.dumps(data)

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
		# Falscher auth string
		data = {'result':'fail','msg':'auth failed'}
	return json.dumps(data)

	
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
		# Falscher auth string
		data = {'result':'fail','msg':'auth failed'}
	return json.dumps(data)

class on_all:        
    def GET(self,pw):
	web.header('Access-Control-Allow-Origin', '*')
	web.header('Content-Type','application/json; charset=utf-8', unique=True) 
	#AUTH
	if pw == authstring:
		for i in range(1, 9):
			try:
				instrument.write_register(i, 0x0100, numberOfDecimals=0, functioncode=6)
				check = instrument.read_register(i, numberOfDecimals=0, functioncode=3)
			except IOError as e:
				e = str(e)
				data = {'channel':id, 'result':'fail','msg':e}
			# Pruefe ob ok
			if check != 1:
				data = {'result':'fail','channel':i,'msg':'on failed'}
				break
			else:
				data = {'result':'ok'}
	else:
		# Falscher auth string
		data = {'result':'fail','msg':'auth failed'}
	return json.dumps(data)

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
		# Falscher auth string
		data = {'result':'fail','msg':'auth failed'}
	return json.dumps(data)


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
		# Falscher auth string
		data = {'result':'fail','msg':'auth failed'}
	return json.dumps(data)

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
		# Falscher auth string
		data = {'result':'fail','msg':'auth failed'}
	return json.dumps(data)

if __name__ == "__main__":
    app.run()
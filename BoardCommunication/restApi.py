#!/usr/bin/env python
__author__ = "Tobias Bossert"
__copyright__ = "Copyright 2018, Fastpath.ch"
__license__ = "GPL"
__version__ = "1.0"
import web
import json
import minimalmodbus
import time

MIN_CHANNEL_ID = 1
MAX_CHANNLE_ID = 8

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
    # /get/{channel}/{password}
    '/get/(.*)/(.*)', 'GetResult',
    # /on/{channel}/{password}
    '/on/(\d{1})/(.*)', 'SwitchOn',
    # /off/{channel}/{password}
    '/off/(\d{1})/(.*)', 'SwitchOff',
    # /toggle/{channel}/{password}
    '/toggle/(\d{1})/(.*)', 'Toggle',
    # /reset/{password}
    '/reset/(.*)', 'ResetAll',
    # /all/{password}
    '/all/(.*)', 'OnAll',
    # /getall/{password}
    '/getall/(.*)', 'GetAll',
    # /timed/{channel}/{delay}/{password}
    '/timed/(\d{1})/(\d{1,3})/(.*)', 'Timed',
    # /shutdown/{password}
    '/shutdown/(.*)', 'Shutdown'

)

authstring = str('test')  # Password

app = web.application(urls, globals())


# Stop server
class Shutdown:
    def GET(self, pw):
        # Check
        if pw == authstring:
            app.stop()


# Delayed open
class Timed:
    def GET(self, channel, timeout, pw):
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Content-Type', 'application/json; charset=utf-8', unique=True)
        # AUTH
        if pw == authstring:
            channel_id = int(channel)
            timeout = int(timeout)
            if MIN_CHANNEL_ID <= channel_id < MAX_CHANNLE_ID:
                if 1 <= timeout < 255:
                    # convert int to hex
                    command = 1536 + timeout
                    # toggle
                    try:
                        instrument.write_register(channel_id, command, numberOfDecimals=0, functioncode=6)
                        data = {'channel': channel_id, 'result': 'ok', 'msg': 1, 'delay': timeout}
                    except IOError as e:
                        e = str(e)
                        data = {'channel': channel_id, 'result': 'fail', 'msg': e}
                else:
                    data = {'channel': channel_id, 'result': 'fail',
                            'msg': 'invalid timeout value must be between 1 and 255 seconds'}
            else:
                data = {'channel': channel_id, 'result': 'fail', 'msg': 'invalid channel'}
        else:
            # wrong password
            data = {'result': 'fail', 'msg': 'auth failed'}
        return json.dumps(data)


# get status of channel
class GetResult:
    def GET(self, id, pw):
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Content-Type', 'application/json; charset=utf-8', unique=True)
        # AUTH
        if pw == authstring:
            id = int(id)
            # Check
            if MIN_CHANNEL_ID <= id <= MAX_CHANNLE_ID:
                # read status
                try:
                    check = instrument.read_register(id, numberOfDecimals=0, functioncode=3)
                    data = {'result': 'ok', 'msg': check, 'channel': id}
                except IOError as e:
                    e = str(e)
                    data = {'channel': id, 'result': 'fail', 'msg': e}
            else:
                # invalid channel
                data = {'channel': id, 'result': 'fail', 'msg': 'invalid channel'}
        else:
            # wrong password
            data = {'result': 'fail', 'msg': 'auth failed'}
        return json.dumps(data)


# reset all channels
class ResetAll:
    def GET(self, pw):
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Content-Type', 'application/json; charset=utf-8', unique=True)
        # AUTH
        if pw == authstring:
            data = {}
            for i in range(MIN_CHANNEL_ID, MAX_CHANNLE_ID + 1):
                try:
                    instrument.write_register(i, 0x0200, numberOfDecimals=0, functioncode=6)
                    data = {'result': 'ok'}
                except IOError as e:
                    e = str(e)
                    data = {'result': 'fail', 'msg': e}
        else:
            # wrong password
            data = {'result': 'fail', 'msg': 'auth failed'}
        return json.dumps(data)


# get status of all channels
class GetAll:
    def GET(self, pw):
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Content-Type', 'application/json; charset=utf-8', unique=True)
        # AUTH
        if pw == authstring:
            data = {}
            for i in range(MIN_CHANNEL_ID, MAX_CHANNLE_ID + 1):
                try:
                    check = instrument.read_register(i, numberOfDecimals=0, functioncode=3)
                    data.update({i: check})
                    data.update({'result': 'ok'})
                except IOError as e:
                    e = str(e)
                    data = {'result': 'fail', 'msg': e}
        else:
            # wrong password
            data = {'result': 'fail', 'msg': 'auth failed'}
        return json.dumps(data)


# activate all channels
class OnAll:
    def GET(self, pw):
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Content-Type', 'application/json; charset=utf-8', unique=True)
        # AUTH
        if pw == authstring:
            data = {}
            # loop through channels
            for i in range(MIN_CHANNEL_ID, MAX_CHANNLE_ID + 1):
                try:
                    instrument.write_register(i, 0x0100, numberOfDecimals=0, functioncode=6)
                    check = instrument.read_register(i, numberOfDecimals=0, functioncode=3)
                except IOError as e:
                    e = str(e)
                    data = {'channel': i, 'result': 'fail', 'msg': e}
                    break
                # check
                if check != 1:
                    data = {'result': 'fail', 'channel': i, 'msg': 'on failed'}
                    break
                else:
                    data = {'result': 'ok'}
        else:
            # wrong password
            data = {'result': 'fail', 'msg': 'auth failed'}
        return json.dumps(data)


# toggle channel
class Toggle:
    def GET(self, channel, pw):
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Content-Type', 'application/json; charset=utf-8', unique=True)
        # AUTH
        if pw == authstring:
            channel_id = int(channel)
            if MIN_CHANNEL_ID <= channel_id < MAX_CHANNLE_ID:
                # Toggle
                try:
                    instrument.write_register(channel_id, 0x0300, numberOfDecimals=0, functioncode=6)
                    check = instrument.read_register(channel_id, numberOfDecimals=0, functioncode=3)
                    data = {'channel': channel_id, 'result': 'ok', 'msg': check}
                except IOError as e:
                    e = str(e)
                    data = {'channel': channel_id, 'result': 'fail', 'msg': e}
            else:
                data = {'channel': channel_id, 'result': 'fail', 'msg': 'invalid channel'}
        else:
            # wrong password
            data = {'result': 'fail', 'msg': 'auth failed'}
        return json.dumps(data)


# activate channel
class SwitchOn:
    def GET(self, channel, pw):
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Content-Type', 'application/json; charset=utf-8', unique=True)
        # AUTH
        if pw == authstring:
            channel_id = int(channel)
            if MIN_CHANNEL_ID <= channel_id < MAX_CHANNLE_ID:
                # On
                try:
                    instrument.write_register(channel_id, 0x0100, numberOfDecimals=0, functioncode=6)
                    data = {'channel': channel_id, 'result': 'ok', 'msg': 1}
                except IOError as e:
                    e = str(e)
                    data = {'channel': channel_id, 'result': 'fail', 'msg': e}
            else:
                data = {'channel': channel_id, 'result': 'fail', 'msg': 'invalid channel'}
        else:
            # wrong auth string
            data = {'result': 'fail', 'msg': 'auth failed'}
        return json.dumps(data)


# reset channel
class SwitchOff:
    def GET(self, id, pw):
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Content-Type', 'application/json; charset=utf-8', unique=True)
        # AUTH
        if pw == authstring:
            id = int(id)
            if MIN_CHANNEL_ID <= id < MAX_CHANNLE_ID:
                # OFF
                try:
                    instrument.write_register(id, 0x0200, numberOfDecimals=0, functioncode=6)
                    data = {'channel': id, 'result': 'ok', 'msg': 0}
                except IOError as e:
                    e = str(e)
                    data = {'channel': id, 'result': 'fail', 'msg': e}
            else:
                data = {'channel': id, 'result': 'fail', 'msg': 'invalid channel'}
        else:
            # wrong auth string
            data = {'result': 'fail', 'msg': 'auth failed'}
        return json.dumps(data)


if __name__ == "__main__":
    from Logging import Log
    app.run(Log)

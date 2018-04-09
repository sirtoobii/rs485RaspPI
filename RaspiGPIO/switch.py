#!/usr/bin/env/python
__author__ = "Tobias Bossert"
__copyright__ = "Copyright 2018, Fastpath.ch"
__license__ = "GPL"
__version__ = "1.0"
import RPi.GPIO as GPIO
import time
import urllib2


# Controller
ip = '192.168.2.214:8080'
pw = 'test'


# Define GPIO Input channels (map buttons to GPIO-Pins)
buttons = {'btn1':40,'btn2':38,'btn3':36,'btn4':32}
# Define Rs485 channels (map buttons to RS485 channels)
rs485 = {'btn1':1,'btn2':3,'btn3':4,'btn4':2}
# Init status array
status = {1:False,2:False,3:False,4:False}
# Sleep timer
rest = 0.5 #if action
rest2 = 0.1 #if no action
#counter
count = 1

# Define Pin count
GPIO.setmode(GPIO.BOARD)
# Setup Pins
GPIO.setup(buttons['btn1'], GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(buttons['btn2'], GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(buttons['btn3'], GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(buttons['btn4'], GPIO.IN, pull_up_down = GPIO.PUD_UP)

# Check status on starts
for btn in buttons:
	if(GPIO.input(buttons[btn])):
		status[count] = True
		time.sleep(rest)
	count = count +1

# Reset counter
count = 1

# Programm loop
try:
	while True:
		count = 1
		for btn in buttons:
			#check if status has changed. I used this "dirty" method because the add_event_detect() was not reliable because the cabels shared the same paths as the mains.
			#maybe this is solved by adding a capacitor....
			if(GPIO.input(buttons[btn])!= status[count]):
				status[count] = GPIO.input(buttons[btn])
				try:
					urllib2.urlopen("http://"+ip+"/toggle/"+str(rs485[btn])+"/"+pw,timeout = 1)
				except urllib2.URLError as e:
					print(e)
				time.sleep(rest)
			else:
				time.sleep(rest2)
			count = count +1
except KeyboardInterrupt:
	GPIO.cleanup()
	print "\nBye"
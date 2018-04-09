# RaspberryPI RS485 Controller
##### 8CH 12V Modbus RTU RS485 Relay

I just wanted to share my simple RS485 controller. This repo contains the following parts:

| Folder | Description |
| ------ | ------ |
| BoardCommunication | A python script the creates a simple REST-based interface with json responses |
| RaspiGPIO | A python script that integrates commands via GPIO-Pins (relays on BoardCommunication script) |
| Webfrontend | A very simple webfrontend (relays on BoardCommunication script) |

## usage
```sh
$ cd BoardCommunication
$ python restApi.py
```
Server listens now on
```sh
127.0.0.1:8080
```
Example request to switch on channel 2
```sh
127.0.0.1:8080/on/2/{password}
```
Returns:
```sh
{'channel':2, 'result':'ok','msg':1} #success
{'channel':2, 'result':'fail','msg':'error_message'} #failure
```
For specific the configurations please refer the comments in the scripts

## Used Hardware
- 8CH 12V Modbus RTU RS485 Relay ([ebay-Link](https://www.ebay.de/itm/8CH-12V-Modbus-RTU-RS485-Relay-Module-Switch-Relais-Board-for-PLC-Lamp-LED-PTZ-/272462513278))
- RaspberryPI Model 3 with debian
- USB - RS485 Konverter ([ebay-Link](https://www.ebay.de/itm/USB-RS485-Konverter-/111326580742))

### Warning
This scripts are **not** secure! I highly recommend to use them only controlled environments. This is especially true for the web-interface.

### License
MIT
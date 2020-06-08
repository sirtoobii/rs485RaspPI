#!/bin/bash

echo Please enter the username on which this service should run:
read USERNAME
PWD=$(pwd)
echo creating python virtual env...
python3 -m venv venv
echo installing python requirements
$PWD/venv/bin/pip install -r requirements.txt
echo install service
sed -i "s|%USER%|$USERNAME|g" rs485.service
sed -i "s|%EXECPATH%|$PWD/venv/bin/python|g" rs485.service
sed -i "s|%COMMAND%|$PWD/BoardCommunication/restApi.py|g" rs485.service

sudo cp rs485.service /etc/systemd/system/
sudo systemctl daemon-reload

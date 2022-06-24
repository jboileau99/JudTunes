#!/bin/sh

cd /root/JudTunes/src

if [ $1 == 'prod' ]
then
while true; do
	/usr/bin/python3 JudTunes.py prod
done &
else
  /usr/bin/python3 JudTunes.py dev
fi
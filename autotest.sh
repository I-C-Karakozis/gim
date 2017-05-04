#!/bin/bash

rm ftp/videos/* &> /dev/null
rm ftp/videos/hof/* &> /dev/null

python ftp/ftpserver.py &> /dev/null &
FTP_PID=$!

CSRF_KEY=$(head -c 16 /dev/urandom)
SECRET_KEY=$(head -c 16 /dev/urandom)

PURVIEW_CSRF_SESSION_KEY=$CSRF_KEY PURVIEW_SECRET_KEY=$SECRET_KEY python -m unittest discover tests

kill -KILL $FTP_PID &> /dev/null

rm ftp/videos/* &> /dev/null
rm ftp/videos/hof/* &> /dev/null

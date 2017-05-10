#!/bin/bash

if [ $# -eq 0 ]
then TEST_DIR="tests"
else TEST_DIR=$1
fi

python ftp/ftpserver.py &> /dev/null &
FTP_PID=$!

MYSQL_URI=''
CSRF_KEY=$(head -c 16 /dev/urandom)
SECRET_KEY=$(head -c 16 /dev/urandom)

PURVIEW_MYSQL_URI=$MYSQL_URI PURVIEW_CSRF_SESSION_KEY=$CSRF_KEY PURVIEW_SECRET_KEY=$SECRET_KEY python -m unittest discover $TEST_DIR

disown $FTP_PID
kill -KILL $FTP_PID &> /dev/null

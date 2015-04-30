#!/bin/sh
if [ ! -f $1 ]
  then
    echo "Could not find pidfile, assuming process does not exist."
    exit 0
fi
pid=`cat $1`
if [ "${pid}" -a "`ps -ef | grep $pid | grep -v \"grep\" | awk '{print $2}'`" ]
  then
    kill -15 ${pid}
    echo "Found and killed old process."
  else
    echo "Old process did not exist."
fi

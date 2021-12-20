#!bin/bash

while [ 1 ]
	do
		pid=`ps -ef | grep "gala" | grep -v 'grep' | awk '{print $2}'`

		if [ -z $pid ];then
			systemctl restart gala-node.service
		fi
		sleep 30
	done

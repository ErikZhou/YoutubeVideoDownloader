#!/bin/bash
#先载入环境变量
source /etc/profile
source /root/.bashrc
PATH=/usr/local/bin:$PATH


processcount=$(pgrep scd.py|wc -l)
cd $(cd $(dirname $0) && pwd)
if [[ 0 -eq $processcount ]]
then
        echo "[ $(date) ] : scd.py is down, start it!" | tee -ai ./scd.log
        #bash ./start.sh #这里是项目的重启脚本
        #/usr/local/bin/scrapy
        cd /home/rslsync/vps/YD/YD && scrapy crawl download -a target=""
else
        echo scd.py is OK!
fi

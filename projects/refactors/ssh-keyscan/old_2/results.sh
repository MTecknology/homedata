#!/bin/bash
# This is the tool to use to put the report file in a homedir for the collector
# Set this up in Cron to automate nightly reports
# Change the GeoIP and homedir to customize

GEO="LOC" #Change to GEO code of host.
PUTDIR="/home/Username" # Change the homedir to write to
OWNER="Username"

cd /opt/scandir/
echo $GEO > ${PUTDIR}/report.txt
echo "finished count" >> ${PUTDIR}/report.txt
fgrep ": done" homes.yml | wc -l >> ${PUTDIR}/report.txt
echo "total homedirs" >> ${PUTDIR}/report.txt
cat /etc/auto.scanhomes | wc -l >> ${PUTDIR}/report.txt
echo "keys found" >> ${PUTDIR}/report.txt
fgrep INFO results.txt | grep -v Start | grep -v Yaml | wc -l >> ${PUTDIR}/report.txt
chown ${OWNER} ${PUTDIR}/report.txt
fgrep INFO results.txt | grep -v Start | grep -v Yaml > ${PUTDIR}/results.txt
chown ${OWNER} ${PUTDIR}/results.txt

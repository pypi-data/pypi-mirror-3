#!/bin/sh                                                                       
cd && wget http://updates.jenkins-ci.org/download/war/latest/jenkins.war
/etc/init.d/jenkins stop
cd /usr/share/jenkins
mv jenkins.war jenkins.war.backup
mv ~/jenkins.war .
chmod 644 jenkins.war
/etc/init.d/jenkins start

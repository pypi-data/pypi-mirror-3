echo "deb http://pkg.jenkins-ci.org/debian binary/" >> /etc/apt/sources.list.d/jenkins.list
wget -q -O - http://pkg.jenkins-ci.org/debian/jenkins-ci.org.key | apt-key add -
apt-get update
apt-get install -y jenkins
#echo 'JENKINS_ARGS=$JENKINS_ARGS" --prefix=/jenkins --httpListenAddress=localhost"' >> /etc/default/jenkins
#/etc/init.d/jenkins restart

apt-get install -y build-essential

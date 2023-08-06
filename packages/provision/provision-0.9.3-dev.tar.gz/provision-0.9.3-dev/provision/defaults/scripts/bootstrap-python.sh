#!/bin/bash
# This script is for bootstrapping python on a new ubuntu node.
# It installs the python-dev apt package (needed to build pycrypto),
# setuptools, and virtualenv.

echo "Starting python bootstrap"

PY_VERSION=`python -c "import sys; print '%d.%d' % (sys.version_info[0], sys.version_info[1])"`

DOWNLOAD_DIR=~/python_bootstrap
mkdir -p $DOWNLOAD_DIR
echo "Will download files to $DOWNLOAD_DIR"

download_file() {
  echo wget -q -O $DOWNLOAD_DIR/$1 $2
  wget -q -O $DOWNLOAD_DIR/$1 $2
  http_rc=$?
  if [[ "$http_rc" != "0" ]]; then
    echo "Download of $1 failed, return code was $http_rc"
    exit 1
  fi
  if [ ! -f $DOWNLOAD_DIR/$1 ]; then
    echo "Downloaded file $1 not found"
    exit 1
  fi
}

echo apt-get install -y python-dev
apt-get install -y python-dev
if [[ "$?" != "0" ]]; then
  echo "Unable to install apt package python-dev"
  exit 1
fi

if [[ "$PY_VERSION" == "2.6" ]]; then
  download_file setuptools-0.6c11-py2.6.egg "http://pypi.python.org/packages/2.6/s/setuptools/setuptools-0.6c11-py2.6.egg#md5=bfa92100bd772d5a213eedd356d64086"
  echo sh -x $DOWNLOAD_DIR/setuptools-0.6c11-py2.6.egg
  sh -x $DOWNLOAD_DIR/setuptools-0.6c11-py2.6.egg
  setup_rc=$?
  if [[ "$setup_rc" != "0" ]]; then
    echo "problem in install of setuptools, rc was $setup_rc"
    exit 1
  fi
else
  if [[ "$PY_VERSION" == "2.7" ]]; then
    download_file setuptools-0.6c11-py2.7.egg "http://pypi.python.org/packages/2.7/s/setuptools/setuptools-0.6c11-py2.7.egg#md5=fe1f997bc722265116870bc7919059ea"
    echo sh -x $DOWNLOAD_DIR/setuptools-0.6c11-py2.7.egg
    sh -x $DOWNLOAD_DIR/setuptools-0.6c11-py2.7.egg
    setup_rc=$?
    if [[ "$setup_rc" != "0" ]]; then
      echo "problem in install of setuptools, rc was $setup_rc"
      exit 1
    fi
  else
    echo "Unsupport python version $PY_VERSION"
    exit 1
  fi
fi

download_file virtualenv-1.7.tar.gz http://pypi.python.org/packages/source/v/virtualenv/virtualenv-1.7.tar.gz#md5=dcc105e5a3907a9dcaa978f813a4f526
echo easy_install $DOWNLOAD_DIR/virtualenv-1.7.tar.gz
easy_install $DOWNLOAD_DIR/virtualenv-1.7.tar.gz
if [[ "$?" != "0" ]]; then
  echo "problem in install of virtualenv"
  exit 1
fi

#echo easy_install pycrypto
#easy_install pycrypto
#if [[ "$?" != "0" ]]; then
#  echo "Problem in pycrypto install"
#  exit 1
#fi
echo "Downloading pycrypto"
download_file pycrypto-2.4.tar.gz http://ftp.dlitz.net/pub/dlitz/crypto/pycrypto/pycrypto-2.4.tar.gz
cd $DOWNLOAD_DIR
tar xvzf pycrypto-2.4.tar.gz
cd pycrypto-2.4
echo "Installing pycrypto"
echo python setup.py install
python setup.py install
if [[ "$?" != "0" ]]; then
  echo "problem in install of pycrtypo"
  exit 1
fi

echo "Python bootstrap successful"
exit 0

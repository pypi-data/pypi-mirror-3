# Parts borrowed extensively from devstack's stack.sh

# Destination path for installation ``DEST``
DEST=${DEST:-/opt/stack}

# OpenStack is designed to be run as a regular user (Horizon will fail to run
# as root, since apache refused to startup serve content from root user).  If
# stack.sh is run as root, it automatically creates a stack user with
# sudo privileges and runs as that user.

# since this script runs as a normal user, we need to give that user
# ability to run sudo
dpkg -l sudo || apt_get update && apt_get install sudo

if ! getent passwd stack >/dev/null; then
    echo "Creating a user called stack"
    useradd -U -G sudo -s /bin/bash -d $DEST -m stack
fi

echo "Giving stack user passwordless sudo priviledges"
# some uec images sudoers does not have a '#includedir'. add one.
grep -q "^#includedir.*/etc/sudoers.d" /etc/sudoers ||
    echo "#includedir /etc/sudoers.d" >> /etc/sudoers
( umask 226 && echo "stack ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/50_stack_sh )

echo "Giving stack user same .ssh/authorized_keys file as root"
su stack -c 'mkdir -p ~stack/.ssh'
cp ~/.ssh/authorized_keys ~stack/.ssh
chown stack:stack ~stack/.ssh/authorized_keys

echo "Generating rsa keypair if necessary"
[ -r ~/.ssh/id_rsa ] || ssh-keygen -b 4096 -t rsa -f ~/.ssh/id_rsa -P ""

apt-get -y install git

echo "Cloning devstack repository"
sudo -u stack -i sh -c "git clone https://github.com/openstack-dev/devstack.git"

echo "Switching to stable/essex branch"
sudo -u stack -i sh -c "cd devstack && git fetch origin && git checkout stable/essex"

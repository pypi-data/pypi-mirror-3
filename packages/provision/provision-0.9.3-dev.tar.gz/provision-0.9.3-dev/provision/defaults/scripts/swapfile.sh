# http://serverfault.com/questions/218750/why-ec2-ubuntu-images-dont-have-swap
dd if=/dev/zero of=/var/swapfile bs=1M count=2048 && \
chmod 600 /var/swapfile && \
mkswap /var/swapfile && \
echo /var/swapfile none swap defaults 0 0 | sudo tee -a /etc/fstab && \
swapon -a

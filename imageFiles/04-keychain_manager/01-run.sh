#!/bin/bash -e

install -m 755 files/keychainbackup-0.3.deb "${ROOTFS_DIR}"

on_chroot << EOF
sudo pip3 install adafruit-circuitpython-rgb-display numpy gpiod gpiodevice --break-system-packages && sudo dpkg --install /keychainbackup-0.3.deb && rm -rf /keychainbackup-0.3.deb 
EOF

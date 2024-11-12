#!/bin/bash -e

# Enable SSH, SPI, I2C and Auto Login via Console on Boot
echo 'Enabling SSH, SPI, I2C and Auto Login via Console on Boot'
on_chroot << EOF
  SUDO_USER="${FIRST_USER_NAME}" raspi-config nonint do_ssh 0
  SUDO_USER="${FIRST_USER_NAME}" raspi-config nonint do_spi 0
  SUDO_USER="${FIRST_USER_NAME}" raspi-config nonint do_i2c 0
  SUDO_USER="${FIRST_USER_NAME}" raspi-config nonint do_boot_behaviour B2
EOF

# Copy wpa_supplicant.conf to /etc/wpa_supplicant
echo 'Copying wpa_supplicant.conf'
install -v -d                               "${ROOTFS_DIR}/etc/wpa_supplicant"
install -v -m 600 files/wpa_supplicant.conf "${ROOTFS_DIR}/etc/wpa_supplicant/"

#!/bin/bash

sudo apt-get install --no-install-recommends git
cd ~
git clone https://github.com/ajtudela/StargateProject-software.git sg1_v4
sudo chmod u+x /home/pi/sg1_v4/install/*.sh
cd /home/pi/sg1_v4/install && ./install.sh

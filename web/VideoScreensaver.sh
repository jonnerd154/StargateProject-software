#!/bin/bash

# https://www.raspberrypi.org/forums/viewtopic.php?t=167789

process() {
while read input; do 
  case "$input" in
    UNBLANK*)	killall omxplayer.bin ;; # This will kill the process of player
    BLANK*)	omxplayer --loop --no-osd --no-keys /home/pi/stargate/web/SGCSpinningLogoAnimation.mp4 & ;; # dont forget the & on the end or it will never stops, just add your movie file path
  esac
done
}

xscreensaver-command -watch | process
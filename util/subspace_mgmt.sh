#!/bin/bash

# TODO: MacOS compatibility for testing

if [ -z "$1" ]
then
 echo "USAGE: subspace_mgmt.sh [ up | down ]"
 exit 1
elif [[ $1 eq "up" ]]; then
  sudo wg-quick up subspace
elif [[ $1 eq "down" ]]; then
  sudo wg-quick down subspace
else
  echo "USAGE: subspace_mgmt.sh [ up | down ]"
  exit 1

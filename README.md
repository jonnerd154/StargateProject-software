# [TheStargateProject.com](https://TheStargateProject.com)
Software for Kristian's Fully Functional 3D Printed Stargate

## Setup Instructions:
It is _highly_ recommended to build your gate by using the pre-built Disk Image (ISO) provided by Kristian.
 - If you are **upgrading an existing gate** read this first: [UPGRADING_FROM_V3.X.md](UPGRADING_FROM_V3.X.md)
 - EXPRESS SETUP process can be found in [EXPRESS_SETUP.md](EXPRESS_SETUP.md)
 - A manual setup guide can be found in [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md)

## Default SSH/SCP credentials
```
Username: pi
Password: sg1
```

## Start/Stop/Restart the Stargate Software manually
The Stargate Software will automatically start when the Raspi boots. It runs as a systemd daemon called `stargate.service`. If you want to manually start/stop/restart it, you can use these commands:
```
sudo systemctl start stargate.service
sudo systemctl stop stargate.service
sudo systemctl restart stargate.service
```

## Web interface
A web interface is provided to allow testing of individual hardware components, dialing, address book, and much more. Find it here:

[http://stargate.local](http://stargate.local)

## Web API
There is a JSON API to interact with the Stargate via a web service. This enables anyone to build software that can control the Stargate. We'd love to see someone build a Stargate Command computer-style controller, or a RPG game that interfaces with the 'Gate. Your imagination is the limit!

The documentation can be found in the repo, or at one of the below links

- v1.0.0 (Current): https://app.swaggerhub.com/apis-docs/TheStargateProject/StargateWebAPI/1.0.0#/
- v1.1.0 (In development): https://app.swaggerhub.com/apis-docs/TheStargateProject/StargateWebAPI/1.1.0

## Credits
- Kristian Tysse designed and wrote all of the original code, most of which is still in use today's program.
- Jonathan Moyes restructured the code and extended it to include additional functionalities.
- The Web UI and basic implementation of the Stargate API Server were based on Dan Clarke's work: https://github.com/danclarke/WorkingStargateMk2Raspi

Stargate SG-1, Stargate Atlantis & Stargate Universe are ™ & © of Metro-Goldwyn-Mayer Studios Inc.  This project is in no way sponsored or endorsed by: SyFy or MGM. This project was created solely as a hobby project and to help other Stargate fans create their own Stargates and to keep the passion and love for Stargate alive.

TheStargateProject.com is a fan-based project and is not intended to infringe upon any copyrights or registered trademarks.

# Development
## Running PyLint
 - To run for StargateMilkyWay: `pylint --rcfile=.pylintrc-milkyway ./*`
 - To run for StargatePegasus:  `pylint --rcfile=.pylintrc-pegasus ./*`

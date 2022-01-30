import pwd
import sys
import subprocess

from os import stat, makedirs, path, chown, execl
from ast import literal_eval
from pathlib import Path
from datetime import datetime
import requests
from packaging import version

from network_tools import NetworkTools
from database import Database
from version import VERSION as current_version

class SoftwareUpdate:

    def __init__(self, app):

        self.current_version = current_version
        self.log = app.log
        self.cfg = app.cfg
        self.audio = app.audio

        self.database = Database(app.base_path)

        # Retrieve the configurations
        self.base_url = self.cfg.get("software_updates_url")
        self.file_download_username = self.cfg.get("software_updates_username")
        self.file_download_password = self.cfg.get("software_updates_password")

        # Update the fan gates from the DB every x hours
        interval = self.cfg.get("software_update_interval")
        app.schedule.every(interval).hours.do( self.check_and_install )

    def get_current_version(self):
        return self.current_version

    def check_and_install(self):
        """
        This functions tries to update the stargate program with new files listed in the database
        main.py must always be updated due to the version variable change in the file.
        The owner and group of the files is set to match the same as the current __file__ variable.
        If the requirements.txt file is updated the missing modules will be installed.
        :return: Nothing is returned.
        """

        try:
            self.log.log('Checking for software updates.')

            ## Verify that we have an internet connection, if not, return false.
            if not NetworkTools(self.log).has_internet_access():
                self.log.log('No internet connection available. Aborting Software Update.')
                return

            ## Some needed variables
            update_found = False
            root_path = Path(__file__).parent.absolute()

            # get the user ID and group ID of the owner of this file (__file__). (In most instances this would result in the UID 1001 for the sg1 user.
            uid = pwd.getpwuid(stat(__file__).st_uid).pw_name
            gid = pwd.getpwuid(stat(__file__).st_uid).pw_gid

            ### Get the information from the DB ###
            sw_update = self.database.get_software_updates()

            ## check the db information for a new update
            for entry in sw_update:

                ## if there is a newer version:
                if version.parse(str(self.current_version)) < version.parse(str(entry[1])):
                    update_audio = self.audio.play_random_audio_clip("update")
                    update_found = True
                    self.log.log(f"Newer version {entry[1]} detected!")
                    self.cfg.set('software_update_status', f'Update Available: v{entry[1]}')
                    new_files = literal_eval(entry[2]) # make a list of the new files
                    # Get the new files
                    for file in new_files:
                        req = requests.get(self.base_url + str(entry[1]) + '/' + file, auth=( self.file_download_username, self.file_download_password )) # get the file
                        filepath = Path.joinpath(root_path, file) # the path of the new file
                        try:
                            makedirs(path.dirname(filepath)) # create directories if they do not exist:
                        except OSError:
                            pass

                        with open(filepath, 'wb') as file:
                            file.write(req.content) # save the file

                        chown(str(root_path / file), uid, gid) # Set correct owner and group for the file
                        self.log.log(f"{file} is updated!")

                        #If requirements.txt is new, run install of requirements.
                        if file == 'requirements.txt':
                            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", Path.joinpath(root_path, 'requirements.txt')])
                    # Don't cut the update audio short the update
                    if update_audio.is_playing():
                        update_audio.wait_done()

                    # Install the update and restart.
                    self.log.log('Update installed -> restarting the program')
                    execl(sys.executable, *([sys.executable] + sys.argv))  # Restart the program

            if not update_found:
                self.log.log("The Stargate is up-to-date.")
                self.cfg.set('software_update_last_check', str(datetime.now() ) )
                self.cfg.set('software_update_status', 'up-to-date' )
                self.cfg.set('software_update_exception', False )

        except Exception as ex: # pylint: disable=broad-except
            self.log.log(f"Software update failed with error: {ex}")
            self.cfg.set('software_update_last_check', str(datetime.now()))
            # Flag the problem in update_exception, not update_status so that update_status can show that an update is available.
            self.cfg.set('software_update_exception', True)

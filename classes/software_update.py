import pymysql, requests, pwd, grp, sys, subprocess
from os import stat, makedirs, path
from base64 import b64decode
from ast import literal_eval
from pathlib import Path
from datetime import datetime

from network_tools import NetworkTools
from database import Database

class SoftwareUpdate:

    def __init__(self, app):

        from version import version as current_version # TODO: move to a json file
        self.current_version = current_version
        self.log = app.log
        self.cfg = app.cfg
        self.audio = app.audio

        self.database = Database(app.base_path)

        # Retrieve the configurations
        self.base_url = self.cfg.get("software_updates_url")
        self.fileDownloadUsername = self.cfg.get("software_updates_username")
        self.fileDownloadPassword = self.cfg.get("software_updates_password")

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
            if ( not NetworkTools(self.log).has_internet_access()):
                self.log.log('No internet connection available. Aborting Software Update.')
                return False

            ## Some needed variables
            update_found = False
            root_path = Path(__file__).parent.absolute()

            # get the user ID and group ID of the owner of this file (__file__). (In most instances this would result in the UID 1001 for the sg1 user.
            uid = pwd.getpwnam(pwd.getpwuid(stat(__file__).st_uid).pw_name).pw_uid
            gid = grp.getgrnam(pwd.getpwuid(stat(__file__).st_uid).pw_name).gr_gid

            ### Get the information from the DB ###
            sw_update = self.database.get_software_updates()

            ## check the db information for a new update
            for entry in sw_update:

                ## if there is a newer version:
                if entry[1] > self.current_version:
                    update_audio = self.audio.play_random_audio_clip("update")
                    update_found = True
                    self.log.log("Newer version {} detected!".format(entry[1]))
                    self.cfg.set('software_update_status', 'Update Available: v{}'.format(entry[1]) )
                    new_files = literal_eval(entry[2]) # make a list of the new files
                    # Get the new files
                    for file in new_files:
                        r = requests.get(self.base_url + str(entry[1]) + '/' + file, auth=( self.fileDownloadUsername, self.fileDownloadPassword )) # get the file
                        filepath = Path.joinpath(root_path, file) # the path of the new file
                        try:
                            makedirs(path.dirname(filepath)) # create directories if they do not exist:
                        except:
                            pass
                        open(filepath, 'wb').write(r.content) # save the file
                        os.chown(str(root_path / file), uid, gid) # Set correct owner and group for the file
                        self.log.log("{} is updated!".format(file))

                        #If requirements.txt is new, run install of requirements.
                        if file == 'requirements.txt':
                            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", Path.joinpath(root_path, 'requirements.txt')])
                    # Don't cut the update audio short the update
                    if update_audio.is_playing():
                        update_audio.wait_done()

                    # Install the update and restart.
                    self.log.log('Update installed -> restarting the program')
                    os.execl(sys.executable, *([sys.executable] + sys.argv))  # Restart the program

            if not update_found:
                self.log.log("The Stargate is up-to-date.")
                self.cfg.set('software_update_last_check', str(datetime.now() ) )
                self.cfg.set('software_update_status', 'up-to-date' )
                self.cfg.set('software_update_exception', False )

        except Exception as ex:
            self.log.log("Software update failed with error: {}".format(ex))
            self.cfg.set('software_update_last_check', str(datetime.now()))
            # Flag the problem in update_exception, not update_status so that update_status can show that an update is available.
            self.cfg.set('software_update_exception', True)

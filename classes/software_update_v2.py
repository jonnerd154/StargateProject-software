import pwd
import sys
import subprocess

from os import stat, makedirs, path, chown, execl
from ast import literal_eval
from collections import OrderedDict
from pathlib import Path
from datetime import datetime
import requests
from packaging import version
import git

from network_tools import NetworkTools
from version import VERSION as current_version

class SoftwareUpdateV2:

    def __init__(self, app):

        self.current_version = current_version
        self.log = app.log
        self.cfg = app.cfg
        self.audio = app.audio

        # Retrieve the configurations
        self.base_url = self.cfg.get("software_update_url")
        self.file_download_username = self.cfg.get("software_update_username")
        self.file_download_password = self.cfg.get("software_update_password")

        # Initialize the GitPython repo object
        self.repo = git.Repo('.')

        # Update the fan gates from the DB every x hours
        interval = self.cfg.get("software_update_interval")
        app.schedule.every(interval).hours.do( self.check_and_install )

    def get_current_version(self):
        return self.current_version

    def get_available_updates(self):
        # Checks for newer software versions, returns the next-newest release

        # Fetch newest data from Github
        self.repo.remotes.origin.fetch()

        # Loop over the tags, an pick out the software that is newer than the current_version
        current_version_sem = version.parse(self.current_version)
        newer_versions = {}
        for tag in self.repo.tags:
            # Extract some useful information
            tag_name = tag.path.split("/")[2]
            tag_version = tag_name.strip('v')

            # Check if this version is newer than the current one
            if (version.parse(tag_version) > current_version_sem ):
                # Add it to the list of updates
                newer_versions[tag_version] = {
                    "tag_path": tag.path,
                    "tag_commit": str(tag.commit),
                    "tag_name": tag_name,
                    "tag_version": tag_version
                }

        #TODO DEBUG REMOVE
        #pprint(newer_versions)

        # Sort the list and pick out the next-newest version
        return OrderedDict(sorted(newer_versions.items()))

    def do_update(self, version_config):
        self.log.log(f"Starting update from {self.current_version} to v{version_config.get('tag_version')}.")

        # Check if the local copy is dirty, if so, abort.
        if self.repo.is_dirty():
            self.log.log("!!!! Local copy of Gate has been modified, aborting update!")
            return

        # Play a random update-related clip
        self.audio.play_random_clip("update")

        # Git pull
        self.repo.git.checkout(version_config.get('tag_commit'))

        # Run apt-get updates:
        ### TODO

        # Run PIP requirements.txt update
        #subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", Path.joinpath(root_path, 'requirements.txt')])

        # Wait for the clip to finish playing before restarting
        self.audio.random_clip_wait_done()

        self.log.log('Update installed -> restarting the program')

        # TODO: Quit or restart

    def check_and_install(self):

        ## Verify that we have an internet connection, if not, return false.
        if not NetworkTools(self.log).has_internet_access():
            self.log.log('No internet connection available. Aborting Software Update.')
            return

        self.log.log('Checking for software updates.')
        updates_available = self.get_available_updates()
        if len(updates_available) > 0:
            self.log.log(f"Found {len(updates_available)} available update(s)")
            next_version = list(updates_available.values())[0]
            most_recent_version = list(updates_available.values())[len(updates_available)-1]['tag_name']
            self.cfg.set('software_update_status', f"Update Available: {next_version.get('tag_name')}")

            # Start the update process to move us up one version
            self.do_update(next_version)
        else:
            self.log.log("The Stargate is up-to-date.")
            self.cfg.set('software_update_last_check', str(datetime.now() ) )
            self.cfg.set('software_update_status', 'up-to-date' )
            self.cfg.set('software_update_exception', False )

        # except Exception as ex: # pylint: disable=broad-except
        #     self.log.log(f"Software update failed with error: {ex}")
        #     self.cfg.set('software_update_last_check', str(datetime.now()))
        #     # Flag the problem in update_exception, not update_status so that update_status can show that an update is available.
        #     self.cfg.set('software_update_exception', True)

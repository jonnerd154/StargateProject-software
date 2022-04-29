import subprocess
import sys
import os

from collections import OrderedDict
from datetime import datetime
from packaging import version
import git
import rollbar

from network_tools import NetworkTools
from version import VERSION as current_version

class SoftwareUpdateV2:

    def __init__(self, app):

        self.app = app
        self.log = app.log
        self.cfg = app.cfg
        self.audio = app.audio
        self.current_version = current_version

        # Retrieve the configurations
        self.base_url = self.cfg.get("software_update_url")

        # Initialize the GitPython repo object
        self.repo = git.Repo('.')

        # Update the fan gates from the DB every x hours
        interval = self.cfg.get("software_update_interval")
        app.schedule.every(interval).hours.do( self.check_and_install )

    def get_current_version(self):
        return self.current_version

    def delete_local_tags(self):
        for tag in self.repo.tags:
            self.repo.git.tag('-d', tag)

    def get_available_updates(self):
        # Checks for newer software versions, returns the next-newest release

        # Clean slate
        self.repo.config_writer().set_value("core", "fileMode", "false").release() # ignore perms
        self.delete_local_tags()

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
            if version.parse(tag_version) > current_version_sem:
                # Add it to the list of updates
                newer_versions[tag_version] = {
                    "tag_path": tag.path,
                    "tag_commit": str(tag.commit),
                    "tag_name": tag_name,
                    "tag_version": tag_version
                }

        # Sort the list and pick out the next-newest version
        return OrderedDict(sorted(newer_versions.items()))

    def do_update(self, version_config):
        message = f"Starting update from v{self.current_version} to v{version_config.get('tag_version')}."
        self.log.log(message)

        # Check if the local copy is dirty, if so, abort.
        if self.repo.is_dirty():
            self.log.log("!!!! Local copy of Gate has been modified, aborting update!")
            rollbar.report_message("Update Abort: Dirty Local Repo", 'warning')
            return

        # Update Rollbar
        rollbar.report_message(message, 'info')

        # Play a random update-related clip
        self.audio.play_random_clip("update")

        # Git pull
        self.repo.git.checkout(version_config.get('tag_commit'))

        # Run apt-get updates, as supported:
        if self.is_raspi():
            subprocess.check_call(["apt-get", "update"])

        # Run PIP requirements.txt update, as supported
        try:
            if self.is_raspi():
                file_name = 'requirements.txt'
            else:
                # OS lacks hardware support, install minimum requirements:
                file_name = 'requirements_minimum.txt'

            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", self.app.base_path + "/" + file_name])

        except: # pylint: disable=bare-except
            self.log.log("pip update failed")

        # Wait for the clip to finish playing before restarting
        self.audio.random_clip_wait_done()

        self.log.log('Update installed -> restarting the program')
        rollbar.report_message("Update Complete", 'info')

        self.app.restart()

    def check_and_install(self):

        try:
            ## Verify that we have an internet connection, if not, return false.
            if not NetworkTools(self.log).has_internet_access():
                self.log.log('No internet connection available. Aborting Software Update.')
                return

            self.log.log('Checking for software updates.')
            updates_available = self.get_available_updates()
            if len(updates_available) > 0:
                self.log.log(f"Found {len(updates_available)} available update(s)")
                next_version = list(updates_available.values())[0]
                most_recent_version = list(updates_available.values())[len(updates_available)-1]
                self.cfg.set('software_update_status', f"Update Available (next): {most_recent_version.get('tag_name')}")

                rollbar.report_message(f"Update Available (next): {next_version.get('tag_name')}", 'info')

                # Start the update process to move us up one version
                self.do_update(next_version)
            else:
                self.log.log("The Stargate is up-to-date.")
                self.cfg.set('software_update_last_check', str(datetime.now() ) )
                self.cfg.set('software_update_status', 'up-to-date' )
                self.cfg.set('software_update_exception', False )

        except Exception as ex: # pylint: disable=broad-except
            self.log.log(f"Software update failed with error: {ex}")
            self.cfg.set('software_update_last_check', str(datetime.now()))
            # Flag the problem in update_exception, not update_status so that update_status can show that an update is available.
            self.cfg.set('software_update_exception', True)

            rollbar.report_message(f"Update Failed: {ex}", 'error')

    @staticmethod
    def is_raspi():
        # Is an ARM processor, and not Apple Silicon M1 (also ARM)
        return os.uname()[4][:3] == 'arm' and "Darwin" not in os.uname().sysname

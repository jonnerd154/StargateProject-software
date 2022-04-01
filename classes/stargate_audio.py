from os import listdir, path
from random import choice
import subprocess
import simpleaudio as sa

class StargateAudio:

    def __init__(self, app, base_path):

        self.log = app.log
        self.cfg = app.cfg
        self.galaxy_path = app.galaxy_path

        self.sound_fx_root = base_path + "/soundfx/" + self.galaxy_path # No trailing slash

        # Make ready the sound effects
        self.sounds = {}
        self.sounds['rolling_ring'] = { 'file': sa.WaveObject.from_wave_file(str(self.sound_fx_root + "/roll.wav")) }

        self.sounds['dialing_cancel'] = { 'file': self.init_wav_file( "/cancel.wav" ) }
        self.sounds['dialing_fail'] =   { 'file': self.init_wav_file( "/dial_fail_sg1.wav" ) }

        self.sounds['wormhole_open'] =        { 'file': self.init_wav_file( "/eh_usual_open.wav" ) }
        self.sounds['wormhole_established'] = { 'file': self.init_wav_file( "/wormhole-loop.wav" ) }
        self.sounds['wormhole_close'] =       { 'file': self.init_wav_file( "/eh_usual_close.wav" ) }

        self.sounds['chevron_1'] = { 'file': self.init_wav_file( "/chev_usual_1.wav" ) }
        self.sounds['chevron_2'] = { 'file': self.init_wav_file( "/chev_usual_2.wav" ) }
        self.sounds['chevron_3'] = { 'file': self.init_wav_file( "/chev_usual_3.wav" ) }
        self.sounds['chevron_4'] = { 'file': self.init_wav_file( "/chev_usual_4.wav" ) }
        self.sounds['chevron_5'] = { 'file': self.init_wav_file( "/chev_usual_5.wav" ) }
        self.sounds['chevron_6'] = { 'file': self.init_wav_file( "/chev_usual_6.wav" ) }
        self.sounds['chevron_7'] = { 'file': self.init_wav_file( "/chev_usual_7.wav" ) }
        self.incoming_chevron_sounds = [ self.sounds['chevron_4'],  self.sounds['chevron_5'],  self.sounds['chevron_6'],  self.sounds['chevron_7'] ]

        self.random_clip = None

        # Check/set the correct USB audio adapter. This is necessary because different raspberries detects the USB audio adapter differently.
        self.set_correct_audio_output_device()

        self.volume = self.cfg.get('audio_volume')
        self.set_volume(self.volume)

    def sound_start(self, clip_name):
        if self.cfg.get('audio_enable'):
            try:
                self.sounds[clip_name]['obj'] = self.sounds[clip_name]['file'].play()
            except: #pylint: disable=bare-except
                self.log.log("Failed to start audio file - is the USB Audio adapter installed?")

    def sound_stop(self, clip_name):
        if self.cfg.get('audio_enable'):
            self.sounds[clip_name]['obj'].stop()

    def is_playing(self, clip_name):
        if self.cfg.get('audio_enable'):
            return self.sounds[clip_name]['obj'].is_playing()
        return False

    def init_wav_file(self, file_path):
        return sa.WaveObject.from_wave_file(str(self.sound_fx_root + "/" + file_path))

    def incoming_chevron(self):
        if self.cfg.get('audio_enable'):
            try:
                choice(self.incoming_chevron_sounds)['file'].play()
            except: #pylint: disable=bare-except
                self.log.log("Failed to start audio file - is the USB Audio adapter installed?")

    def play_random_clip(self, directory):

        """
        This function plays a random audio clip from the specified folder path. Must include trailing slash.
        :param path_to_folder: The path to the folder containing the audio clips as a string, including the trailing slash.
        :return: the play object is returned.
        """

        if not self.cfg.get('audio_enable'):
            return

        # Don't start playing another clip if one is already playing
        if self.random_clip_is_playing():
            return

        path_to_folder = self.sound_fx_root + "/" + directory
        rand_file = choice(listdir(path_to_folder))
        filepath =  path.join(path_to_folder, rand_file)

        while not path.isfile(filepath): # If the rand_file is not a file. (If it's a directory)
            rand_file = choice(listdir(path_to_folder)) # Choose a new one.
            filepath = path.join(path_to_folder, rand_file) # Update Filepath
        clip = sa.WaveObject.from_wave_file(path_to_folder + '/' + rand_file)

        try:
            self.random_clip = clip.play()
        except: #pylint: disable=bare-except
            self.log.log("Failed to start audio file - is the USB Audio adapter installed?")

        return

    def random_clip_is_playing(self):
        if not self.cfg.get('audio_enable'):
            return False

        try:
            return self.random_clip.is_playing()
        except AttributeError: # If there's never been a clip playing, this will be None.
            return False

    def random_clip_wait_done(self):
        if self.random_clip_is_playing():
            self.random_clip.wait_done()

    @staticmethod
    def get_usb_audio_device_card_number():
        """
        This function gets the card number for the USB audio adapter.
        :return: It will return a number (string) that should correspond to the card number for the USB adapter. If it can't find it, it returns 1
        """
        try:
            audio_devices = subprocess.run(['aplay', '-l'], capture_output=True, text=True, check=False).stdout.splitlines() #TODO: Check should be true, throws exception if non-zero exit code
            for line in audio_devices:
                if 'USB' in line:
                    return line[5]
                return 1
        except FileNotFoundError:
            return 1

    @staticmethod
    def get_active_audio_card_number():
        """
        This function gets the active audio card number from the /usr/share/alsa/alsa.conf file.
        :return: It will return an integer that should correspond to the card number for the USB adapter. If it can't find it, it returns 1
        """
        # Get the contents of the file
        try:
            with open('/usr/share/alsa/alsa.conf', 'r', encoding="utf8") as alsa_file:
                lines = alsa_file.readlines()
            for line in lines:
                if 'defaults.ctl.card ' in line:
                    return line[-2]
            return None
        except FileNotFoundError:
            return None

    def set_correct_audio_output_device(self):
        """
        This functions checks if the USB audio adapter is correctly set in the alsa.conf file and fixes it if not.
        :return: Nothing is returned
        """

        # pylint: disable=anomalous-backslash-in-string

        try:
            # If the wrong card is set in the alsa.conf file
            if self.get_usb_audio_device_card_number() != self.get_active_audio_card_number():
                self.log.log(f'Updating the alsa.conf file with card {self.get_usb_audio_device_card_number()}')

                ctl = 'defaults.ctl.card ' + str(self.get_usb_audio_device_card_number())
                pcm = 'defaults.pcm.card ' + str(self.get_usb_audio_device_card_number())
                # replace the lines in the alsa.conf file.
                subprocess.run(['sudo', 'sed', '-i', f"/defaults.ctl.card /c\{ctl}", '/usr/share/alsa/alsa.conf'], check=False) #TODO: Check should be true
                subprocess.run(['sudo', 'sed', '-i', f"/defaults.pcm.card /c\{pcm}", '/usr/share/alsa/alsa.conf'], check=False) #TODO: Check should be true
        except subprocess.CalledProcessError:
            self.log.log("Failed to set audio adapter config")

    def set_volume(self, percent_value):
        """
        Attempt to set the audio volume level according to the percent_value.
        :param percent_value: an integer between 0 and 100. 65 seems good.
        :return: Nothing is returned.
        """

        # Update the config
        self.volume = percent_value
        self.cfg.set("audio_volume", self.volume)

        try:
            subprocess.run(['amixer', '-M', 'set', 'Headphone', f'{str(self.volume)}%'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False) #TODO: Check should be true
            subprocess.run(['amixer', '-M', 'set', 'PCM', f'{str(self.volume)}%'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False) #TODO: Check should be true
            subprocess.run(['amixer', '-M', 'set', 'Speaker', f'{str(self.volume)}%'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False) #TODO: Check should be true
            self.log.log(f'Audio set to {self.volume}%')
        except (FileNotFoundError, subprocess.CalledProcessError):
            self.log.log('Unable to set the volume. You can set the volume level manually by running the alsamixer command.')

    def volume_up(self, step=5):
        # Get current volume
        new_volume = self.volume

        # Increase, to a max of 100
        new_volume+=step
        new_volume = min(new_volume, 100)

        # Set the volume, which also updates the config file
        self.set_volume(new_volume)

    def volume_down(self, step=5):
        # Get current volume
        new_volume = self.volume

        # Increase, to a max of 100
        new_volume-=step
        new_volume = max(new_volume, 0)

        # Set the volume, which also updates the config file
        self.set_volume(new_volume)

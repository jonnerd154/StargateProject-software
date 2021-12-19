import simpleaudio as sa
from os import listdir, path
from random import choice
import subprocess

class StargateAudio:

    def __init__(self, app, base_path):

        self.log = app.log
        self.cfg = app.cfg

        self.soundFxRoot = base_path + "/soundfx" # No trailing slash

        # Make ready the sound effects
        self.sounds = {}
        self.sounds['rolling_ring'] = { 'file': sa.WaveObject.from_wave_file(str(self.soundFxRoot + "/roll.wav")) }

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
        
        # Check/set the correct USB audio adapter. This is necessary because different raspberries detects the USB audio adapter differently.
        self.set_correct_audio_output_device()
        
        self.volume = self.cfg.get('volume_as_percent')
        self.set_volume(self.volume)
        

    def sound_start(self, clip_name):
        self.sounds[clip_name]['obj'] = self.sounds[clip_name]['file'].play()

    def sound_stop(self, clip_name):
        self.sounds[clip_name]['obj'].stop()

    def is_playing(self, clip_name):
        return self.sounds[clip_name]['obj'].is_playing()

    def init_wav_file(self, file_path):
        return sa.WaveObject.from_wave_file(str(self.soundFxRoot + "/" + file_path))

    def play_random_clip_from_group(self, group_name, wait_done):
        handle = choice(self.incoming_chevron_sounds)['file'].play()
        
    def play_random_clip(self, directory):

        """
        This function plays a random audio clip from the specified folder path. Must include trailing slash.
        :param path_to_folder: The path to the folder containing the audio clips as a string, including the trailing slash.
        :return: the play object is returned.
        """

        path_to_folder = self.soundFxRoot + "/" + directory
        rand_file = choice(listdir(path_to_folder))
        filepath =  path.join(path_to_folder, rand_file)

        while not path.isfile(filepath): # If the rand_file is not a file. (If it's a directory)
            rand_file = choice(listdir(path_to_folder)) # Choose a new one.
            filepath = path.join(path_to_folder, rand_file) # Update Filepath
        random_audio = sa.WaveObject.from_wave_file(path_to_folder + '/' + rand_file)
        return random_audio.play()


    def get_usb_audio_device_card_number(self):
        """
        This function gets the card number for the USB audio adapter.
        :return: It will return a number (string) that should correspond to the card number for the USB adapter. If it can't find it, it returns 1
        """
        audio_devices = subprocess.run(['aplay', '-l'], capture_output=True, text=True).stdout.splitlines()
        for line in audio_devices:
            if 'USB' in line:
                return line[5]
        return 1


    def get_active_audio_card_number(self):
        """
        This function gets the active audio card number from the /usr/share/alsa/alsa.conf file.
        :return: It will return an integer that should correspond to the card number for the USB adapter. If it can't find it, it returns 1
        """
        # Get the contents of the file
        with open('/usr/share/alsa/alsa.conf') as alsa_file:
            lines = alsa_file.readlines()
        for line in lines:
            if 'defaults.ctl.card ' in line:
                return line[-2]


    def set_correct_audio_output_device(self):
        """
        This functions checks if the USB audio adapter is correctly set in the alsa.conf file and fixes it if not.
        :return: Nothing is returned
        """
        try:
            # If the wrong card is set in the alsa.conf file
            if get_usb_audio_device_card_number() != get_active_audio_card_number():
                self.log.log(f'Updating the alsa.conf file with card {get_usb_audio_device_card_number()}')

                ctl = 'defaults.ctl.card ' + str(get_usb_audio_device_card_number())
                pcm = 'defaults.pcm.card ' + str(get_usb_audio_device_card_number())
                # replace the lines in the alsa.conf file.
                subprocess.run(['sudo', 'sed', '-i', f"/defaults.ctl.card /c\{ctl}", '/usr/share/alsa/alsa.conf'])
                subprocess.run(['sudo', 'sed', '-i', f"/defaults.pcm.card /c\{pcm}", '/usr/share/alsa/alsa.conf'])
        except:
            pass

    def set_volume(self, percent_value):
        """
        Attempt to set the audio volume level according to the percent_value.
        :param percent_value: an integer between 0 and 100. 65 seems good.
        :return: Nothing is returned.
        """
        
        # Update the config
        self.volume = percent_value
        self.cfg.set("volume_as_percent", self.volume)
        
        try:
            subprocess.run(['amixer', '-M', 'set', 'Headphone', f'{str(self.volume)}%'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['amixer', '-M', 'set', 'PCM', f'{str(self.volume)}%'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['amixer', '-M', 'set', 'Speaker', f'{str(self.volume)}%'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.log.log(f'Audio set to {self.volume}%')
        except:
            self.log.log('Unable to set the volume. You can set the volume level manually by running the alsamixer command.')

    def volume_up(self, step=5):
        # Get current volume
        new_volume = self.volume
        
        # Increase, to a max of 100
        new_volume+=step
        if (new_volume>100):
            new_volume = 100
        
        # Set the volume, which also updates the config file
        self.set_volume(new_volume)
    
    def volume_down(self, step=5):
        # Get current volume
        new_volume = self.volume
        
        # Increase, to a max of 100
        new_volume-=step
        if (new_volume<0):
            new_volume = 0
        
        # Set the volume, which also updates the config file
        self.set_volume(new_volume)
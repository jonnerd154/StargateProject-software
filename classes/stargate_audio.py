import simpleaudio as sound

class StargateAudio:

    def __init__(self, app):

        self.log = app.log
        self.cfg = app.cfg
        
        self.soundFxRoot = "/home/sg1/sg1/soundfx" #No trailing slash ## TODO: Move to config or Parent(__file__)

        
        self.sounds = {}
        self.sounds['rolling_ring'] = sound.WaveObject.from_wave_file(str(self.soundFxRoot + "/roll.wav"))

    def sound_start(self, clip_name):
        self.sounds[clip_name].play()
        
    def sound_stop(self, clip_name):
        self.sounds[clip_name].stop()

    def play_random_audio_clip(self, path_to_folder):
        from os import listdir, path
        from random import choice
        import simpleaudio as sa
        """
        This function plays a random audio clip from the specified folder path. Must include trailing slash.
        :param path_to_folder: The path to the folder containing the audio clips as a string, including the trailing slash.
        :return: the play object is returned.
        """
        
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
        import subprocess
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
        import subprocess
    try:
        # If the wrong card is set in the alsa.conf file
        if get_usb_audio_device_card_number() != get_active_audio_card_number():
            log('sg1.log', f'Updating the alsa.conf file with card {get_usb_audio_device_card_number()}')
            print(f'Updating the alsa.conf file with card {get_usb_audio_device_card_number()}')

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
        import subprocess
        try:
            subprocess.run(['amixer', '-M', 'set', 'Headphone', f'{str(percent_value)}%'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['amixer', '-M', 'set', 'PCM', f'{str(percent_value)}%'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['amixer', '-M', 'set', 'Speaker', f'{str(percent_value)}%'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.log.log(f'Audio set to {percent_value}%')
        except:
            self.log.log('Unable to set the volume. You can set the volume level manually by running the alsamixer command.')

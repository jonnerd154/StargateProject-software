import simpleaudio as sa
from time import sleep
wave_obj = sa.WaveObject.from_wave_file("/home/sg1/sg1/soundfx/inaudible.wav")
play_obj = wave_obj.play()
sleep(1) # End after 1 second
# play_obj.wait_done()
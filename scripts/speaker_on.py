from time import sleep
import simpleaudio as sa

wave_obj = sa.WaveObject.from_wave_file("/home/pi/sg1_v4/soundfx/inaudible.wav")
play_obj = wave_obj.play()
sleep(1) # End after 1 second
# play_obj.wait_done()

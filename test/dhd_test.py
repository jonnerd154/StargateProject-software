from classes.DHD import DHDv2
from time import sleep

# Initiate the DHD object.
dhd_port = "/dev/serial/by-id/usb-Adafruit_ItsyBitsy_32u4_5V_16MHz_HIDPC-if00"
dhd_serial_baud_rate = 115200
dhd = DHDv2(dhd_port, dhd_serial_baud_rate)
dhd.setBrightnessCenter(100)
dhd.setBrightnessSymbols(3)
dhd.setAllPixelsToColor(0, 0, 0)
dhd.latch()

# Run through all the DHD key lights
for led in reversed(range(1, 39,)):
    dhd.setPixel_use_LED_id(led, 250, 117, 0)
    dhd.latch()
    sleep(0.15)
    dhd.setPixel_use_LED_id(led, 0, 0, 0)
    dhd.latch()
# The centre button
dhd.setPixel_use_LED_id(0, 255, 0, 0)
dhd.latch()
sleep(2)
dhd.clearAllPixels()
dhd.latch()

## the dictionary containing the key to symbol-number relations. https://thestargateproject.com/symbols_overview.pdf
key_symbol_map = {'8':1, 'C':2, 'V':3, 'U':4, 'a':5, '3':6, '5':7, 'S':8, 'b':9, 'K':10, 'X':11, 'Z':12,
                  'E':14, 'P':15, 'M':16, 'D':17, 'F':18, '7':19, 'c':20, 'W':21, '6':22, 'G':23, '4':24,
                  'B':25, 'H':26, 'R':27, 'L':28, '2':29, 'N':30, 'Q':31, '9':32, 'J':33, '0':34, 'O':35,
                  'T':36, 'Y':37, '1':38, 'I':39, 'A':0
                  }
def ask_for_input():
    """
    This function collects key inputs from the user, and does actions based on input.
    :return: Nothing is returned
    """
    def key_press():
        """
        This helper function stops the program (thread) and waits for a single keypress.
        :return: The pressed key is returned.
        """
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    active = [] # keep a list of pressed DHD keys.
    while True:  # Keep running
        key = key_press()  # Save the input as a variable

        # convert key press to symbol_number. https://thestargateproject.com/symbols_overview.pdf
        symbol_number = key_symbol_map[str(key)]

        # Toggle the light for the pressed key
        if symbol_number not in active:
            active.append(symbol_number)
            if symbol_number == 0:
                dhd.setPixel(symbol_number, 255, 0, 0)
                dhd.latch()
            else:
                dhd.setPixel(symbol_number, 250, 117, 0)
                dhd.latch()
        else:
            active.remove(symbol_number)
            dhd.setPixel(symbol_number, 0, 0, 0)
            dhd.latch()

# Run the DHD test script!
ask_for_input()
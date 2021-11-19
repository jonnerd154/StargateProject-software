import sys, tty, termios
from pathlib import Path

class KeyboardManager:

    def __init__(self, stargate):

        self.log = stargate.log
        self.cfg = stargate.cfg
        self.audio = stargate.audio
                
    def key_press(self):
        """
        This helper function stops the program (thread) and waits for a single keypress.
        :return: The pressed key is returned.
        """
        
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    
    def ask_for_input(self, stargate):
        """
        This function takes the stargate as input and listens for user input (from the DHD or keyboard). The pressed key
        is converted to a stargate symbol number as seen in this document: https://www.rdanderson.com/stargate/glyphs/index.htm
        This function is run in parallel in its own thread.
        :param stargate: The stargate object itself.
        :return: Nothing is returned, but the stargate is manipulated.
        """

        ## the dictionary containing the key to symbol-number relations.
        key_symbol_map = {'8': 1, 'C': 2, 'V': 3, 'U': 4, 'a': 5, '3': 6, '5': 7, 'S': 8, 'b': 9, 'K': 10, 'X': 11, 'Z': 12,
                          'E': 14, 'P': 15, 'M': 16, 'D': 17, 'F': 18, '7': 19, 'c': 20, 'W': 21, '6': 22, 'G': 23, '4': 24,
                          'B': 25, 'H': 26, 'R': 27, 'L': 28, '2': 29, 'N': 30, 'Q': 31, '9': 32, 'J': 33, '0': 34, 'O': 35,
                          'T': 36, 'Y': 37, '1': 38, 'I': 39
                          }

        self.log.log("Listening for input from the DHD. You can abort with the '-' key.")
        while True: # Keep running and ask for user input
            key = self.key_press() #Save the input key as a variable
            ## Convert the key to the correct symbol_number. ##
            try:
                symbol_number = key_symbol_map[key]  # convert key press to symbol_number
            except KeyError:  # if the pressed button is not a key in the self.key_symbol_map dictionary
                symbol_number = 'unknown'
                if key == '-':
                    symbol_number = 'abort'
                if key == 'A':
                    symbol_number = 'centre_button_outgoing'

            self.audio.play_random_clip("DHD")
            self.log.log(f'key: {key} -> symbol: {symbol_number}')

            ## If the user inputs the - key to abort. Not possible from the DHD.
            if key == '-':
                stargate.running = False # Stop the stargate object from running.
                break # This will break us out of the while loop and end the function.

            ## If the user hits the centre_button
            elif key == 'A':
                # If we are dialling
                if len(stargate.address_buffer_outgoing) > 0 and not stargate.wormhole:
                    stargate.centre_button_outgoing = True
                    stargate.dialer.hardware.setPixel(0, 255, 0, 0) # Activate the centre_button_outgoing light
                    stargate.dialer.hardware.latch()
                # If an outgoing wormhole is established
                if stargate.wormhole == 'outgoing':
                    if stargate.fan_gate_online_status: # If we are connected to a fan_gate
                        send_to_remote_stargate(get_ip_from_stargate_address(stargate.address_buffer_outgoing, stargate.fan_gates), 'centre_button_incoming')
                    if not stargate.black_hole: # If we did not dial the black hole.
                        stargate.wormhole = False # cancel outgoing wormhole

            # If we are hitting symbols on the DHD.
            elif symbol_number != 'unknown' and symbol_number not in stargate.address_buffer_outgoing:
                # If we have not yet activated the centre_button
                if not (stargate.centre_button_outgoing or stargate.centre_button_incoming):
                    ### DHD lights ###
                    stargate.dialer.hardware.setPixel(symbol_number, 250, 117, 0)
                    stargate.dialer.hardware.latch()
                    stargate.address_buffer_outgoing.append(symbol_number)
                    self.log.log(f'address_buffer_outgoing: {stargate.address_buffer_outgoing}') # Log the address_buffer

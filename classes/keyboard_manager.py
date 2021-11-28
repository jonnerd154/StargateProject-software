import sys, tty, termios

class KeyboardManager:

    def __init__(self, stargate):

        self.stargate = stargate
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

        self.log.log("Listening for input from the Dialer. You can abort with the '-' key.")
        while True: # Keep running and ask for user input
            key = self.key_press() #Save the input key as a variable
            ## Convert the key to the correct symbol_number. ##
            try:
                symbol_number = key_symbol_map[key]  # convert key press to symbol_number
            except KeyError:  # if the pressed button is not a key in the self.key_symbol_map dictionary
                symbol_number = 'unknown'
                if key == '-':
                    symbol_number = 'abort'
                elif key == 'A':
                    symbol_number = 'centre_button_outgoing'
                    self.log.log(f'key: {key} -> symbol: {symbol_number} CENTER')
                else:
                    self.log.log(f'key: {key} -> symbol: {symbol_number} SYMBOL')

            ## If the user inputs the - key to abort. Not possible from the DHD.
            if key == '-':
                self.log.log("Abort Requested: Shutting down any active wormholes, stopping the gate.")
                self.stargate.wormhole = False # Shutdown any open wormholes (particularly if turned on via web interface)
                self.stargate.running = False  # Stop the stargate object from running.

                break # This will break us out of the while loop and end the function.

            ## If the user hits the centre_button
            elif key == 'A':
                self.queue_center_button()

            # If we are hitting symbols on the DHD.
            else:
                self.queue_symbol(symbol_number)
                
    def queue_symbol(self, symbol_number):
        self.audio.play_random_clip("DHD")
        if symbol_number != 'unknown' and symbol_number not in self.stargate.address_buffer_outgoing:
            # If we have not yet activated the centre_button
            if not (self.stargate.centre_button_outgoing or self.stargate.centre_button_incoming):
                self.stargate.dialer.hardware.set_symbol_on( symbol_number ) # Light this symbol on the DHD

                # Append the symbol to the outgoing address buffer
                self.stargate.address_buffer_outgoing.append(symbol_number)
                self.log.log(f'address_buffer_outgoing: {self.stargate.address_buffer_outgoing}') # Log the address_buffer
            
    def queue_center_button(self):
        self.audio.play_random_clip("DHD")
        # If we are dialing
        if len(self.stargate.address_buffer_outgoing) > 0 and not self.stargate.wormhole:
            self.stargate.centre_button_outgoing = True
            self.stargate.dialer.hardware.set_center_on() # Activate the centre_button_outgoing light
        # If an outgoing wormhole is established
        if self.stargate.wormhole == 'outgoing':
            if self.stargate.fan_gate_online_status: # If we are connected to a fan_gate
                self.stargate.subspace.send_to_remote_stargate(get_ip_from_stargate_address(self.stargate.address_buffer_outgoing, self.stargate.fan_gates), 'centre_button_incoming')
            if not self.stargate.black_hole: # If we did not dial the black hole.
                self.stargate.wormhole = False # cancel outgoing wormhole            if stargate.fan_gate_online_status: # If we are connected to a fan_gate
                self.stargate.subspace.send_to_remote_stargate(get_ip_from_stargate_address(self.stargate.address_buffer_outgoing, self.stargate.fan_gates), 'centre_button_incoming')
            if not self.stargate.black_hole: # If we did not dial the black hole.
                self.stargate.wormhole = False # cancel outgoing wormhole
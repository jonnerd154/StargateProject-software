import sys
from threading import Thread
import tty
import termios
import evdev

class KeyboardManager:

    def __init__(self, stargate, is_daemon):

        self.stargate = stargate
        self.is_daemon = is_daemon
        self.log = stargate.log
        self.cfg = stargate.cfg
        self.audio = stargate.audio
        self.addr_manager = stargate.addr_manager
        self.address_book = stargate.addr_manager.get_book()

        if is_daemon:
            self.keyboard_direct_thread_start()
        else:
            self.stdin_thread_start()

    @staticmethod
    def get_symbol_key_map():
        # Symbol numbers are mapped as in this document: https://www.rdanderson.com/stargate/glyphs/index.htm
        return {'8': 1, 'C': 2, 'V': 3, 'U': 4, 'a': 5, '3': 6, '5': 7, 'S': 8, 'b': 9, 'K': 10, 'X': 11, 'Z': 12,
                  'E': 14, 'P': 15, 'M': 16, 'D': 17, 'F': 18, '7': 19, 'c': 20, 'W': 21, '6': 22, 'G': 23, '4': 24,
                  'B': 25, 'H': 26, 'R': 27, 'L': 28, '2': 29, 'N': 30, 'Q': 31, '9': 32, 'J': 33, '0': 34, 'O': 35,
                  'T': 36, 'Y': 37, '1': 38, 'I': 39
                  }

    @staticmethod
    def get_abort_characters():
        # If these symbols are entered, the gate will shutdown
        return [ '-', '\x03' ]  # '\x03' == Ctrl-C

    def stdin_thread_start(self):
        ## Create a background thread that runs in parallel and asks for user inputs from the DHD or keyboard.
        self.ask_for_input_thread = Thread(target=self.thread_stdin, args=([self.stargate]))
        self.ask_for_input_thread.start()  # start

    @staticmethod
    def block_for_stdin():
        """
        This helper function stops the program (thread) and waits for a single keypress on STDIN.
        :return: The pressed key is returned.
        """

        file_desc = sys.stdin.fileno()
        old_settings = termios.tcgetattr(file_desc)
        try:
            tty.setraw(sys.stdin.fileno())
            char = sys.stdin.read(1)
        finally:
            termios.tcsetattr(file_desc, termios.TCSADRAIN, old_settings)
        return char

    def thread_stdin(self, stargate):
        """
        This function takes the stargate as input and listens for user input (from the DHD or keyboard).
        This function is run in parallel in its own thread.
        :return: Nothing is returned, but the stargate is manipulated.
        """

        stargate.log.log("Listening for input from the DHD/Keyboard on STDIN. You can abort with the '-' key.")
        while stargate.running:
            self.keypress_handler( self.block_for_stdin() ) # Blocks the thread until a character is subspace_client_server_thread

    def keyboard_direct_thread_start(self):
        ## Create a background thread that runs in parallel and asks for user inputs from the DHD or keyboard.
        self.ask_for_input_thread = Thread(target=self.thread_keyboard_direct, args=([self.stargate]))
        self.ask_for_input_thread.start()  # start

    def thread_keyboard_direct(self, stargate):
        """
        This function takes the stargate as input and listens for user input (from the DHD or keyboard).
        This function is run in parallel in its own thread.
        :return: Nothing is returned, but the stargate is manipulated.
        """

        stargate.log.log("Listening for input from the DHD/Keyboard via direct input. You can abort with the '-' key.")
        while stargate.running:
            device = evdev.InputDevice('/dev/input/event1')
            stargate.log.log(device)

            self.block_for_keyboard_direct(stargate.log, device)
            #self.keypress_handler( self.block_for_keyboard_direct(device) ) # Blocks the thread until a character is subspace_client_server_thread

    @staticmethod
    def block_for_keyboard_direct(log, device):
        """
        This helper function stops the program (thread) and waits for a single keypress via direct keyboard input.
        :return: The pressed key is returned.
        """
        for event in device.read_loop():
            if event.type == evdev.ecodes.EV_KEY:
                log.log(evdev.categorize(event))

    def keypress_handler( self, key ):
        """
        This function takes a keypress and interprets it's meaning for the Stargate.
        :return: Nothing is returned, but the stargate is manipulated.
        """

        ## If the user inputs one of the abort characters, stop the software. Not possible from the DHD.
        if key in self.get_abort_characters():
            self.log.log("Abort Requested: Shutting down any active wormholes, stopping the gate.")
            self.stargate.wormhole_active = False # Shutdown any open wormholes (particularly if turned on via web interface)
            self.stargate.running = False  # Stop the stargate object from running.
            return

        # Center Button
        if key == 'A':
            symbol_number = 'centre_button_outgoing'
            self.log.log(f'key: {key} -> symbol: {symbol_number} CENTER')
            self.queue_center_button()
            return

        # Try to convert other key presses to symbol_number
        try:
            symbol_number = self.get_symbol_key_map()[key]
            self.queue_symbol(symbol_number)
            return
        except KeyError:
            # The key pressed is not a symbol
            self.log.log(f'Unknown key: {key}')

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
        if len(self.stargate.address_buffer_outgoing) > 0 and not self.stargate.wormhole_active:
            self.stargate.centre_button_outgoing = True
            self.stargate.dialer.hardware.set_center_on() # Activate the centre_button_outgoing light
        # If an outgoing wormhole is established
        if self.stargate.wormhole_active == 'outgoing':
            # TODO: We shouldn't be doing subspace-y stuff in the keyboard manager
            if self.addr_manager.is_fan_made_stargate(self.stargate.address_buffer_outgoing) \
             and self.stargate.fan_gate_online_status: # If we are connected to a fan_gate
                self.stargate.subspace_client.send_to_remote_stargate(self.addr_manager.get_ip_from_stargate_address(self.stargate.address_buffer_outgoing), 'centre_button_incoming')
            if not self.stargate.black_hole: # If we did not dial the black hole.
                self.stargate.wormhole_active = False # cancel outgoing wormhole

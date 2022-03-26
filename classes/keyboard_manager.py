import sys
from threading import Thread
import tty
import termios
import subspace_messages

class KeyboardManager:

    def __init__(self, stargate, is_daemon):

        self.stargate = stargate
        self.is_daemon = is_daemon
        self.log = stargate.log
        self.cfg = stargate.cfg
        self.audio = stargate.audio
        self.addr_manager = stargate.addr_manager
        self.address_book = stargate.addr_manager.get_book()
        self.symbol_manager = stargate.symbol_manager

        self.dhd_test_enable = False
        self.dhd_test_active_buttons = []
        self.center_button_key = "A"

        if is_daemon:
            self.keyboard_direct_thread_start()
        else:
            self.stdin_thread_start()

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

        stargate.log.log("Initializing Keyboard listeners")

        # pylint: disable-next=import-outside-toplevel
        import keyboard # importing this on MacOS causes a seg fault

        for char_in in self.symbol_manager.get_symbol_key_map():
            # Transform upper case presses
            char = char_in
            if char_in != char_in.lower():
                char = f"shift+{char.lower()}"

            # Add the hotkey
            keyboard.add_hotkey(char, lambda char_in=char_in: self.keypress_handler(char_in))

        # Add one for the center button ("A")
        keyboard.add_hotkey("shift+a", lambda: self.keypress_handler(self.center_button_key))

        stargate.log.log("Listening for input from the DHD/Keyboard via direct input. You can abort with the '-' key.")
        keyboard.wait()

    def enable_dhd_test( self, enable ):
        if enable:
            self.stargate.shutdown()
            self.dhd_test_enable = True
        else:
            self.dhd_test_enable = False
            self.stargate.dialer.hardware.clear_lights()

        self.dhd_test_active_buttons = []

    def handle_dhd_test(self, key):
        # Handle test mode here
        try:
            symbol_number = self.symbol_manager.get_symbol_key_map()[key]
            self.log.log(f'DHD Test: Pressed Key {key} --> Symbol {symbol_number}')
        except KeyError:
            if key == self.center_button_key:
                self.log.log(f'DHD Test: Pressed Center Button {key} --> Symbol {symbol_number}')
                symbol_number = 0
            else:
                self.log.log(f'DHD Test: Key NOT RECOGNIZED {key}')

        if symbol_number not in self.dhd_test_active_buttons:
            self.dhd_test_active_buttons.append(symbol_number)
            if symbol_number == 0:
                self.stargate.dialer.hardware.set_pixel(symbol_number, 255, 0, 0) # TODO: Use colors in config
                self.stargate.dialer.hardware.latch()
            else:
                self.stargate.dialer.hardware.set_pixel(symbol_number, 250, 117, 0) # TODO: Use colors in config
                self.stargate.dialer.hardware.latch()
        else:
            self.dhd_test_active_buttons.remove(symbol_number)
            self.stargate.dialer.hardware.clear_pixel(symbol_number)
            self.stargate.dialer.hardware.latch()

    def keypress_handler( self, key ):
        """
        This function takes a keypress and interprets it's meaning for the Stargate.
        :return: Nothing is returned, but the stargate is manipulated.
        """

        if self.dhd_test_enable:
            self.handle_dhd_test( key )
            return

        ## If the user inputs one of the abort characters, stop the software. Not possible from the DHD.
        if key in self.get_abort_characters():
            self.log.log("Abort Requested: Shutting down any active wormholes, stopping the gate.")
            self.stargate.wormhole_active = False # Shutdown any open wormholes (particularly if turned on via web interface)
            self.stargate.running = False  # Stop the stargate object from running.
            return

        # Center Button
        if key == self.center_button_key:
            symbol_number = 'centre_button_outgoing'
            self.log.log(f'key: {key} -> symbol: {symbol_number} CENTER')
            self.queue_center_button()
            return

        # Try to convert other key presses to symbol_number
        try:
            symbol_number = self.symbol_manager.get_symbol_key_map()[key]
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
                self.stargate.subspace_client.send_to_remote_stargate(self.addr_manager.get_ip_from_stargate_address(self.stargate.address_buffer_outgoing), subspace_messages.DIAL_CENTER_INCOMING)
            if not self.stargate.black_hole: # If we did not dial the black hole.
                self.stargate.wormhole_active = False # cancel outgoing wormhole

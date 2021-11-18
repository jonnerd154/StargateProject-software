from DIAL import Dial
from WORMHOLE import Wormhole
from STARGATE_SERVER import StargateServer

from threading import Thread
from time import time, sleep
from pathlib import Path
import simpleaudio as sa
from random import randrange

from stargate_address import local_stargate_address


from stargate_address import fan_gates
from hardcoded_addresses import known_planets

# New
from chevrons import ChevronManager
from dialers import Dialer
from network_tools import NetworkTools
from keyboard_manager import KeyboardManager


class StargateSG1:
    """
    This is the class to create the stargate object itself.
    """
    def __init__(self, app):

        self.app = app
        self.log = app.log
        self.cfg = app.cfg
        self.audio = app.audio
        
        self.keyboard = KeyboardManager(self)
        
        self.root_path = Path(__file__).parent.absolute()

        ### This is the states and features of the StargateSG1 object. ###
        self.running = True
        self.last_activity_time = None # A variable to store the last user input time
        self.address_buffer_outgoing = [] #Storage buffer for dialed outgoing address
        self.address_buffer_incoming = [] #Storage buffer for dialed incoming address
        self.centre_button_outgoing = False #A variable for the state of the centre button, outgoing.
        self.centre_button_incoming = False #A variable for the state of the centre button, incoming.
        self.locked_chevrons_outgoing = 0 # The current number of locked outgoing chevrons
        self.locked_chevrons_incoming = 0 # The current number of locked outgoing chevrons
        self.wormhole = False # The state of the wormhole.
        self.black_hole = False # Did we dial the black hole?
        self.fan_gate_online_status = None # To keep track of the dialled fan_gate status
        self.fan_gate_incoming_IP = None # To keep track of the IP address for the remote gate that establishes a wormhole

        ### Set the local stargate address so that it's ready to accept incoming connections from the internet, or other local stargates.
        # The local stargate address is set in a separate file; stargate_address.py. This way it won't get overwritten with an automatic update.

        self.local_stargate_address = local_stargate_address

        ### Set up the needed classes and make them ready to use ###
        ### Initiate the spinning ring dial object.
        self.ring = Dial(self)
        self.ring.release()
        self.ring.homingManager.set_ring(self.ring)

        ### initiate the Chevrons:
        # The chevron config is moved to the chevrons.py file. The chevron.py file is not overwritten with the automatic update
        # so you can keep your custom setup if you have one.
        self.chevrons = ChevronManager(self)

        # A "Dialer" is either a Keyboard or DHDv2
        self.dialer = Dialer(self)

        ### Initiate the Wormhole object.
        self.wh = Wormhole(self)
        self.wh.clear_wormhole() # Start with the wormhole off.

        ### Stargate fan-made gate addresses ###
        # The custom fan_gate addresses is set in a separate file; stargate_address.py. This way it won't get overwritten with an automatic update.
        self.fan_gates = fan_gates

        ### Check if we have an internet connection.
        netTools = NetworkTools(self.log)
        self.internet = netTools.has_internet_access()

        ### Other known remote fan_gates will be added automatically to this dictionary
        from subspace import Subspace
        self.subspace = Subspace(self)
        if self.internet:
            self.fan_gates = self.subspace.get_fan_gates_from_db(self.fan_gates)
        
        ## Create a background thread that runs in parallel and asks for user inputs from the DHD or keyboard.
        self.ask_for_input_thread = Thread(target=self.keyboard.ask_for_input, args=(self,))
        self.ask_for_input_thread.start()  # start

        ### Run the stargate server ###
        # The stargate_server runs in it's own thread listening for incoming wormholes
        if self.internet:
            self.stargate_server_thread = Thread(target=StargateServer(self).start, daemon=True, args=())
            self.stargate_server_thread.start()

        ### Set volume ###
        self.audio.set_volume(65)

        ### Notify that the Stargate is ready
        self.audio.play_random_audio_clip(str(self.root_path / "../soundfx/startup/"))
        self.log.log('The Stargate is started and ready!')

    ## Methods to manipulate the StargateSG1 object ###
    def update(self):
        """
        This is the main method to keep the stargate running and make decisions based on the manipulated objects variables.
        There are basically two main phases, the dialling phase and the wormhole phase.
        :return: Nothing is returned.
        """
        while self.running: # If we have not aborted

            ### The Dialling phase###
            if not self.wormhole and self.running: # If we are in the dialing phase

                ## Outgoing Dialling ##
                self.outgoing_dialling()

                ## Incoming Dialling ##
                self.incoming_dialling()

                ## Establishing wormhole ##
                self.establishing_wormhole()

                ### Check for inactivity ###
                # If there are something in the buffers and no activity for 1 minute while dialling.
                if self.inactivity(60):
                    self.log.log('Inactivity detected, aborting.')
                    self.shutdown()

            ### The wormhole phase ###
            elif self.wormhole: # If wormhole
                self.ring.release() # Release the stepper motor.
                self.wh.establish_wormhole() # This will establish the wormhole and keep it running until self.wormhole is False
                #When the wormhole is no longer running
                self.shutdown(cancel_sound=False)

        # When the stargate is no longer running.
        self.shutdown(cancel_sound=False)

    def outgoing_dialling(self):
        """
        This method handles the outgoing dialling of the stargate. It's kept in it's own method so not to clutter up the update method too much.
        :return: Nothing is returned
        """
        if len(self.address_buffer_outgoing) > self.locked_chevrons_outgoing:
            self.ring.dial(self.address_buffer_outgoing[self.locked_chevrons_outgoing], self.locked_chevrons_outgoing + 1)  # Dial the symbol
            self.locked_chevrons_outgoing += 1  # Increment the locked chevrons variable.
            try:
                self.chevrons[self.locked_chevrons_outgoing].on()  # Do the chevron locking thing.
            except KeyError:  # If we dialled more chevrons than the stargate can handle.
                pass  # Just pass without activating a chevron.
            self.log.log(f'Chevron {self.locked_chevrons_outgoing} locked with symbol: {self.address_buffer_outgoing[self.locked_chevrons_outgoing - 1]}')
            self.last_activity_time = self.time()  # update the last_activity_time

            ## Check if we are dialing a fan_gate and send the symbols to the remote gate.
            if self.is_it_a_known_fan_made_stargate(self.address_buffer_outgoing, self.fan_gates, self):
                # If we don't know the online status of the fan_gate or it is online.
                if self.fan_gate_online_status is None or self.fan_gate_online_status:
                    # send the locked symbols to the remote gate.
                    if self.send_to_remote_stargate(self.get_ip_from_stargate_address(self.address_buffer_outgoing, self.fan_gates), str(self.address_buffer_outgoing[0:self.locked_chevrons_outgoing]))[0]:
                        self.log.log(f'Sent to fan_gate: {self.address_buffer_outgoing[0:self.locked_chevrons_outgoing]}')
                        self.fan_gate_online_status = True  # set the online status to True
                    else:
                        self.fan_gate_online_status = False  # set the online status to False, to keep the dialing running more smoothly if the fan_gate is offline.
    def incoming_dialling(self):
        """
        This method handles the incoming dialling of the stargate. It's kept in it's own method so not to clutter up the update method too much.
        :return: Nothing is returned
        """
        # If there are dialled incoming symbols that are not yet locked and we are currently not dialing out.
        if len(self.address_buffer_incoming) > self.locked_chevrons_incoming and len(self.address_buffer_outgoing) == 0:
            # If there are more than one unlocked symbol, add a short delay to avoid locking both symbols at once.
            if len(self.address_buffer_incoming) > self.locked_chevrons_incoming + 1:
                delay = self.randrange(1, 800) / 100  # Add a delay with some randomness
            else:
                delay = 0
            # If we are still receiving the correct address to match the local stargate:
            if self.address_buffer_incoming[0:min(len(self.address_buffer_incoming), 6)] == self.local_stargate_address[0:min(len(self.address_buffer_incoming), 6)]:
                self.locked_chevrons_incoming += 1  # Increment the locked chevrons variable.
                try:
                    self.chevrons[self.locked_chevrons_incoming].incoming_on()  # Do the chevron locking thing.
                except KeyError:  # If we dialled more chevrons than the stargate can handle.
                    pass  # Just pass without activating a chevron.
                # Play the audio clip for incoming wormhole
                if self.locked_chevrons_incoming == 1:
                    self.play_random_audio_clip(str(self.root_path / "../soundfx/IncomingWormhole/"))
                self.sleep(delay)  # if there's a delay, used it.
                self.last_activity_time = self.time()  # update the last_activity_time
                # Do the logging
                self.log.log(f'Incoming: Chevron {self.locked_chevrons_incoming} locked with symbol {self.address_buffer_incoming[self.locked_chevrons_incoming - 1]}')
    def try_sending_centre_button(self):
        """
        This functions simply checks if it is possible to send the centre_button to the remote gate and sends it.
        This method is used in the establishing_wormhole method.
        :return: Nothing is returned.
        """
        if self.fan_gate_online_status and self.centre_button_outgoing and len(self.address_buffer_outgoing) == self.locked_chevrons_outgoing:
            self.send_to_remote_stargate(self.get_ip_from_stargate_address(self.address_buffer_outgoing, self.fan_gates), 'centre_button_incoming')
            self.log.log(f'Sent to fan_gate: centre_button_incoming')
    def establishing_wormhole(self):
        """
        This is the method that decides if we are to establish a wormhole or not
        :return: Nothing is returned, But the self.wormhole variable is changed if we can establish a wormhole.
        """
        ### Establishing wormhole ###
        ## Outgoing wormhole##
        # If the centre_button_outgoing is active and all dialled symbols are locked.
        if self.centre_button_outgoing and (0 < len(self.address_buffer_outgoing) == self.locked_chevrons_outgoing):
            # If we did not dial a fan_gate, set the IP variable to True instead of an IP.
            if self.valid_planet(self.address_buffer_outgoing) != 'fan_gate':
                self.fan_gate_incoming_IP = True
            # Try to send the centre button to the fan_gate:
            self.try_sending_centre_button()
            # Try to establish a wormhole
            if self.possible_to_establish_wormhole():
                print('Valid address is locked')
                self.log.log('Valid address is locked')
                self.wormhole = 'outgoing'
            else:
                print('Unable to establish a Wormhole!')
                self.log.log('Unable to establish a Wormhole!')
                self.shutdown(cancel_sound=False, wormhole_fail_sound=True)

        ## Incoming wormhole ##
        # If the centre_button_incoming is active and all dialled symbols are locked.
        elif self.centre_button_incoming and 0 < len(self.address_buffer_incoming) == self.locked_chevrons_incoming:
            # If the incoming wormhole matches the local address
            if self.address_buffer_incoming[0:-1] == self.local_stargate_address:
                self.wormhole = 'incoming'  # Set the wormhole state to activate the wormhole.
                self.log.log('Incoming address is a match!')
            else:
                print('NOT my local address!')
                self.log.log('Incoming address is NOT a match!')
                self.shutdown(cancel_sound=False, wormhole_fail_sound=True)
    def possible_to_establish_wormhole(self):
        """
        This is a method to help check if we are able to establish a wormhole or not.
        :return: Returns True if we can establish a wormhole, and False if not
        """
        # If the dialled address is valid
        if len(self.address_buffer_outgoing) > 0 and self.valid_planet(self.address_buffer_outgoing) or \
            len(self.address_buffer_incoming) > 0 and self.valid_planet(self.address_buffer_incoming):
            # If we dialed a fan_gate
            if self.valid_planet(self.address_buffer_outgoing) == 'fan_gate':
                # If the dialled fan_gate is not online
                if not self.fan_gate_online_status:
                    self.log.log('The dialled fan_gate is NOT online!')
                    return False
                # If the dialed fan_gate is already busy, with an active wormhole or outgoing dialing is in progress.
                elif self.get_status_of_remote_gate(self.get_ip_from_stargate_address(self.address_buffer_outgoing, self.fan_gates)):
                    self.log.log('The dialled fan_gate is already busy!')
                    return False
            return True  # returns true if we can establish a wormhole
        return False  # returns false if we cannot establish a wormhole.
    def shutdown(self, cancel_sound=True, wormhole_fail_sound=False):
        """
        This method shuts down or resets the stargate object.
        :return:
        """
        # Play the cancel sound
        if cancel_sound:
            self.sa.WaveObject.from_wave_file(str(self.root_path / "../soundfx/cancel.wav")).play()
        # Play the wormhole fail sound
        if wormhole_fail_sound:
            self.sa.WaveObject.from_wave_file(str(self.root_path / "../soundfx/dial_fail_sg1.wav")).play()
        # Turn off the chevrons
        self.all_chevrons_off(self.chevrons)
        # Turn off the DHD lights
        self.dhd.setAllPixelsToColor(0, 0, 0)
        self.dhd.latch()
        # Release the stepper motor.
        self.ring.release()
        self.log.log('Shutting down..')
        # Reset som variables
        self.address_buffer_outgoing = []
        self.address_buffer_incoming = []
        self.last_activity_time = None
        self.centre_button_outgoing = False
        self.centre_button_incoming = False
        self.locked_chevrons_outgoing = 0
        self.locked_chevrons_incoming = 0
        self.wormhole = False
        self.black_hole = False
        self.fan_gate_online_status = None
        self.fan_gate_incoming_IP = None
    def valid_planet(self, address):
        """
            A helper function to check if the dialed address is a valid planet address. This function excludes the
            last symbol in the address since the last symbol can be any point of origin.
            :param address: the destination as a list of symbol numbers
            :return:    If the dialled address is a fan_gate, the string 'fan_gate' is returned.
                        If the dialled address is a known_planet, the string 'known_planet' is returned.
                        Else: False is returned if it is not a valid planet.
            """

        # make a copy of the address, so not to manipulate the input variable directly
        copy_of_address = address[:]

        # remove the point of origin from address
        if len(copy_of_address) != 0:
            del copy_of_address[-1]

        # Eliminate the local(self) address:
        if copy_of_address == self.local_stargate_address:
            return False

        # Check if we dialled the black hole planet
        if copy_of_address == known_planets["P3W-451"]:
            self.black_hole = True
            self.log.log("Oh no! It's the black hole planet!")

        # Check the known_planets dictionary for a match
        for planet in known_planets:
            if known_planets[planet] == copy_of_address:
                return 'known_planet'

        # Check the fan_gates dictionary for a match
        for gate in self.fan_gates:
            if self.fan_gates[gate][0] == copy_of_address:
                return 'fan_gate'
        return False  # Return False if it's not a valid destination
    def inactivity(self, seconds):
        """
        This functions checks if there has been more than the variable seconds of inactivity:
        :param seconds: The number of seconds of allowed inactivity
        :return: True if inactivity is detected, False if not
        """
        if not self.wormhole: #If we are in the dialling phase
            if self.last_activity_time: #If the variable is not None
                if (len(self.address_buffer_incoming) > 0) or (len(self.address_buffer_outgoing) > 0): # If there are something in the buffers
                    if (self.time() - self.last_activity_time) > seconds:
                        return True
        return False

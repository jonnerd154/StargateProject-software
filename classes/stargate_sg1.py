from threading import Thread
from time import time, sleep
from random import randrange

from chevrons import ChevronManager
from dialers import Dialer
from network_tools import NetworkTools
from keyboard_manager import KeyboardManager
from symbol_ring import SymbolRing
from stargate_address_manager import StargateAddressManager
from subspace import Subspace
from wormhole import Wormhole
from stargate_server import StargateServer

class StargateSG1:
    """
    This is the class to create the stargate object itself.
    """
    def __init__(self, app):

        self.app = app
        self.log = app.log
        self.cfg = app.cfg
        self.audio = app.audio
        self.electronics = app.electronics

        # TODO: Move to cfg
        self.inactivityTimeout = 60
        self.defaultAudioVolume = 65

        self.running = True
        self.initialize_gate_state_vars()

        ### Set up the needed classes and make them ready to use ###
        self.netTools = NetworkTools(self.log)
        self.subspace = Subspace(self)
        self.keyboard = KeyboardManager(self)
        self.addrManager = StargateAddressManager(self)
        self.chevrons = ChevronManager(self)
        self.ring = SymbolRing(self)
        self.dialer = Dialer(self) # A "Dialer" is either a Keyboard or DHDv2
        self.wh = Wormhole(self)

        ## Create a background thread that runs in parallel and asks for user inputs from the DHD or keyboard.
        self.ask_for_input_thread = Thread(target=self.keyboard.ask_for_input, args=(self,))
        self.ask_for_input_thread.start()  # start

        ### Run the stargate server if we have an internet connection ###
        # The stargate_server runs in it's own thread listening for incoming wormholes
        if self.netTools.has_internet_access():
            self.stargate_server_thread = Thread(target=StargateServer(self).start, daemon=True, args=())
            self.stargate_server_thread.start()

        ### Set volume ###
        self.audio.set_volume( self.defaultAudioVolume )

        ### Notify that the Stargate is ready
        self.audio.play_random_clip("startup")
        self.log.log('The Stargate is started and ready!')

    def initialize_gate_state_vars(self):
        """
        This method resets the state variables to "gate idle"
        :return:
        """
        # Reset/initialize the state variables and address buffers
        self.address_buffer_outgoing = [] #Storage buffer for dialed outgoing address
        self.address_buffer_incoming = [] #Storage buffer for dialed incoming address
        self.last_activity_time = None # A variable to store the last user input time
        self.centre_button_outgoing = False #A variable for the state of the centre button, outgoing.
        self.centre_button_incoming = False #A variable for the state of the centre button, incoming.
        self.locked_chevrons_outgoing = 0 # The current number of locked outgoing chevrons
        self.locked_chevrons_incoming = 0 # The current number of locked outgoing chevrons
        self.wormhole = False # The state of the wormhole.
        self.black_hole = False # Did we dial the black hole?
        self.fan_gate_online_status = None # To keep track of the dialed fan_gate status
        self.fan_gate_incoming_IP = None # To keep track of the IP address for the remote gate that establishes a wormhole

    ## Methods to manipulate the StargateSG1 object ###
    def update(self):
        """
        This is the main method to keep the stargate running and make decisions based on the manipulated objects variables.
        There are basically two main phases, the dialing phase and the wormhole phase.
        :return: Nothing is returned.
        """
        while self.running: # If we have not aborted

            ### The Dialing phase###
            if not self.wormhole and self.running: # If we are in the dialing phase

                ## Outgoing dialing ##
                self.outgoing_dialing()

                ## Incoming dialing ##
                self.incoming_dialing()

                ## Establishing wormhole ##
                self.establishing_wormhole()

                ### Check for inactivity ###
                # If there are something in the buffers and no activity for 1 minute while dialing.
                if self.inactivity( self.inactivityTimeout ):
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

    def outgoing_dialing(self):
        """
        This method handles the outgoing dialing of the stargate. It's kept in it's own method so not to clutter up the update method too much.
        :return: Nothing is returned
        """
        if len(self.address_buffer_outgoing) > self.locked_chevrons_outgoing:
            self.ring.move_symbol_to_chevron(self.address_buffer_outgoing[self.locked_chevrons_outgoing], self.locked_chevrons_outgoing + 1)  # Dial the symbol
            self.locked_chevrons_outgoing += 1  # Increment the locked chevrons variable.
            try:
                self.chevrons.get(self.locked_chevrons_outgoing).cycle_outgoing()  # Do the chevron locking thing.
            except KeyError:  # If we dialed more chevrons than the stargate can handle.
                pass  # Just pass without activating a chevron.
            self.log.log(f'Chevron {self.locked_chevrons_outgoing} locked with symbol: {self.address_buffer_outgoing[self.locked_chevrons_outgoing - 1]}')
            self.last_activity_time = time()  # update the last_activity_time

            ## Check if we are dialing a fan_gate and send the symbols to the remote gate.
            if self.addrManager.is_fan_made_stargate(self.address_buffer_outgoing):
                # If we don't know the online status of the fan_gate or it is online.
                if self.fan_gate_online_status is None or self.fan_gate_online_status:
                    # send the locked symbols to the remote gate.
                    if self.send_to_remote_stargate(self.get_ip_from_stargate_address(self.address_buffer_outgoing, self.fan_gates), str(self.address_buffer_outgoing[0:self.locked_chevrons_outgoing]))[0]:
                        self.log.log(f'Sent to fan_gate: {self.address_buffer_outgoing[0:self.locked_chevrons_outgoing]}')
                        self.fan_gate_online_status = True  # set the online status to True
                    else:
                        self.fan_gate_online_status = False  # set the online status to False, to keep the dialing running more smoothly if the fan_gate is offline.

    def incoming_dialing(self):
        """
        This method handles the incoming dialing of the stargate. It's kept in it's own method so not to clutter up the update method too much.
        :return: Nothing is returned
        """
        # If there are dialed incoming symbols that are not yet locked and we are currently not dialing out.
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
                except KeyError:  # If we dialed more chevrons than the stargate can handle.
                    pass  # Just pass without activating a chevron.
                # Play the audio clip for incoming wormhole
                if self.locked_chevrons_incoming == 1:
                    self.audio.play_random_clip("IncomingWormhole")
                self.sleep(delay)  # if there's a delay, used it.
                self.last_activity_time = time()  # update the last_activity_time
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
        # If the centre_button_outgoing is active and all dialed symbols are locked.
        if self.centre_button_outgoing and (0 < len(self.address_buffer_outgoing) == self.locked_chevrons_outgoing):
            # If we did not dial a fan_gate, set the IP variable to True instead of an IP.
            if self.addrManager.valid_planet(self.address_buffer_outgoing) != 'fan_gate':
                self.fan_gate_incoming_IP = True
            # Try to send the centre button to the fan_gate:
            self.try_sending_centre_button()
            # Try to establish a wormhole
            if self.possible_to_establish_wormhole():
                self.log.log('Valid address is locked')
                self.wormhole = 'outgoing'
            else:
                self.log.log('Unable to establish a Wormhole!')
                self.shutdown(cancel_sound=False, wormhole_fail_sound=True)

        ## Incoming wormhole ##
        # If the centre_button_incoming is active and all dialed symbols are locked.
        elif self.centre_button_incoming and 0 < len(self.address_buffer_incoming) == self.locked_chevrons_incoming:
            # If the incoming wormhole matches the local address
            if self.address_buffer_incoming[0:-1] == self.local_stargate_address:
                self.wormhole = 'incoming'  # Set the wormhole state to activate the wormhole.
                self.log.log('Incoming address is a match!')
            else:
                self.log.log('Incoming address is NOT a match to Local Gate Address!')
                self.shutdown(cancel_sound=False, wormhole_fail_sound=True)


    def shutdown(self, cancel_sound=True, wormhole_fail_sound=False):
        """
        This method shuts down and resets the Stargate.
        :return:
        """

        self.log.log('Shutting down the gate...')

        # Play the cancel sound
        if cancel_sound:
            self.audio.sound_start('dialing_cancel')

        # Play the wormhole fail sound
        if wormhole_fail_sound:
            self.audio.sound_start('dialing_fail')

        # Turn off the chevrons
        self.chevrons.all_off()

        # Turn off the DHD lights
        self.dialer.hardware.clear_lights()

        # Release the stepper motor.
        self.ring.release()

        # Put the gate back in to an idle state
        self.initialize_gate_state_vars()

        self.log.log("Gate is idle.")

    def inactivity(self, seconds):
        """
        This functions checks if there has been more than the variable seconds of inactivity:
        :param seconds: The number of seconds of allowed inactivity
        :return: True if inactivity is detected, False if not
        """
        if not self.wormhole: #If we are in the dialing phase
            if self.last_activity_time: #If the variable is not None
                if (len(self.address_buffer_incoming) > 0) or (len(self.address_buffer_outgoing) > 0): # If there are something in the buffers
                    if (time() - self.last_activity_time) > seconds:
                        return True
        return False

    # TODO: Move to subspace
    def possible_to_establish_wormhole(self):
        """
        This is a method to help check if we are able to establish a wormhole or not.
        :return: Returns True if we can establish a wormhole, and False if not
        """
        # If the dialed address is valid
        if len(self.address_buffer_outgoing) > 0 and self.addrManager.valid_planet(self.address_buffer_outgoing) or \
            len(self.address_buffer_incoming) > 0 and self.addrManager.valid_planet(self.address_buffer_incoming):
            # If we dialed a fan_gate
            if self.addrManager.valid_planet(self.address_buffer_outgoing) == 'fan_gate':
                # If the dialed fan_gate is not online
                if not self.fan_gate_online_status:
                    self.log.log('The dialed fan_gate is NOT online!')
                    return False
                # If the dialed fan_gate is already busy, with an active wormhole or outgoing dialing is in progress.
                elif self.get_status_of_remote_gate(self.get_ip_from_stargate_address(self.address_buffer_outgoing, self.fan_gates)):
                    self.log.log('The dialed fan_gate is already busy!')
                    return False
            return True  # returns true if we can establish a wormhole
        return False  # returns false if we cannot establish a wormhole.

from time import sleep

from stargate_config import StargateConfig

class SymbolRing:
    """
    The dialing sequence.
    """

    def __init__(self, stargate):

        self.stargate = stargate
        self.log = stargate.log
        self.cfg = stargate.cfg
        self.audio = stargate.audio
        self.chevrons = stargate.chevrons
        self.base_path = stargate.base_path

        # Load the last known ring position
        self.position_store = StargateConfig(self.base_path, "ring_position.json")
        self.position_store.set_log(self.log)
        self.position_store.load()

        self.gate_symbol_count = 36

        # Initialize some state variables for Web UI
        self.direction = False
        self.steps_remaining = 0
        self.current_speed = False
        self.drive_status = "Stopped"

        # Constants for direction handling
        self.forward_direction = 0
        self.backward_direction = 1

        # What symbol is each Chevron aligned with?
        # Symbol positions starting from 0.

        # TODO: This needs some thinking: Where is symbol 0? Where is chevron 0? What order are the chevrons in?
        #           Do we need to re-map the symbol & chevron position maps on the LED Controller?

        self.chevron_positions = [
            0,
            5,
            9,
            13,
            17,
            21,
            24,
            28,
            32
        ]

    def get_status(self):
        return {
            "ring_position": self.get_position(),
            "direction": self.direction,
            "steps_remaining": self.steps_remaining,
            "current_speed": self.current_speed,
            "drive_status": self.drive_status
        }

    def move(self, steps, direction):
        """
        This method moves a symbol the desired number of steps in the desired direction and from it's last position, and
        updates the saved position with the new value.
        :param steps: the number of steps to move as int.
        :param direction: the direction to move. Must be either self.forward_direction or self.backward_direction
        :return: Nothing is returned
        """

        # Check that `direction` is valid
        if direction not in [ self.forward_direction, self.backward_direction ]:
            self.log.log("move() called with invalid direction")
            raise ValueError

        # Check that `steps` is valid/non-negative
        if steps < 0:
            self.log.log("move() called with negative steps")
            raise ValueError

        # Start the rolling ring sound
        self.audio.sound_start('rolling_ring')

        self.direction = direction
        self.steps_remaining = steps
        self.current_speed = self.cfg.get("stepper_speed_slow")

        #TODO: Consider caching the configs here?

        # Move the ring one step at at time
        for i in range(steps): # pylint: disable=unused-variable
            # Check if the gate is still running, if not, break out of the loop.
            if not self.stargate.running:
                break

            # Move the symbol one step
            # TODO: Kristian

            # Update the position in non-persistent memory
            self.update_position(1, direction)

            ## Speed control
            self.drive_status = "Constant Speed: Normal"
            sleep(self.current_speed)

        # After this move() is complete, save the position to persistent memory
        self.current_speed = False
        self.direction = False
        self.drive_status = "Stopped"
        self.save_position()

        self.audio.sound_stop('rolling_ring')  # stop the audio

    def calculate_steps(self, chevron_number, symbol_number):
        """
        Helper function to determine the needed number of steps to move symbol_number, to chevron
        :return: The number of steps to move is returned as an int.
        """

        # How many steps are needed:
        try:
            steps = self.chevron_positions[chevron_number] - ((self.get_position() + symbol_number) % self.gate_symbol_count )
        except KeyError: # If we dial more chevrons than the stargate can handle. Don't return any steps.
            return None

        if abs(steps) > self.gate_symbol_count / 2: # Check if distance is more than half a revolution
            new_steps = (self.gate_symbol_count - abs(steps)) % self.gate_symbol_count # Reduce with half a revolution, and flips the direction
            if steps > 0: # if the direction was forward, flip the direction
                new_steps = new_steps * -1
            return new_steps
        return steps

    def move_symbol_to_chevron(self, symbol_number, chevron_number ):

        """
        This function moves the symbol_number to the desired chevron. It also updates the ring position file.
        :param symbol_number: the number of the symbol
        :param chevron: the number of the chevron
        :return: nothing is returned
        """
        calc_steps = self.calculate_steps(chevron_number, symbol_number) # calculate the steps

        # Choose which ring direction mode to use
        if self.cfg.get("dialing_ring_direction_mode") is False:
            ## Option one. This will move the symbol the shortest direction, cc or ccw.
            if calc_steps: # If not None
                ## Determine the direction
                if calc_steps >= 0:  # If steps is positive move forward
                    direction = self.forward_direction
                else:  # if steps is negative move backward
                    calc_steps = abs(calc_steps)
                    direction = self.backward_direction

                self.move(calc_steps, direction) # move the ring the calc_steps steps.
        else:
            ## Option two. This will move the symbol the longest direction, cc or ccw.
            if calc_steps: # If not None
                if calc_steps >= 0:
                    calc_steps = (self.cfg.get("stepper_one_revolution_steps") - calc_steps)
                    direction = self.backward_direction
                    self.move(calc_steps, direction)  # move the ring, but the long way in the opposite direction.
                else:
                    calc_steps = self.cfg.get("stepper_one_revolution_steps") - abs(calc_steps)
                    direction = self.forward_direction
                    self.move(calc_steps, direction)  # move the ring, but the long way in the opposite direction.

    def get_position(self):
        return self.position_store.get('ring_position')

    def update_position(self, steps, direction):
        if direction == self.forward_direction:
            offset = steps
        else: # Backward
            offset = steps * -1

        new_position = (self.get_position() + offset) % self.cfg.get("stepper_one_revolution_steps")
        self.position_store.set_non_persistent('ring_position', new_position)

    def save_position(self):
        self.position_store.save()

    def zero_position(self):
        self.log.log("Setting Ring Position: 0")
        self.position_store.set_non_persistent('ring_position', 0)
        self.save_position()

    def release(self):
        # TODO: Extinguish all lights
        pass

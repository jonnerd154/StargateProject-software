from time import sleep

from stargate_config import StargateConfig
from symbol_ring_homing_manager import SymbolRingHomingManager

class SymbolRing:
    """
    The dialing sequence.
    1251 is the normal steps needed for one revolutions of the gate as set in self.total_steps.
    # A range of 32 is approximately one symbol movement.
    """

    def __init__(self, stargate):

        self.stargate = stargate
        self.log = stargate.log
        self.cfg = stargate.cfg
        self.audio = stargate.audio
        self.chevrons = stargate.chevrons
        self.base_path = stargate.base_path

        # The symbol positions on the symbol ring
        self.symbol_step_positions = {
            1: 0,
            2: 32,
            3: 64,
            4: 96,
            5: 128,
            6: 160,
            7: 192,
            8: 224,
            9: 256,
            10: 288,
            11: 320,
            12: 352,
            13: 384,
            14: 416,
            15: 448,
            16: 480,
            17: 512,
            18: 544,
            19: 576,
            20: 608,
            21: 640,
            22: 672,
            23: 704,
            24: 736,
            25: 768,
            26: 800,
            27: 832,
            28: 864,
            29: 896,
            30: 928,
            31: 960,
            32: 992,
            33: 1024,
            34: 1056,
            35: 1088,
            36: 1120,
            37: 1152,
            38: 1184,
            39: 1216,
        }

        # The chevron positions on the stargate
        self.chevron_step_positions = {
            1: 139,
            2: 278,
            3: 417,
            4: 834,
            5: 973,
            6: 1112,
            7: 0,
            8: 556,
            9: 695,
        }
        ## --------------------------

        # Inititialize some hardware
        self.stepper = stargate.electronics.get_stepper()
        self.forward_direction = stargate.electronics.get_stepper_forward()
        self.backward_direction = stargate.electronics.get_stepper_backward()

        # Load the last known ring position
        self.position_store = StargateConfig(self.base_path, "ring_position", stargate.galaxy_path)
        self.position_store.set_log(self.log)
        self.position_store.load()

        ## Initialize the Homing Manager
        self.homing_manager = SymbolRingHomingManager( self.stargate )

        # Initialize some state variables for Web UI
        self.direction = False
        self.steps_remaining = 0
        self.current_speed = False
        self.drive_status = "Stopped"

        # Release the ring for safety
        self.release()

    def get_status(self):
        return {
            "ring_position": self.get_position(),
            "direction": self.direction,
            "steps_remaining": self.steps_remaining,
            "current_speed": self.current_speed,
            "drive_status": self.drive_status
        }

    @staticmethod
    def find_offset(position, max_steps):
        """
        This static function finds the offset of position as compared to max_steps for when the position is in the home position.
        :param position: The current real position of the ring
        :param max_steps: the total_max steps for one revolution
        :return: The offset is returned. The value is positive for CW and negative for CCW.
        """
        if 5 < position < (max_steps - 5):  # if the position is between 5 and 5 lower than max.
            if position < (max_steps // 2):  # If the offset is positive/counter clock wise.
                return position * -1
            # if the offset is negative/clock wise.
            return max_steps - position
        return 0

    def move(self, steps, direction):
        """
        This method moves the stepper motor the desired number of steps in the desired direction and updates the
        saved position with the new value. This method does NOT release the stepper. Do this with the release method.
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
        for i in range(steps):
            # Check if the gate is still running, if not, break out of the loop.
            if not self.stargate.running:
                break

            # Move the stepper one step
            stepper_drive_mode = self.stargate.electronics.get_stepper_drive_mode(self.cfg.get("stepper_drive_mode"))
            self.stepper.onestep(direction=direction, style=stepper_drive_mode)
            self.steps_remaining -= 1

            ## acceleration
            try:
                if i < self.cfg.get("stepper_acceleration_steps"):
                    self.current_speed -= (self.cfg.get("stepper_speed_slow") - self.cfg.get("stepper_speed_normal")) / self.cfg.get("stepper_acceleration_steps")
                    self.drive_status = "Accelerating"
                    sleep(self.current_speed)
                ## deceleration
                elif i > (steps - self.cfg.get("stepper_acceleration_steps")):
                    self.current_speed += (self.cfg.get("stepper_speed_slow") - self.cfg.get("stepper_speed_normal")) / self.cfg.get("stepper_acceleration_steps")
                    self.drive_status = "Decelerating"
                    sleep(self.current_speed)
                ## slow without acceleration when short distance
                elif steps < self.cfg.get("stepper_acceleration_steps"):
                    self.current_speed = self.cfg.get("stepper_speed_normal")
                    self.drive_status = "Constant Speed: Slow"
                    sleep(self.current_speed)
                else:
                    self.drive_status = "Constant Speed: Normal"
            except ValueError:
                # If we've tried to sleep for negative time
                pass

            # Update the position in non-persistent memory
            self.update_position(1, direction)

            # Checks if the ring is in the home position, and zeros the cached value if so
            self.homing_manager.in_move_calibrate()

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
            steps = self.chevron_step_positions[chevron_number] - ((self.get_position() + self.symbol_step_positions[symbol_number]) % self.cfg.get("stepper_one_revolution_steps"))
        except KeyError: # If we dial more chevrons than the stargate can handle. Don't return any steps.
            return None

        if abs(steps) > self.cfg.get("stepper_one_revolution_steps") / 2: # Check if distance is more than half a revolution
            new_steps = (self.cfg.get("stepper_one_revolution_steps") - abs(steps)) % self.cfg.get("stepper_one_revolution_steps") # Reduce with half a revolution, and flips the direction
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

        """
        This method releases the stepper so that there are no power holding it in position. The stepper is free to roll.
        :return: Nothing is returned.
        """
        sleep(0.4)
        self.stepper.release()

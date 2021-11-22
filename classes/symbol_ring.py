from time import sleep

from stargate_config import StargateConfig
from hardware_detection import HardwareDetector
from homing import SymbolRingHomingManager

class SymbolRing:
    """
    The dialing sequence.
    One iteration is 16 micro steps (as printed from the onestep function when stepper.DOUBLE. But for unknown reasons
    the first step is 8 micro steps..) This is set in the self.micro_steps variable.
    1251 is the normal steps needed for one revolutions of the gate as set in self.total_steps.
    # A range of 32 is approximately one symbol movement.
    """

    def __init__(self, stargate):

        self.log = stargate.log
        self.cfg = stargate.cfg
        self.audio = stargate.audio
        self.chevrons = stargate.chevrons
        self.base_path = stargate.base_path

        # TODO: Move to cfg
        self.enableStepper = False
        self.stepper_drive_mode = "double"
        self.total_steps = 1250 # Old value: 1251
        self.micro_steps = 16
        self.stepper_pos = 0
        self.normal_speed = 0.002
        self.slow_speed = 0.01
        self.initial_speed = 0.01  # the initial speed
        self.acceleration_length = 40  # the number of steps used for acceleration
        self.ringDirectionModeLongest = True

        # The symbols position on the symbol ring
        self.symbol_step_positions = {1: 0, 2: 32, 3: 64, 4: 96, 5: 128, 6: 160, 7: 192, 8: 224, 9: 256, 10: 288, 11: 320, 12: 352, 13: 384, 14: 416, 15: 448, 16: 480, 17: 512, 18: 544, 19: 576, 20: 608, 21: 640, 22: 672, 23: 704, 24: 736, 25: 768, 26: 800, 27: 832, 28: 864, 29: 896, 30: 928, 31: 960, 32: 992, 33: 1024, 34: 1056, 35: 1088, 36: 1120, 37: 1152, 38: 1184, 39: 1216}
        # The chevrons position on the stargate.
        self.chevron_step_positions = {1: 139, 2: 278, 3: 417, 4: 834, 5: 973, 6: 1112, 7: 0, 8: 556, 9: 695}

        ## --------------------------

        self.stepper = stargate.electronics.get_stepper()
        self.forwardDirection = stargate.electronics.get_stepper_forward()
        self.backwardDirection = stargate.electronics.get_stepper_backward()
        self.stepperDriveMode = stargate.electronics.get_stepper_drive_mode(self.stepper_drive_mode)

        # Load the last known ring position
        self.position_store = StargateConfig(self.base_path, "ring_position.json")

        ## Initialize the Homing Manager
        self.homingManager = SymbolRingHomingManager(stargate, self)

        # Release the ring for safety
        self.release()


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
            else:  # if the offset is negative/clock wise.
                return max_steps - position
        else:
            return 0

    # TODO: Move to a stepper/hardware manager
    def move_raw_one_step(self, direction, style):
        self.stepper.onestep(direction=direction, style=style)

    def move(self, steps, direction=False):
        """
        This method moves the stepper motor the desired number of steps in the desired direction and updates the
        self.stepper_pos with the new value. This method does NOT release the stepper. Do this with the release method.
        Nor does this method update the "ring_position". Do this with the ring_position method.
        :param steps: the number of steps to move as int. Negative is backward(ccw) and positive is forward (cw)
        :return: Nothing is returned
        """
        ## Set the direction ##
        if not direction:
            if steps >= 0:  # If steps is positive move forward
                direction = self.forwardDirection
            else:  # if steps is negative move backward
                steps = abs(steps)
                direction = self.backwardDirection

        current_speed = self.initial_speed

        # Move the ring
        self.audio.sound_start('rolling_ring')  # play the audio movement
        stepper_micro_pos = 0
        for i in range(steps):
            self.move_raw_one_step(direction, style=self.stepperDriveMode)
            stepper_micro_pos += 8
            self.stepper_pos = (stepper_micro_pos // self.micro_steps) % self.total_steps # Update the self.stepper_pos value as the ring moves. Will have a value from 0 till self.total_steps = 1250.

            ## acceleration
            if i < self.acceleration_length:
                current_speed -= (self.slow_speed - self.normal_speed) / self.acceleration_length
                sleep(current_speed)
            ## deceleration
            elif i > (steps - self.acceleration_length):
                current_speed += (self.slow_speed - self.normal_speed) / self.acceleration_length
                sleep(current_speed)
            ## slow without acceleration when short distance
            elif steps < self.acceleration_length:
                current_speed = self.normal_speed
                sleep(current_speed)

        self.audio.sound_stop('rolling_ring')  # stop the audio

    def calculate_steps(self, chevron_number, symbol_number):
        """
        Helper function to determine the needed number of steps to move symbol_number, to chevron
        :return: The number of steps to move is returned as an int.
        """
        # How many steps are needed:
        try:
            steps = self.chevron_step_positions[chevron_number] - ((self.get_position() + self.symbol_step_positions[symbol_number]) % self.total_steps)
        except KeyError: # If we dial more chevrons than the stargate can handle. Don't return any steps.
            return None

        if abs(steps) > self.total_steps / 2: # Check if distance is more than half a revolution
            new_steps = (self.total_steps - abs(steps)) % self.total_steps # Reduce with half a revolution, and flips the direction
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
        if ( self.ringDirectionModeLongest is False ):
            ## Option one. This will move the symbol the shortest direction, cc or ccw.
            if calc_steps: # If not None
                self.move(calc_steps) # move the ring the calc_steps steps.
        else:
            ## Option two. This will move the symbol the longest direction, cc or ccw.
            if calc_steps: # If not None
                if calc_steps >= 0:
                    self.move((self.total_steps - calc_steps) * -1)  # move the ring, but the long way in the opposite direction.
                else:
                    self.move((self.total_steps - abs(calc_steps)))  # move the ring, but the long way in the opposite direction.

        # Update and save the ring position.
        self.set_position()
        self.save_position()

    def get_position(self):
        return self.position_store.get('ring_position')

    def set_position(self):
        calculatedPosition = ( (self.stepper_pos + self.get_position() ) % self.total_steps) + self.homingManager.offset
        self.position_store.set_non_persistent('ring_position', calculatedPosition)

    def save_position(self):
        self.position_store.save()

    def release(self):

        """
        This method releases the stepper so that there are no power holding it in position. The stepper is free to roll.
        :return: Nothing is returned.
        """
        sleep(0.4)
        self.stepper.release()

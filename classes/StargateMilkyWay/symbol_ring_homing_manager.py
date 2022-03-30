
class SymbolRingHomingManager:

    def __init__(self, stargate):

        self.stargate = stargate
        self.log = stargate.log
        self.cfg = stargate.cfg

        # This SymbolRingHomingManager object is initialized in the SymbolRing initializer,
        # and therefore stargate.ring is not yet available
        self.ring = None # Gets set after initialization of the SymbolRing object.

        # Retrieve the configurations
        self.auto_homing_enabled = self.cfg.get("stepper_auto_homing_enabled")
        self.auto_homing_threshold = self.cfg.get("stepper_auto_homing_threshold")

    def in_move_calibrate( self ):
        if self.auto_homing_enabled and self.is_at_home():
            actual = 0
            expected = self.stargate.ring.get_position()
            error = actual - expected

            if error > self.stargate.ring.total_steps // 2:
                error = (self.stargate.ring.total_steps - error)*-1

            self.log.log(f'HOME detected! Expected:           {expected}')
            self.log.log(f'               Actual:             {actual}')
            self.log.log(f'               Accumulated Error : {error}')
            self.log.log('Setting Zero-Position.')
            self.ring.zero_position()

    def is_at_home(self):
        if self.stargate.electronics.homing_supported():
            sensor_voltage = self.stargate.electronics.get_homing_sensor_voltage()
            if sensor_voltage < self.auto_homing_threshold:  # if the ring is in the "home position"
                return True
        return False

    # def find_home(self):
    #     self.audio.sound_start('rolling_ring')  # play the audio movement
    #     for i in range(self.ring.steps):
    #         if self.ring.motor_hardware_mode > 0:
    #             stepper_micro_pos = self.ring.move_raw_one_step() + 8 # this line moves the motor.
    #         else:
    #             try:
    #                 stepper_micro_pos = stepper_micro_pos + 8
    #             except NameError:
    #                 stepper_micro_pos = 8
    #         self.stepper_pos = (stepper_micro_pos // self.micro_steps) % self.total_steps # Update the self.stepper_pos value as the ring moves. Will have a value from 0 till self.total_steps = 1250.
    #
    #         ## homing sensor ##
    #         try:
    #             if self.electronics.homing_enabled(): # If the jumper for the sensor is present
    #                 sensor_voltage = self.electronics.get_homing_sensor_voltage()
    #                 if sensor_voltage < self.homing_sensor_home_threshold:  # if the ring is in the "home position"
    #                     # print('HOME detected!')
    #                     actual_position = (self.stepper_pos + self.saved_pos) % self.total_steps
    #                     self.offset = (self.find_offset(actual_position, self.total_steps))
    #         except:
    #             pass
    #
    #         ## acceleration
    #         if i < acceleration_length:
    #             current_speed -= (slow_speed - normal_speed) / acceleration_length
    #             sleep(current_speed)
    #         ## de acceleration
    #         elif i > (steps - acceleration_length):
    #             current_speed += (slow_speed - normal_speed) / acceleration_length
    #             sleep(current_speed)
    #         ## slow without acceleration when short distance
    #         elif steps < acceleration_length:
    #             current_speed = normal_speed
    #             sleep(current_speed)
    #     self.audio.sound_stop('rolling_ring')  # stop the audio

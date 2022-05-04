from time import sleep

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
        self.one_revolution_steps = self.cfg.get("stepper_one_revolution_steps")

    def in_move_calibrate( self ):
        # expected = self.stargate.ring.get_position()
#         self.log.log(f'               Expected:             {expected}')
#         error = 0
#         if self.auto_homing_enabled and self.is_at_home():
#             actual = 0
#             expected = self.stargate.ring.get_position()
#             error = actual - expected
# 
#             if error > self.one_revolution_steps // 2:
#                 error = (one_revolution_steps - error)*-1
# 
# #             self.ring.steps_remaining += error
#             
#             self.log.log(f'HOME detected! Expected:           {expected}')
#             self.log.log(f'               Actual:             {actual}')
#             self.log.log(f'               Accumulated Error : {error}')
#             self.log.log('Setting Zero-Position.')
#             self.ring.zero_position()
#           
#         return error
        return 0
            
    def is_at_home(self):
        if self.stargate.electronics.homing_supported():
            sensor_voltage = self.stargate.electronics.get_homing_sensor_voltage()
            if sensor_voltage < self.auto_homing_threshold:  # if the ring is in the "home position"
                return True
        return False

    def find_home(self):
    
        '''
          This is a really simple stand-alone homing implementation. It would be fun
          to implement functionality to check/compensate for backlash, and
          to start from the current understanding of where home is, and more intelligently
          search for home, rather than the current brute force method of
          
             "move clockwise 1.1x rotations until we find home"
             
          Some comments are below to help guide that effort in the future.
             
          ...gotta start somewhere. FISI!
          
        '''
        
        if not self.stargate.electronics.homing_supported():
            message = "Current Hardware does not support self-homing"
            self.log.log(message)
            return { 'success': False, 'message': message }
            
        self.log.log("Self-homing: Start")
        
        # Check if we're already at home
        if self.is_at_home():
            self.log.log("Self-homing: Ring already at home.")
            return { 'success': False, 'message': "" } 
          
        # TODO
        # - Move Earth to symbol 7, which should bring us home
        # - Overshoot by 2 symbols
        # - If home still isn't found, continue moving in the same direction up to 1.1 revolutions total
          
        # Move the ring *at most* 1.1 full revolutions
        max_steps = int(self.one_revolution_steps * 1.1)
        self.stargate.audio.sound_start('rolling_ring')  # play the audio movement
        for i in range(max_steps):
            
            # Check the homing sensor
            if self.is_at_home():
                message = "HOME detected!"
                self.log.log("Self-homing: " + message)
                self.ring.zero_position()
                self.ring.release()
                self.stargate.audio.sound_stop('rolling_ring')  # stop the audio   
                message = "Current Hardware does not support self-homing"
                sleep(0.75)
                return { 'success': True, 'message': ""}
                        
            # Move one step forward at Normal speed
            direction = self.stargate.electronics.get_stepper_forward()
            stepper_drive_mode = self.stargate.electronics.get_stepper_drive_mode(self.cfg.get("stepper_drive_mode"))
            self.stargate.electronics.stepper.onestep(direction=direction, style=stepper_drive_mode)
            sleep(self.cfg.get("stepper_speed_normal"))
         
        message = "Failed to find home"
        self.stargate.audio.sound_stop('rolling_ring')  # stop the audio   
        return { 'success': False, 'message': message}
        

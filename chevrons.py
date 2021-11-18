# You can change or the values in this file to match your setup. This file should not be overwritten with an automatic update
# The first number in the parenthesis is the gpio led number and the second value is the motor number.
from classes.CHEVRON import Chevron
from classes.HardwareDetector import HardwareDetector

hwDetector = HardwareDetector()
mode = hwDetector.getMotorHardwareMode()

chevrons = {1: Chevron(6, 7, mode),
            2: Chevron(13, 8, mode),
            3: Chevron(19, 11, mode),
            4: Chevron(21, 3, mode),
            5: Chevron(16, 4, mode),
            6: Chevron(20, 5, mode),
            7: Chevron(26, 6, mode),
            8: Chevron(None, 10, mode),
            9: Chevron(None, 9, mode)}

#chevrons = {1: Chevron(21, 3),
#            2: Chevron(16, 4),
#            3: Chevron(20, 5),
#            4: Chevron(26, 6),
#            5: Chevron(6, 7),
#            6: Chevron(13, 8),
#            7: Chevron(19, 9),
#            8: Chevron(None, 10),
#            9: Chevron(None, 11)}

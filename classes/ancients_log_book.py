import sys
from datetime import datetime
import threading

# pylint: disable=too-few-public-methods

class AncientsLogBook:

    def __init__(self, base_path, log_file, print_to_console = True):

        self.print_to_console = print_to_console

        self.gate_log = log_file
        self.log_dir = base_path + "/logs" #No trailing slash

    def log(self, msg, print_to_console_override = False):
        """
        This functions logs the string_for_logging to the end of file.
        :param file: the file name as a string. It will be placed in the same folder as the file from where this function is run.
        :param msg: the entry for the log, as a string. The timestamp will be prepended automatically.
        :return: Nothing is returned.
        """

        with open(self.log_dir +"/"+ self.gate_log, 'a+', encoding="utf8") as log_file:
            timestamp = datetime.now().replace(microsecond=0)
            log_line = f'\n[{timestamp}]\t{msg}'
            log_file.write(log_line)

        if (self.print_to_console and not print_to_console_override):
            # Some magic to prevent threads from messing up newlines on the console print
            print_lock = threading.Lock()
            with print_lock:
                print(log_line, end='\r')
                sys.stdout.flush()

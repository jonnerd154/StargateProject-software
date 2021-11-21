import pwd, grp
from os import stat
from pathlib import Path
from datetime import datetime

class AncientsLogBook:

    def __init__(self, base_path, log_file, printToConsole = True):

        self.printToConsole = printToConsole

        self.gateLog = log_file
        self.logDir = base_path + "/logs" #No trailing slash

        # TODO: Open the log file here, and do any creation/permission repairs.
        #    log() should only be appending to the file.

        pass

    def log(self, str, printToConsoleOverride = False):
        """
        This functions logs the string_for_logging to the end of file.
        :param file: the file name as a string. It will be placed in the same folder as the file from where this function is run.
        :param string_for_logging: the entry for the log, as a string. The timestamp will be prepended automatically.
        :return: Nothing is returned.
        """

        with open(self.logDir +"/"+ self.gateLog, 'a') as logFile:
            logLine = '\n' + f'[{datetime.now().replace(microsecond=0)}] \t {str}'
            logFile.write(logLine)

        if (self.printToConsole and not printToConsoleOverride):
            print(logLine)

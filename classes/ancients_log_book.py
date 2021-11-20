class AncientsLogBook:

    def __init__(self, log_file, printToConsole = True):

        self.printToConsole = printToConsole

        self.gateLog = log_file

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
        import pwd, grp
        from os import stat
        from pathlib import Path
        from datetime import datetime
        root_path = Path(__file__).parent.absolute()
        with open(Path.joinpath(root_path, self.gateLog), 'a') as sg1log:
            logLine = '\n' + f'[{datetime.now().replace(microsecond=0)}] \t {str}'
            sg1log.write(logLine)
        ## If the owner and group of the file is wrong, fix it.
        # get the user ID and group ID of the owner of this file (__file__). (In most instances this would result in the UID 1001 for the sg1 user.

        # TODO: Not work on MacOS...commenting out for now

        # uid = pwd.getpwnam(pwd.getpwuid(stat(__file__).st_uid).pw_name).pw_uid
        # gid = grp.getgrnam(pwd.getpwuid(stat(__file__).st_uid).pw_name).gr_gid
        # if stat(Path.joinpath(root_path, file)).st_uid != uid: # If the user is wrong
        #     os.chown(str(root_path / file), uid, gid) # Change the owner and group of the file.

        if (self.printToConsole and not printToConsoleOverride):
            print(logLine)

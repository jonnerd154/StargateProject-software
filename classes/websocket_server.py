import threading
import subprocess

# pylint: disable=consider-using-with

class LogTailServerWrapper(threading.Thread):
    def __init__(self, log_path, port):
        self.stdout = None
        self.stderr = None
        threading.Thread.__init__(self)

        self.process = None
        self.log_path = log_path
        self.port = port

    def run(self):
        self.process = subprocess.Popen(['python3', 'log_server.py', self.log_path, self.port],
                             shell=False)

    def terminate(self):
        self.process.kill()

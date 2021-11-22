import os
import json
import threading

from http.server import SimpleHTTPRequestHandler

class StargateWebServer(SimpleHTTPRequestHandler):
 
    def translate_path(self, path):
        fullpath = "/home/sg1/sg1/web" + path
        return fullpath

#   def translate_path(self, path):
#         path = SimpleHTTPRequestHandler.translate_path(self, path)
#         relpath = os.path.relpath(path, os.getcwd())
#         fullpath = os.path.join('web', relpath)
#         return fullpath

    def translate_path(self, path):
        path = SimpleHTTPRequestHandler.translate_path(self, path)
        relpath = os.path.relpath(path, os.getcwd())
        fullpath = os.path.join('web', relpath)
        return fullpath
        
        
    def do_GET(self):
        fullPath = self.translate_path(self.path)
        if fullPath:
            try:
                with open(fullPath, 'rb') as file: 
                    self.wfile.write(file.read()) # Read the file and send the contents     
            except:
                pass
                
#         self.send_response(200)
#         self.send_header("Content-type", "text/html")
#         self.end_headers()
#         self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
#         self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
#         self.wfile.write(bytes("<p>Thread: %s</p>" % threading.currentThread().getName(), "utf-8"))
#         self.wfile.write(bytes("<p>Thread Count: %s</p>" % threading.active_count(), "utf-8"))
#         self.wfile.write(bytes("<body>", "utf-8"))
#         self.wfile.write(bytes("<p>This is an example web server.</p>", "utf-8"))
#         self.wfile.write(bytes("</body></html>", "utf-8"))
#         
        
        
    def do_POST(self):
        # For debugging:
        print('POST PATH: {}'.format(self.path))
        if self.path == '/shutdown':
            os.system('systemctl poweroff')
            self.send_response(200, 'OK')
            return

        if self.path == '/reboot':
            os.system('systemctl reboot')
            self.send_response(200, 'OK')
            return

        content_len = int(self.headers.get('content-length', 0))
        body = self.rfile.read(content_len)
        data = json.loads(body)
        print('POST DATA: {}'.format(data))

        if self.path == '/update':
            if data['action'] == "chevron_cycle":
                self.stargate.chevrons.get(int(data['chevron_number'])).cycle_outgoing()
        

        # For debugging
        # print('POST data: {}'.format(data))
#         StargateWebServer.logic.execute_command(data)
        self.send_response(200, 'OK')
        self.end_headers()
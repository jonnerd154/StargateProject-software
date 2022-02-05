import sys
import time
import asyncio
import websockets

class LogTailServer():
    # pylint: disable=too-few-public-methods

    def __init__(self):

        loop = asyncio.get_event_loop()

        async def tail(websocket, path): # pylint: disable=unused-argument
            try:
                with open(file_path, 'rt') as file:
                    sleep = None

                    file.seek (0, 2)           # Seek @ EOF
                    fsize = file.tell()        # Get Size
                    file.seek (max (fsize-1024, 0), 0) # Set pos @ last n chars

                    while True:

                        for line in file.readlines():
                            if line:
                                await websocket.send(line.strip())

                        if sleep:
                            time.sleep(0.04)
            except:
                print("Client disconnected.  Do cleanup")
                raise


        tail_server = websockets.serve(tail, '', port)
        loop.run_until_complete(tail_server)
        loop.run_forever()

file_path = sys.argv[1]
port = str(sys.argv[2])
log_tail_server = LogTailServer()

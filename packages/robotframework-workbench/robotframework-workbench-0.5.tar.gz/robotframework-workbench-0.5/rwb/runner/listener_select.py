'''listener.py

This implements the classes used as the endpoint of a SocketListener
(see socket_listener.py). 

RemoteRobotListener is the class that should be instantiated to listen
for results from the SocketListener. 

'''

import SocketServer
import StringIO
import Tkinter as tk
import json
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
import socket
import select

class JSONSocketServer(object):
    backlog = 256
    buffsize = 2048
    sleep = 1
    def __init__(self, app, callback, host="localhost", port=8910):
        self._callback = callback
        self.port = port
        self.app = app
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.server.bind((host, port)) 
        self.server.listen(self.backlog) 
        self.input = [self.server] 
        self.poll()
        self.buffer = {}

    def callback(self, data):
        deserialized_json = json.loads(data)
        self._callback(*deserialized_json)

    def poll(self):
        inputready,outputready,exceptready = select.select(self.input,[],[],0) 

        for s in inputready: 

            if s == self.server: 
                # handle the server socket 
                client, address = s.accept() 
                self.input.append(client) 
                self.buffer[client] = ""

            else: 
                # handle all other sockets 
                data = s.recv(self.buffsize) 
                if data: 
                    # we read some data. Now, call the callback for 
                    # each complete line of data
                    self.buffer[s] += data
                    lines = self.buffer[s].split("\n")
                    self.buffer[s] = lines.pop()
                    for line in lines:
                        self.callback(line)
                else: 
                    s.close() 
                    self.input.remove(s) 
                    del self.buffer[s]
#        self.app.after(self.sleep, self.poll)
        self.app.after_idle(self.app.after, 1, self.poll)


# for backwards compatibility with older code...
# (old. HA! this isn't even at version 1.0 yet!)
class RemoteRobotListener(JSONSocketServer):
    pass

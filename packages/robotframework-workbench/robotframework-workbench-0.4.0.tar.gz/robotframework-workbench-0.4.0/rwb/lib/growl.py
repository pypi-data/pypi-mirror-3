import gntp.notifier

import SocketServer
import socket
import json

class ListenerServer(SocketServer.TCPServer):
    """Implements a simple line-buffered socket server"""
    allow_reuse_address = True
    def __init__(self, server_address, RequestHandlerClass):
        SocketServer.TCPServer.__init__(self, server_address, RequestHandlerClass)
#        self.callback = callback

class ListenerHandler(SocketServer.StreamRequestHandler):
    def growl(self, msg):
        print "msg:", msg
        growl = gntp.notifier.GrowlNotifier(
            applicationName = "Robot",
            notifications = ["New Updates", "New Messages"],
            defaultNotifications = ["New Messages"],
            hostname = "P-QA-DSK-BOAKL"
            )
        growl.notify(
            noteTYpe = "New Messages",
            title="You have a new message",
            description = msg,
            priority = 1,
            )
        gntp.notifier.mini(msg)
#        gntp.notifier.mini("my work here is done: %s" % str(self.stats))

    def handle(self):
        self.stats = None
        f = self.request.makefile('r')
        while True:
            line = f.readline()
            if not line: break
            j = json.loads(line)
            cmd = j[0]
            if cmd == "end_suite":
                self.stats = j[2]
            print "=>", j
            import sys; sys.stdout.flush()
        print "done!", self.stats
        msg = "My work here is done: %s" % self.stats["status"]
        self.growl(msg)
        import sys; sys.stdout.flush()

port = 8910
server = ListenerServer(("",port), ListenerHandler)
print "serving..."; import sys; sys.stdout.flush()
server.serve_forever()
print "done serving forever"


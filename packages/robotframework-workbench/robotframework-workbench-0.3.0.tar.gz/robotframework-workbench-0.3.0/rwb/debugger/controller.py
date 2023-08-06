'''DebugController

'''

from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from robot.libraries.BuiltIn import BuiltIn
import robot.errors

class DebugController(object):
    # global, so we can create a single XMLRPC server that lasts for
    # the life of the suite
    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    def __init__(self, listener, port=8911):
        self.listener = listener
        self.port=8911
        self.state = "continue-to-error"
        print "DebugController opening server on port", port; import sys; sys.stdout.flush()
        self.server = SimpleXMLRPCServer(("localhost", int(port)), 
                                   SimpleXMLRPCRequestHandler, 
                                   allow_none=True,
                                   logRequests=False)
        self.server.register_function(self._ping, "ping")
        self.server.register_function(self._get_variables, "get_variables")
        self.server.register_function(self._run_keyword, "run_keyword")
        self.server.register_function(self.do_command, "do_command")

    def do_command(self, command):
        if command in ("continue","continue-to-kw","continue-to-test","stop","fail-test", "break-on-error"):
            self.state = command
            print "I just set the state to '%s'" % command ; import sys; sys.stdout.flush()
        elif command == "get_variables":
            self._get_variables()
        elif command == "run_keyword":
            self._run_keyword()
        else:
            raise(Exception("unsupported command '%s'" % command))            

    def start_keyword(self, name, attrs): pass
    def end_keyword(self, name, attrs): pass
    def start_test(self, name, attrs): pass
    def end_test(self, name, attrs): 
        t = BuiltIn().get_test()
        print "dir of BuiltIn()..."
        print dir(BuiltIn())
        print "end_test; status is", t.status
        
    def start_suite(self, name, attrs): pass
    def end_suite(self, name, attrs): pass

    def end_keyword(self, name, attrs):
        if attrs["status"] == "FAIL" and self.state == "break-on-error":
            self.breakpoint("break on failed keyword")

    def log_message(self, message):
        if (message["message"].startswith(":break:")):
            # test has a "breakpoint" command (more correctly,
            # test issued a 'log | :break: | DEBUG' command)
            self.state = "break"
            self.breakpoint()

    def breakpoint(self, message="breakpoint"):
        # This method is intended to be interpreted by a remote
        # listener. This keyword will block until the remote listener
        # sends back a command to continue or fail (via the XMLRPC
        # methods "stop", "fail_test", "fail_suite"  or "resume"
        # "fail_suite" isn't working right now :-(
        BuiltIn().log(message, "DEBUG")

        # this enters into a mini event loop, handling requests
        # from the remote listener. N.B. self.state is set by the
        # various commands called by the remote client
        while True:
            try:
                import sys
                sys.stdout=sys.__stdout__
                import traceback
                print "\n*** traceback:"
                for line in traceback.extract_stack():
                    print line
                t = BuiltIn().get_test()
                print "t:", t, t.__class__, type(t)
                print "t.run_errors:", t.run_errors, t.run_errors.__class__
                print "t.keywords:", t.keywords, t.keywords.__class__
                print "status:", t.status
                import sys; sys.stdout.flush()
                self.server.handle_request()
                print "after handling a request, the state is", self.state; import sys; sys.stdout.flush()
                if self.state in ("continue", "break-on-error", "break-on-test", "break-on-keyword"): 
                    break

                if self.state == "fail-test":
                    t = BuiltIn().get_test()
                    print "fail-test; status was", t.status
                    t.status="FAIL"
                    s = BuiltIn().get_suite()
                    print "fail-test; suite status was", s.status
                    s.status="FAIL"
                    print "fail-test!"; import sys; sys.stdout.flush()
                    break
#                    raise AssertionError("debug fail")
#                    BuiltIn().fail("debug fail")

                if self.state == "fail-suite":
                    s = BuiltIn().get_suite()
                    s.status="FAIL"
                    break
#                    error = robot.errors.ExecutionFailed("debug quit")
#                    error = AssertionError("killed by the debugger")
#                    error.ROBOT_EXIT_ON_FAILURE = True
#                    raise error
                if self.state == "stop":
                    BuiltIn().fatal_error("killed by the debuggerz")
                    
            except Exception, e:
                raise

#     def _continue_to_kw(self):
#         self.state = "continue-to-kw"
#     def _continue_to_test(self):
#         self.state = "continue-to-test"
#     def _resume(self):
#         self.state = "continue"
#     def _stop(self, message="stopped by debugger"):
#         self.state = "fail-suite"

#     def _fail_test(self, message="test failed via debugger"):
#         self.state = "fail-test"

    def _run_keyword(self, *args):
        BuiltIn().log("debug: " + " ".join(args), "DEBUG")
        return BuiltIn().run_keyword(*args)

    def _get_variables(self):
        variables = BuiltIn().get_variables()
        return dict(variables)

    def _ping(self):
        return "ping!"



import sys
from robot import LOGGER

# Robot expects the class to be the same as the filename, so
# we can't use the convention of capitalizing the class name
class null_console_listener:
    '''Turn off the default listener'''
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self, *args):
        print "null listener initialized. w00t!"
#        LOGGER.disable_automatic_console_logger()
        LOGGER._loggers.remove_first_regular_logger()
        print "double w00t! (though, probably not)"
        self.name = "null"

    def start_suite(self, name, attrs):
        print "*** start suite", name
        sys.stdout.flush()

    def start_test(self, name, attrs):
        print "*** start test", name
        sys.stdout.flush()



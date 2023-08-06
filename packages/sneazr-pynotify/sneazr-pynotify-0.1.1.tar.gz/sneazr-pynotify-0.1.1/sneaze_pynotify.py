import os
import sys
from nose.plugins.base import Plugin
from pkg_resources import resource_filename

try:
    import pynotify
except:
    pass

class SneazrPyNotify(Plugin):
    '''
    A Nose plugin which displays pynotify notifications
    indicating the number of (un)successful tests.
    '''
    name = 'sneazr-pynotify'

    def __init__(self):
        '''Registers a pynotifier.'''
        super(SneazrPyNotify, self).__init__()
        # Store resource path to icons in dict.
        self.icon_paths = {}
        for status in ['pass', 'error', 'fail']:
            self.icon_paths[status] = os.path.join(
                os.path.dirname(__file__),
                'resources', 'logo_%s.png' % status
            )

        try:
            pynotify.init("Sneazr nosetests runner")
        except:
            print "Cannot use pynotify"


    def finalize(self, result=None):
        '''
        Checks results of nosetests and prepares
        notification body.
        '''
        if result.wasSuccessful():
            self.__notify(
                'Success!',
                'All tests passed successfully.',
                self.icon_paths['pass']
            )
        elif len(result.errors) > len(result.failures):
            self.__notify(
                'Failure!',
                'Failed with %s errors and %s failures.' % (
                    len(result.errors), len(result.failures)
                ),
                self.icon_paths['error']
            )
        else:
            self.__notify(
                'Failure!',
                'Failed with %s failures and %s errors' % (
                    len(result.failures), len(result.errors)
                ),
                self.icon_paths['fail']
            )


    def __notify(self, title, message, icon_path=None):
        '''
        Sends a standard notification with the
        given parameters.
        '''
        try:
            n = pynotify.Notification(title, message, icon_path)
            n.show()
        except:
            print "Unexpected error:", sys.exc_info()[0]
            print "Can't send notification"

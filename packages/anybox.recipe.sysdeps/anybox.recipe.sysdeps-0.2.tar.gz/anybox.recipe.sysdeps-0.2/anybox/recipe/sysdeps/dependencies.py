import os,sys, subprocess

class Dependencies(object):

    def __init__(self, buildout, name, options):
        self.name, self.options = name, options
        for executable, system_package in [
                line.split(':') for line in options['bin'].split()]:
            sys.stdout.write('Checking ' + executable + ': ')
            try:
                assert(not subprocess.call(['which', executable], stdout=subprocess.PIPE))
                print('ok')
            except AssertionError:
                raise EnvironmentError('Your system is missing the following executable: '
                                       + executable
                                       + '. Please install ' + system_package)


    def install(self):
        return []

    def update(self):
        pass

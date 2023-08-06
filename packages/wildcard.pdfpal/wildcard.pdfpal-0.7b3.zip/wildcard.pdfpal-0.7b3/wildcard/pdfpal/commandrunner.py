import os
import subprocess
import logging
logger = logging.getLogger('wildcard.pdfpal')

def _format_command(command):
    if type(command) in (tuple, list, set):
        return ' '.join(command)
    else:
        return command

class command_subprocess(object):
    """
    idea of how to handle this shamelessly
    stolen from ploneformgen's gpg calls
    """
    paths = ['/bin', '/usr/bin', '/usr/local/bin']
    bin_name = None # implement this
    shell = False
    throw_exception = False # throw exception if unsuccessfully run

    logging = {
        'info' : 'Command %(command)s successfully executed.',
        'warn' : 'Command "%(command)s" finished with error code: %(return_code)d and output: %(output)s'
    }

    options = [
    ]

    def __init__(self):
        if os.name == 'nt':
            self.bin_name += '.exe'
        binary = self._findbinary()
        self.binary = binary
        if binary is None:
            raise IOError, "Unable to find gs binary"

    def _findbinary(self):
        if os.environ.has_key('PATH'):
            path = os.environ['PATH']
            path = path.split(os.pathsep)
        else:
            path = self.paths
        for dir in path:
            fullname = os.path.join(dir, self.bin_name)
            if os.path.exists( fullname ):
                return fullname
        return None

    def get_command(self, opt_values={}):
        command = [self.binary]
        for option in self.options:
            if '%s' not in option:
                option = option % opt_values

            command.append(option)
        return command

    def get_process(self, stdin=None, opt_values={}):
        command = self.get_command(opt_values)
        logger.info("""Running '%s'""" % _format_command(command))
        if self.shell:
            command = ' '.join(command)
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, shell=self.shell)
        return process

    def run_command(self, opt_values={}, stdin=None, bad_return_code=False):
        process = self.get_process(stdin=stdin, opt_values=opt_values)

        if stdin:
            process.stdin.write(stdin)

        output = process.communicate()[0]

        if stdin:
            process.stdin.close()

        command = _format_command(self.get_command(opt_values))
        strargs = {'command' : command, 'output' : output}
        if process.returncode == 0 or bad_return_code:
            logger.info(self.logging.get('info') % strargs)
        else:
            strargs['return_code'] = process.returncode
            logger.warn(self.logging.get('warn') % strargs)
            if self.throw_exception:
                raise Exception("There was an error running the command %s. " % command)

        return process, output

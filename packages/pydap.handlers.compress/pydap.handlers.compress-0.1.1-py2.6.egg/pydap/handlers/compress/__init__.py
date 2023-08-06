import os
import re
from subprocess import Popen

from pydap.handlers.lib import BaseHandler, get_handler
from pydap.exceptions import OpenFileError
from pydap.client import open_url
from pydap.handlers.helper import constrain


class Handler(BaseHandler):

    extensions = re.compile(r"^.*\.(zip|gz|z|bz2)$", re.IGNORECASE)
    COMMANDS = {'.gz' : 'gunzip -c %s > %s',
                '.bz2': 'bunzip2 -c %s > %s',
                '.z'  : 'uncompress -c %s > %s',
                '.zip': 'unzip -c %s > %s',
               }
    
    def __init__(self, filepath):
        self.compressedfilepath = filepath

    def parse_constraints(self, environ):
        self.environ = environ
        
        tmpdir = environ.get('dap.plugins.compress.tmpdir', '/tmp')
        
        if not os.path.exists(tmpdir):
            os.mkdir(tmpdir)

        id_, extension = os.path.splitext(self.compressedfilepath)
        id_ = id_.replace(os.path.sep, '_')
        self.filepath = newpath = os.path.join(tmpdir, id_)

        if not os.path.exists(newpath):
            try:
                command = self.COMMANDS[extension.lower()] % (self.compressedfilepath, newpath)

                # allowing apache to Popen with the shell is dangerous, but in my testing
                # it was necessary. I believe the restrictions on what can be sent to this
                # should be sufficient for most
                p = Popen(command,shell=True)
                sts = os.waitpid(p.pid,0)[1]

            except:
                raise OpenFileError('Unable to open file %s or write to %s' % (self.compressedfilepath, self.filepath))
        
        H = get_handler(self.filepath)
        return H.parse_constraints(environ)
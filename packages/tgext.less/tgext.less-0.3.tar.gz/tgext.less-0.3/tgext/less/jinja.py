import subprocess
import os
from tg import config
from jinja2 import nodes
from jinja2.ext import Extension

class LessExtension(Extension):
    tags = set(['less'])
    
    def __init__(self, environment):
        super(LessExtension, self).__init__(environment)
        self.static_files_path = os.path.abspath(config['pylons.paths']['static_files'])

    def compile_less(self, name, caller):
        less_body = caller()

        # We are assuming Jinja only calls this function when the template
        # is loaded or reloaded (cached), thus no caching on our part.
        lessc = subprocess.Popen(['lessc', "-x", "-I" + self.static_files_path, '-'], stdout=subprocess.PIPE, stdin=subprocess.PIPE)

        # TODO: EOF Character is not crossplatform, 125 works for linux need to find what works for windows (probably 26)
        out, err = lessc.communicate(input=less_body+chr(125))

        # TODO: Handle returned error code from compiler
        if err:
            return ""

        return out

    def parse(self, parser):
        lineno = parser.stream.next().lineno
        args = [parser.parse_expression()]

        less_body = parser.parse_statements(['name:endless'], drop_needle=True)

        return nodes.CallBlock(self.call_method('compile_less', args), [], [], less_body).set_lineno(lineno)
    
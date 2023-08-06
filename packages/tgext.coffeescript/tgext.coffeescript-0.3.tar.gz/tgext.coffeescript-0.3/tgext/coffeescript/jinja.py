import subprocess
import os
from tg import config
from jinja2 import nodes
from jinja2.ext import Extension

class CoffeeExtension(Extension):
    tags = set(['coffee'])
    
    def __init__(self, environment):
        super(CoffeeExtension, self).__init__(environment)
        self.static_files_path = os.path.abspath(config['pylons.paths']['static_files'])

    def compile_coffee(self, name, caller):
        body = caller()

        # We are assuming Jinja only calls this function when the template
        # is loaded or reloaded (cached), thus no caching on our part.
        coffee = subprocess.Popen(['coffee', "-c", "-b", "-s"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        out, err = coffee.communicate(input=body+"\n")

        # TODO: Handle returned error code from compiler
        if err:
            return ""

        return out

    def parse(self, parser):
        lineno = parser.stream.next().lineno
        args = [parser.parse_expression()]

        body = parser.parse_statements(['name:endcoffee'], drop_needle=True)

        return nodes.CallBlock(self.call_method('compile_coffee', args), [], [], body).set_lineno(lineno)
    
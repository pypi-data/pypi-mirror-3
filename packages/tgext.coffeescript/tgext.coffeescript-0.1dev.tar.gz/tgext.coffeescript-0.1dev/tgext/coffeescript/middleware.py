import subprocess
import os
from tg import config
from webob.exc import status_map
from webob.response import Response

class CoffeeScriptMiddleware(object):
    def __init__(self, app, bare=True):
        self.app = app
        self.cache = {}
        self.static_files_path = os.path.abspath(config['pylons.paths']['static_files'])
        self.bare = True

        try:
            coffee = subprocess.Popen(['coffee', '--version'], stdout=subprocess.PIPE)
        except OSError:
            pass

        out, err = coffee.communicate()

        if "CoffeeScript" in out:
            self.method = "subprocess"

    def compile_coffee(self, fullpath):
        if self.bare:
            args = ['coffee', '-bp', fullpath]
        else:
            ['coffee', '-p', fullpath]

        coffee = subprocess.Popen(args, stdout=subprocess.PIPE)
        out, err = coffee.communicate()

        # TODO: Handle returned error code from compiler
        if err:
            return ""

        return out

    def compile(self, fullpath):
        if self.method == "subprocess":
            return self.compile_coffee(fullpath)
        return ""

    def __call__(self, environment, start_response):
        path = environment.get('PATH_INFO')

        if not path.endswith('.coffee'):
            return self.app(environment, start_response)

        # Check if the file exists, if it doesn't send 404 response
        full_path = os.path.join(self.static_files_path, path[1:])
        if not os.path.exists(full_path):
            return status_map[404]()(environment, start_response)

        # Generate etag key (file modified time)
        etag_key = '"%s"' % os.stat(full_path).st_mtime
        none_match = environment.get('HTTP_IF_NONE_MATCH')

        if none_match and etag_key == none_match:
            start_response('304 Not Modified', (('ETag', etag_key),))
            return ['']

        cached = self.cache.get(path)
        if not cached or cached['etag_key'] != etag_key:
            cached = dict(content=self.compile(full_path), etag_key=etag_key)
            self.cache[path] = cached

        response = Response()
        response.content_type = "text/javascript"
        response.headers['ETag'] = etag_key
        response.body = cached['content']

        return response(environment, start_response)

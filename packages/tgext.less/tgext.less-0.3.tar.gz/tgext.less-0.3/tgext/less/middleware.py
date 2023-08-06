import subprocess
import os
from tg import config
from webob.exc import status_map
from webob.response import Response

class LESSMiddleware(object):
    def __init__(self, app, cache=None):
        self.app = app
        if cache:
            self.cache = cache
        else:
            self.cache = {}
        
        self.static_files_path = os.path.abspath(config['pylons.paths']['static_files'])

        # Check if we have a local less compiler available
        try:
            lessc = subprocess.Popen(['lessc', '--version'], stdout=subprocess.PIPE)
        except OSError:
            pass

        out, err = lessc.communicate()

        if "lessc" in out:
            self.method = "subprocess"

    def compile_lessc(self, fullpath):
        lessc = subprocess.Popen(['lessc', fullpath], stdout=subprocess.PIPE)
        out, err = lessc.communicate()

        # TODO: Handle returned error code from compiler
        if err:
            return ""

        return out

    def compile(self, fullpath):
        if self.method == "subprocess":
            return self.compile_lessc(fullpath)
        return ""

    def __call__(self, environment, start_response):
        path = environment.get('PATH_INFO')

        if not path.endswith('.less'):
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

        try:
            cached = self.cache[path]
        except KeyError:
            cached = None

        if not cached or cached['etag_key'] != etag_key:
            cached = dict(content=self.compile(full_path), etag_key=etag_key)
            self.cache[path] = cached

        response = Response()
        response.content_type = "text/css"
        response.headers['ETag'] = etag_key
        response.body = cached['content']

        return response(environment, start_response)

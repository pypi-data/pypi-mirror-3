import os
from webob import Response
from webob.exc import status_map
from rcssmin import cssmin
from rjsmin import jsmin
from tg import config

class MinifyMiddleware(object):
    def __init__(self, app):
        self.app = app
        self.cache = {}
        self.convert = {'js': self._convert_js,
                        'css': self._convert_css}
        try:
            self.root_directory = os.path.normcase(os.path.abspath((config['paths']['static_files'])))
        except KeyError:
            self.root_directory = os.path.normcase(os.path.abspath((config['pylons.paths']['static_files'])))            

    def _convert_js(self, text):
        return jsmin(text)

    def _convert_css(self, text):
        return cssmin(text)

    def get_pretty_content(self, path):
        f = open(path)
        try:
            return f.read()
        finally:
            f.close()

    def full_path(self, path):
        if path[0] == '/':
            path = path[1:]
        return os.path.normcase(os.path.abspath((os.path.join(self.root_directory, path))))

    def __call__(self, environ, start_response):
        requested_path = environ['PATH_INFO']
        try:
            requested_ext = requested_path.rsplit('.', 1)[1]
        except IndexError:
            return self.app(environ, start_response)
        if requested_ext not in self.convert.keys():
            return self.app(environ, start_response)

        full = self.full_path(requested_path)
        if not os.path.exists(full):
            return status_map[404]()(environ, start_response)

        mtime = os.stat(full).st_mtime

        etag_key = '"%s"' % mtime
        if_none_match = environ.get('HTTP_IF_NONE_MATCH')
        if if_none_match and etag_key == if_none_match:
            start_response('304 Not Modified', [('ETag', etag_key)])
            return ['']

        cached_data = self.cache.get(requested_path)
        if not cached_data or cached_data['etag_key'] != etag_key:
            cached_data = {'content':self.convert[requested_ext](self.get_pretty_content(full)),
                           'etag_key':etag_key}
            self.cache[requested_path] = cached_data

        response = Response()
        response.content_type = 'text/css' if requested_ext == 'css' else 'text/javascript'
        response.headers['ETag'] = etag_key
        response.body = cached_data['content']
        return response(environ, start_response)

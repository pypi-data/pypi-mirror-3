import os, os.path
from webob import Request, Response
from webob.exc import status_map
from scss import parser
from tg import config

class SCSSMiddleware(object):
    def __init__(self, app):
        self.app = app
        self.cache = {}
        try:
            self.root_directory = os.path.normcase(os.path.abspath((config['paths']['static_files'])))
        except KeyError:
            self.root_directory = os.path.normcase(os.path.abspath((config['pylons.paths']['static_files'])))            

    def convert(self, text):
        p = parser.Stylesheet(options=dict(compress=True, comments=False))
        return p.loads(text)

    def __call__(self, environ, start_response):
        requested_path = environ['PATH_INFO']
        if requested_path[-5:] != '.scss':
            return self.app(environ, start_response)

        full = os.path.normcase(os.path.abspath((os.path.join(self.root_directory, requested_path[1:]))))
        if not os.path.exists(full):
            return status_map[404]()(environ, start_response)

        etag_key = '"%s"' % os.stat(full).st_mtime
        if_none_match = environ.get('HTTP_IF_NONE_MATCH')
        if if_none_match and etag_key == if_none_match:
            start_response('304 Not Modified', (('ETag', etag_key),))
            return ['']

        cached_data = self.cache.get(requested_path)
        if not cached_data or cached_data['etag_key'] != etag_key:
            content = open(full)
            cached_data = {'content':self.convert(content.read()),
                           'etag_key':etag_key}
            self.cache[requested_path] = cached_data
            content.close()

        response = Response()
        response.content_type = 'text/css'
        response.headers['ETag'] = etag_key
        response.body = cached_data['content']
        return response(environ, start_response)

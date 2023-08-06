import os, os.path
from webob import Request, Response
from webob.exc import status_map
from compiler import Scss
from tg import config

from logging import getLogger

log = getLogger('tgext.scss')

try:
    import libsass
    USE_LIBSASS = True
except LookupError:
    log.warning('libsass not found, falling back to plain Python SCSS compiler')
    USE_LIBSASS = False

class SCSSMiddleware(object):
    def __init__(self, app):
        self.app = app
        self.cache = {}
        self.includes_cache = {}
        try:
            self.root_directory = os.path.normcase(os.path.abspath((config['paths']['static_files'])))
        except KeyError:
            self.root_directory = os.path.normcase(os.path.abspath((config['pylons.paths']['static_files'])))

        include_paths = [os.path.join(self.root_directory, ip) for ip in config.get('tgext.scss.include_paths', [])]

        if USE_LIBSASS:
            INCLUDES_JOIN_CHAR = ':'
        else:
            INCLUDES_JOIN_CHAR = ','
        self.include_paths = INCLUDES_JOIN_CHAR.join([self.root_directory] + include_paths)

    def convert(self, text):
        if USE_LIBSASS:
            res = libsass.compile(text, self.include_paths)
            if res[0]:
               return res[1]
            else:
                raise RuntimeError(res[1])
        else:
            p = Scss(scss_opts=dict(compress=True, root_path=self.include_paths))
            return p.compile(text)

    def get_scss_content(self, path):
        f = open(path)
        try:
            return f.read()
        finally:
            f.close()

    def parse_imports(self, file_path):
        result = []
        def child(obj):
            imported_path = self.full_path(obj.group(1))
            result.extend(self.parse_imports(imported_path))
            result.append(imported_path)
        src = self.get_scss_content(file_path)
        Scss.import_re.sub(child, src)
        return result

    def full_path(self, path):
        if path[0] == '/':
            path = path[1:]
        return os.path.normcase(os.path.abspath((os.path.join(self.root_directory, path))))

    def __call__(self, environ, start_response):
        requested_path = environ['PATH_INFO']
        if requested_path[-5:] != '.scss':
            return self.app(environ, start_response)

        full = self.full_path(requested_path)
        if not os.path.exists(full):
            return status_map[404]()(environ, start_response)

        files = self.includes_cache.get(requested_path)
        if not files:
            #We still don't know which files are imported, at least the first
            #time we must parse it.
            imports = self.parse_imports(full)
            files = imports + [full]
        mtime = max([os.stat(f).st_mtime for f in files])

        etag_key = '"%s"' % mtime
        if_none_match = environ.get('HTTP_IF_NONE_MATCH')
        if if_none_match and etag_key == if_none_match:
            start_response('304 Not Modified', [('ETag', etag_key)])
            return ['']

        cached_data = self.cache.get(requested_path)
        if not cached_data or cached_data['etag_key'] != etag_key:
            imports = self.parse_imports(full)
            self.includes_cache[requested_path] = imports + [full]

            cached_data = {'content':self.convert(self.get_scss_content(full)),
                           'etag_key':etag_key}
            self.cache[requested_path] = cached_data

        response = Response()
        response.content_type = 'text/css'
        response.headers['ETag'] = etag_key
        response.body = cached_data['content']
        return response(environ, start_response)

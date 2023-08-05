import os, os.path, re
from webob import Request, Response
from webob.exc import status_map
from compiler import Scss
from tg import config

class SCSSMiddleware(object):
    import_re = re.compile(r'^\s*@import +url\(\s*["\']?([^\)\'\"]+)["\']?\s*\)\s*;?\s*$', re.MULTILINE)

    def __init__(self, app):
        self.app = app
        self.cache = {}
        self.includes_cache = {}
        try:
            self.root_directory = os.path.normcase(os.path.abspath((config['paths']['static_files'])))
        except KeyError:
            self.root_directory = os.path.normcase(os.path.abspath((config['pylons.paths']['static_files'])))            

    def convert(self, text, imports):
        text = self.execute_imports(text, imports)

        p = Scss(scss_opts=dict(compress=True))
        return p.compile(text)

    def parse_imports(self, src):
        result = []
        def child(obj):
            result.append(self.full_path(obj.group(1)))
        src = self.import_re.sub(child, src)
        return src, result

    def execute_imports(self, src, imports):
        output = []
        for path in imports:
            f = open(path)
            output.append(f.read())
            f.close()
        output.append(src)

        return '\n'.join(output)

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
            content = open(full)
            text, imports = self.parse_imports(content.read())
            content.close()
            files = imports + [full]
        mtime = max([os.stat(f).st_mtime for f in files])

        etag_key = '"%s"' % mtime
        if_none_match = environ.get('HTTP_IF_NONE_MATCH')
        if if_none_match and etag_key == if_none_match:
            start_response('304 Not Modified', (('ETag', etag_key),))
            return ['']

        cached_data = self.cache.get(requested_path)
        if not cached_data or cached_data['etag_key'] != etag_key:
            content = open(full)
            text, imports = self.parse_imports(content.read())
            cached_data = {'content':self.convert(text, imports),
                           'etag_key':etag_key}
            self.cache[requested_path] = cached_data
            self.includes_cache[requested_path] = imports + [full]
            content.close()

        response = Response()
        response.content_type = 'text/css'
        response.headers['ETag'] = etag_key
        response.body = cached_data['content']
        return response(environ, start_response)

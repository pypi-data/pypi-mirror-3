import widgets as wd, util, core, params as pm
import re, logging, itertools
import os, webob as wo, pkg_resources as pr, mimetypes, simplejson
import inspect


log = logging.getLogger(__name__)


# TBD is there a better place to put this?
mimetypes.init()
mimetypes.types_map['.ico'] = 'image/x-icon'

class JSSymbol(object):
    def __init__(self, src):
        self.src = src

class TW2Encoder(simplejson.encoder.JSONEncoder):
    """
    Technical note: This is basically a copy & paste of TW1's TWEncoder,
    but dumbed down, since I don't need JSCall, etc., but just a wrapper
    kind of like HTML.literal but for JS.
    """

    def __init__(self, *args, **kw):
        self.unescape_pattern = re.compile('"TW2Encoder_unescape_([0-9]*)"')
        super(TW2Encoder, self).__init__(*args, **kw)

    def default(self, obj):
        from js import js_function, js_callback
        if isinstance(obj, (JSSymbol, js_callback, js_function)):
            return self.mark_for_escape(obj)
        if hasattr(obj, '__json__'):
            return obj.__json__()
        return super(TW2Encoder, self).default(obj)

    def encode(self, obj):
        self.unescape_symbols = {}
        encoded = super(TW2Encoder, self).encode(obj)
        unescaped = self.unescape_marked(encoded)
        self.unescape_symbols = {}
        return unescaped

    def mark_for_escape(self, obj):
        self.unescape_symbols[id(obj)] = obj
        return 'TW2Encoder_unescape_' + str(id(obj))

    def unescape_marked(self, encoded):
        def unescape(match):
            try:
                obj_id = int(match.group(1))
                obj = self.unescape_symbols[obj_id]
                return obj.src
            except:
                # Simply return the match if there is a problem
                return match.group(0)
        return self.unescape_pattern.sub(unescape, encoded)

encoder = TW2Encoder()

class Resource(wd.Widget):
    location = pm.Param('Location on the page where the resource should be placed.' \
                        'This can be one of: head, headbottom, bodytop or bodybottom. '\
                        'None means the resource will not be injected, which is still '\
                        'useful, e.g. static images.', default=None)
    id = None

    @classmethod
    def inject(cls):
        cls.req().prepare()

    def prepare(self):
        super(Resource, self).prepare()

        rl_resources = core.request_local().setdefault('resources', [])
        rl_location = core.request_local()['middleware'].config.inject_resources_location

        if self not in rl_resources:
            if self.location is '__use_middleware':
                self.location = rl_location
            for r in self.resources:
                r.req().prepare()

            rl_resources.append(self)


class Link(Resource):
    '''
    A link to a file.
    '''
    id = None
    link = pm.Param('Direct web link to file. If this is not specified, it is automatically generated, based on :attr:`modname` and :attr:`filename`.')
    modname = pm.Param('Name of Python module that contains the file.', default=None)
    filename = pm.Param('Path to file, relative to module base.', default=None)
    no_inject = pm.Param("Don't inject this link. (Default: False)", default=False)

    def guess_modname(self):
        """ Try to guess my modname.

        If I wasn't supplied any modname, take a guess by stepping back up the
        frame stack until I find something not in tw2.core
        """

        try:
            frame, i = inspect.stack()[0][0], 0
            while frame.f_globals['__name__'].startswith('tw2.core'):
                frame, i = inspect.stack()[i][0], i + 1

            return frame.f_globals['__name__']
        except Exception as e:
            return None

    def prepare(self):

        if not self.modname:
            self.modname = self.guess_modname()

        rl = core.request_local()
        if not self.no_inject:
            if not hasattr(self, 'link'):
                # TBD shouldn't we test for this in __new__ ?
                if not self.filename:
                    raise pm.ParameterError("Either 'link' or 'filename' must be specified")
                resources = rl['middleware'].resources
                self.link = resources.register(self.modname or '__anon__', self.filename)
            super(Link, self).prepare()

    def __hash__(self):
        return hash(hasattr(self, 'link') and self.link or ((self.modname or '') + self.filename))

    def __eq__(self, other):
        return (getattr(self, 'link', None) == getattr(other, 'link', None)
                and getattr(self, 'modname', None) == getattr(other, 'modname', None)
                and getattr(self, 'filename', None) == getattr(other, 'filename', None))

    def __repr__(self):
        return "%s('%s')" % (self.__class__.__name__, getattr(self, 'link', '%s/%s'%(self.modname,self.filename)))

class DirLink(Link):
    link = pm.Variable()
    filename = pm.Required

    def prepare(self):
        resources = core.request_local()['middleware'].resources
        self.link = resources.register(self.modname, self.filename, whole_dir=True)


class JSLink(Link):
    '''
    A JavaScript source file.
    '''
    location = '__use_middleware'
    template = 'tw2.core.templates.jslink'

class CSSLink(Link):
    '''
    A CSS style sheet.
    '''
    media = pm.Param('Media tag', default='all')
    location = 'head'
    template = 'tw2.core.templates.csslink'

class JSSource(Resource):
    """
    Inline JavaScript source code.
    """
    src = pm.Param('Source code')
    location = 'bodybottom'
    template = 'tw2.core.templates.jssource'

    def __repr__(self):
        return "%s('%s')" % (self.__class__.__name__, self.src)

class JSFuncCall(JSSource):
    """
    Inline JavaScript function call.
    """
    src = None
    function = pm.Param('Function name')
    args = pm.Param('Function arguments', default=None)
    location = 'bodybottom' # TBD: afterwidget?

    def __str__(self):
        if not self.src:
            self.prepare()
        return self.src

    def prepare(self):
        if not self.src:
            args = ''
            if isinstance(self.args, dict):
                args = encoder.encode(self.args)
            elif self.args:
                args = ', '.join(encoder.encode(a) for a in self.args)

            self.src = '%s(%s)' % (self.function, args)
        super(JSFuncCall, self).prepare()

    def __hash__(self):
        if self.args:
            if isinstance(self.args, dict):
                sargs = encoder.encode(self.args)
            else:
                sargs = ', '.join(encoder.encode(a) for a in self.args)
        else:
            sargs = None

        return hash((hasattr(self, 'src') and self.src or '') + (sargs or ''))

    def __eq__(self, other):
        return (getattr(self, 'src', None) == getattr(other, 'src', None)
                and getattr(self, 'args', None) == getattr(other, 'args', None)
                )

class ResourcesApp(object):
    """WSGI Middleware to serve static resources

    This handles URLs like this:
        /resources/tw2.forms/static/forms.css

    Where:
        resources       is the prefix
        tw2.forms       is a python package name
        static          is a directory inside the package
        forms.css       is the file to retrieve

    For this to work, the file must have been registered in advance,
    using :meth:`register`. There is a ResourcesApp instance for each
    TwMiddleware instance.
    """

    def __init__(self, config):
        self._paths = {}
        self._dirs = []
        self.config = config

    def register(self, modname, filename, whole_dir=False):
        """Register a file for static serving, and return the web path.

        After this method has been called, for say ('tw2.forms',
        'static/forms.css'), the URL /resources/tw2.forms/static/forms.css will
        then serve that file from within the tw2.forms package. This works
        correctly for zipped eggs.

        *Security Consideration* - This file will be readable by users of the
        application, so make sure it contains no confidential data. For
        DirLink resources, the whole directory, and subdirectories will be
        readable.

        `modname`
            The python module that contains the file to publish. You can also
            pass a pkg_resources.Requirement instance to point to the root of
            an egg distribution.

        `filename`
            The path, relative to the base of the module, of the file to be
            published. If *modname* is None, it's an absolute path.
        """
        if isinstance(modname, pr.Requirement):
            modname = os.path.basename(pr.working_set.find(modname).location)
        if whole_dir:
            path = modname + '/' + filename.lstrip('/')
            if path not in self._dirs:
                self._dirs.append(path)
        else:
            path = modname + '/' + filename.strip('/')
            if path not in self._paths:
                self._paths[path] = (modname, filename)

        return self.config.script_name+self.config.res_prefix + path

    def __call__(self, environ, start_response):
        req = wo.Request(environ)
        try:
            path = environ['PATH_INFO']
            path = path[len(self.config.res_prefix):]

            if path not in self._paths:
                if '..' in path: # protect against directory traversal
                    raise IOError()
                for d in self._dirs:
                    if path.startswith(d):
                        break
                else:
                    raise IOError()
            modname, filename = path.lstrip('/').split('/', 1)
            ct, enc = mimetypes.guess_type(os.path.basename(filename))
            if modname and modname != '__anon__':
                stream = pr.resource_stream(modname, filename)
            else:
                stream = open(filename)
        except IOError:
            resp = wo.Response(status="404 Not Found")
        else:
            stream = _FileIter(stream, self.config.bufsize)
            resp = wo.Response(app_iter=stream, content_type=ct)
            if enc:
                resp.content_type_params['charset'] = enc
        resp.cache_control = {'max-age': int(self.config.res_max_age)}
        return resp(environ, start_response)

# Could use wsgiref, but this is python 2.4 compatible
class _FileIter(object):
    def __init__(self, fileobj, bufsize):
        self.fileobj = fileobj
        self.bufsize = bufsize

    def __iter__(self):
        return self

    def next(self):
        buf = self.fileobj.read(self.bufsize)
        if not buf:
            raise StopIteration
        return buf

    def close(self):
        self.fileobj.close()


class _ResourceInjector(util.MultipleReplacer):
    """ToscaWidgets can inject resources that have been registered for injection in
    the current request.

    Usually widgets register them when they're displayed and they have instances of
    :class:`tw2.core.resources.Resource` declared at their :attr:`tw2.core.Widget.javascript` or
    :attr:`tw2.core.Widget.css` attributes.

    Resources can also be registered manually from a controller or template by
    calling their :meth:`tw2.core.resources.Resource.inject` method.

    When a page including widgets is rendered, Resources that are registered for
    injection are collected in a request-local
    storage area (this means any thing stored here is only visible to one single
    thread of execution and that its contents are freed when the request is
    finished) where they can be rendered and injected in the resulting html.

    ToscaWidgets' middleware can take care of injecting them automatically (default)
    but they can also be injected explicitly, example::

       >>> from tw2.core.resources import JSLink, inject_resources
       >>> JSLink(link="http://example.com").inject()
       >>> html = "<html><head></head><body></body></html>"
       >>> inject_resources(html)
       '<html><head><script type="text/javascript" src="http://example.com"></script></head><body></body></html>'

    Once resources have been injected they are popped from request local and
    cannot be injected again (in the same request). This is useful in case
    :class:`injector_middleware` is stacked so it doesn't inject them again.

    Injecting them explicitly is neccesary if the response's body is being cached
    before the middleware has a chance to inject them because when the cached
    version is served no widgets are being rendered so they will not have a chance
    to register their resources.
    """

    def __init__(self):
        return util.MultipleReplacer.__init__(self, {
            r'<head(?!er).*?>': self._injector_for_location('head'),
            r'</head(?!er).*?>': self._injector_for_location('headbottom', False),
            r'<body.*?>': self._injector_for_location('bodytop'),
            r'</body.*?>': self._injector_for_location('bodybottom', False)
            }, re.I|re.M)

    def _injector_for_location(self, key, after=True):
        def inject(group, resources, encoding):
            inj = u'\n'.join([r.display(displays_on='string') for r in resources if r.location == key])
            inj = inj.encode(encoding)
            if after:
                return group + inj
            return  inj + group
        return inject

    def __call__(self, html, resources=None, encoding=None):
        """Injects resources, if any, into html string when called.

        .. note::
           Ignore the ``self`` parameter if seeing this as
           :func:`tw.core.resource_injector.inject_resources` docstring
           since it is an alias for an instance method of a private class.

        ``html`` must be a ``encoding`` encoded string. If ``encoding`` is not
        given it will be tried to be derived from a <meta>.

        """
        if resources is None:
            resources = core.request_local().get('resources', None)
        if resources:
            encoding = encoding or find_charset(html) or 'utf-8'
            html = util.MultipleReplacer.__call__(self, html, resources, encoding)
            core.request_local().pop('resources', None)
        return html


# Bind __call__ directly so docstring is included in docs
inject_resources = _ResourceInjector().__call__


_charset_re = re.compile(r"charset\s*=\s*(?P<charset>[\w-]+)([^\>])*",
                         re.I|re.M)
def find_charset(string):
    m = _charset_re.search(string)
    if m:
        return m.group('charset').lower()

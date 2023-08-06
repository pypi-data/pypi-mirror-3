""":mod:`irclog.web` --- Web IRC log view
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import re
import datetime
import functools
import urllib
import base64
import os.path
import sys
import traceback
import json
import jinja2
import irclog.archive
import irclog.messages


MIMETYPES = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
             "gif": "image/gif", "ico": "image/vnd.microsoft.icon",
             "css": "text/css", "html": "text/html",
             "js": "text/javascript"}
REDIR_STATUS_CODES = {301: "301 Moved Permanently",
                      302: "302 Found",
                      303: "303 See Other",
                      304: "304 Not Modified",
                      305: "305 Use Proxy",
                      307: "307 Temporary Redirect"}
JINJA2_EXTENSIONS = ["jinja2.ext.autoescape", "jinja2.ext.do"]


class Application(object):
    """WSGI application. ::

        import os, os.path
        path = os.path.join(
            os.environ["HOME"],
            ".irssi/logs/<server>/<channel>/<date:%Y-%m-%d>.log"
        )
        app = Application(path)

    :param archive: an archive object or path
    :type archive: :class:`Archive <irclog.archive.Archive>`,
                   :class:`FilenamePattern <irclog.archive.FilenamePattern>`,
                   :class:`basestring`
    :param template_path: a path of template files
    :type template_path: :class:`basestring`
    :param path_prefix: a prefix for the path. default is an empty string
    :type path_prefix: :class:`basestring`
    :param encoding: an encoding of response text. default is ``"utf-8"``
    :type encoding: :class:`basestring`
    :param debug: a debug flag. default is ``False``
    :type debug: :class:`bool`


    .. data:: STATIC_PATH_PATTERN

    .. data:: PATH_MAP

       The :class:`list`: of :class:`tuple` contains template name, routing
       pattern and object getting function.

       Form is like following::

           [("template.html", re.compile("url regex"), lambda app, ...: ...)]

    .. attribute:: archive
    
       The :class:`Archive <irclog.archive.Archive>` object.

    .. attribute:: template_path

       The path of template files.

    .. attribute:: template_environment

       The Jinja2 template environment. A :class:`jinja2.Environment` instance.

    .. attribute:: path_prefix

       The prefix of the path.

    .. attribute:: encoding

       The encoding of response text.

    .. attribute:: debug

       The debug flag.

    """

    STATIC_PATH_PATTERN = re.compile(r"^/_/static/_/(?P<file>.+)$")
    PATH_MAP = []

    __slots__ = "archive", "template_path", "template_environment", \
                "path_prefix", "encoding", "debug"

    @classmethod
    def route(cls, template_name, pattern_string):
        """Registers a function as request handler.

        .. sourcecode:: pycon

           >>> __tmp__ = Application.PATH_MAP
           >>> Application.PATH_MAP = []
           >>> Application.PATH_MAP
           []
           >>> @Application.route("myhandler.html", r"^/(?P<a>.)/(?P<b>.)/?$")
           ... def myhandler(app, a, b):
           ...     return {"a": a, "b": b}
           ...
           >>> Application.PATH_MAP  # doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
           [('myhandler.html', <_sre.SRE_Pattern object at ...>,
             <function myhandler at ...>)]
           >>> Application.PATH_MAP = __tmp__

        :param template_name: a template filename
        :type template_name: :class:`basestring`
        :param pattern_string: a pattern of URL to route
        :type pattern_string: :class:`basestring`

        """
        def decorate(function):
            pattern = re.compile(pattern_string)
            cls.PATH_MAP.append((template_name, pattern, function))
            return function
        return decorate

    @classmethod
    def redirect(cls, pattern_string, status_code=307):
        """Registers a redirection handler.

        .. sourcecode:: pycon

           >>> __tmp__ = Application.PATH_MAP
           >>> Application.PATH_MAP = []
           >>> Application.PATH_MAP
           []
           >>> @Application.redirect(r"^/(?P<a>.)/(?P<b>.)/?$", 301)
           ... def redirect(app, a, b):
           ...     return "/url/{0}/{1}".format(a, b)
           ...
           >>> Application.PATH_MAP  # doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
           [(301, <_sre.SRE_Pattern object at ...>,
             <function redirect at ...>)]
           >>> Application.PATH_MAP = __tmp__

        :param pattern_string: a pattern of URL to route
        :type pattern_string: :class:`basestring`

        """
        def decorate(function):
            pattern = re.compile(pattern_string)
            cls.PATH_MAP.append((status_code, pattern, function))
            return function
        return decorate

    def __init__(self, archive, template_path,
                 path_prefix="", encoding="utf-8", debug=False):
        if not isinstance(archive, irclog.archive.Archive):
            archive = irclog.archive.Archive(archive)
        self.archive = archive
        self.template_path = template_path
        loader = jinja2.FileSystemLoader(template_path)
        environ = jinja2.Environment(loader=loader,
                                     autoescape=True,
                                     extensions=JINJA2_EXTENSIONS)
        self.template_environment = environ
        setup_template_environment(self.template_environment)
        if path_prefix.endswith("/"):
            path_prefix = path_prefix[:-1]
        self.path_prefix = path_prefix
        self.encoding = encoding
        self.debug = debug

    def __call__(self, environ, start_response):
        try:
            if environ["PATH_INFO"].startswith(self.path_prefix):
                prefix_len = len(self.path_prefix)
                environ["PATH_INFO"] = environ["PATH_INFO"][prefix_len:]
                if "RAW_URI" in environ:
                    environ["RAW_URI"] = environ["RAW_URI"][prefix_len:]
            else:
                return self.error_404(environ, start_response)
            match = self.STATIC_PATH_PATTERN.match(environ["PATH_INFO"])
            if match:
                r = self.serve_static_resources(environ, start_response, match)
                return r
            else:
                return self.serve_application(environ, start_response)
        except Exception:
            exc_info = sys.exc_info()
            return self.error_500(environ, start_response, exc_info)

    def serve_application(self, environ, start_response):
        for template_name, pattern, handle in self.PATH_MAP:
            match = pattern.match(environ["PATH_INFO"])
            if match:
                env = Environment(self, environ)
                try:
                    context = handle(env, **match.groupdict())
                except LookupError:
                    continue
                if template_name in REDIR_STATUS_CODES:
                    start_response(
                        REDIR_STATUS_CODES[template_name],
                        [("Location", context), ("Content-Type", "text/plain")]
                    )
                    return "Go {0}".format(context)
                if "__app__" not in context:
                    context["__app__"] = self
                    context["__environ__"] = env
                tpl = self.template_environment.get_template(template_name)
                if self.debug:
                    result = tpl.render(context)
                else:
                    result = tpl.generate(context)
                content_type = "text/html; charset=" + self.encoding
                start_response("200 OK", [("Content-Type", content_type)])
                return (buffer.encode(self.encoding) for buffer in result)
        return self.error_404(environ, start_response)

    def serve_static_resources(self, environ, start_response, match=None):
        match = match or self.STATIC_PATH_PATTERN.match(path)
        path = os.path.join(self.template_path,
                            *match.group("file").split("/"))
        _, suffix = path.rsplit(".", 1)
        if os.path.isfile(path):
            content_type = MIMETYPES.get(suffix, "application/octet-stream")
            start_response("200 OK", [("Content-Type", content_type)])
            with open(path) as file:
                for buffer in file:
                    yield buffer
        else:
            for buffer in self.error_404(environ, start_response):
                yield buffer

    def error_404(self, environ, start_response):
        start_response("404 Not Found", [("Content-Type", "text/plain")])
        return "page not found",

    def error_500(self, environ, start_response, exc_info=None):
        start_response("500 Internal Server Error",
                       [("Content-Type", "text/plain")])
        yield "internal server error"
        if exc_info is not None and self.debug:
            yield "\n\n"
            for line in traceback.format_exception(*exc_info):
                yield line


class Environment(dict):
    """HTTP request environment. It contains WSGI environment values, and is
    a subtype of :class:`dict`.

    :param application: an application
    :type application: :class:`Application`
    :param environment: a WSGI environment dictionary
    :type environment: :class:`dict`

    .. attribute:: application

       The :class:`Application` instance.

    """

    __slots__ = "application",

    def __init__(self, application, environment):
        if not isinstance(application, Application):
            raise TypeError("application must be an irclog.web.Application "
                            "instance, not " + repr(application))
        dict.__init__(self, environment)
        self.application = application

    @property
    def app(self):
        """Alias of :attr:`application`."""
        return self.application

    @property
    def authorization(self):
        """The :class:`tuple` that contains credential pair: user and password.

        .. sourcecode:: pycon

           >>> assert isinstance(env, Environment)  # doctest: +SKIP
           >>> env['HTTP_AUTHORIZATION']  # doctest: +SKIP
           'Basic dXNlcjpwYXNz'
           >>> env.authorization  # doctest: +SKIP
           ('user', 'pass')

        It is ``None`` when there's no ``'HTTP_AUTHORIZATION'`` key:

        .. sourcecode:: pycon

           >>> assert isinstance(env2, Environment)  # doctest: +SKIP
           >>> 'HTTP_AUTHORIZATION' in env  # doctest: +SKIP
           False
           >>> print env.auth  # doctest: +SKIP
           None

        """
        try:
            auth = self["HTTP_AUTHORIZATION"]
        except KeyError:
            return
        type, auth = auth.split()
        if type.lower() == "basic":
            return tuple(base64.b64decode(auth).split(":", 1))
        elif type.lower() == "digest":
            m = re.search(r'(?:^|,)\s*username\s*=\s*"([^"]*)"\s*(?:,|$)',
                          auth, re.I)
            if m:
                return m.group(1), None

    def __repr__(self):
        cls = type(self)
        modname = "" if cls.__module__ == "__main__" else cls.__module__ + "."
        clsname = modname + cls.__name__
        return "<{0} {1}>".format(clsname, dict.__repr__(self)[1:-1])


@Application.route("archive.html", r"^/?$")
def handle_archive(environ):
    return {"archive": environ.app.archive}


@Application.route("server.html", r"^/(?P<server>.+?)/?$")
def handle_server(environ, server):
    context = handle_archive(environ)
    context["server"] = environ.app.archive[server]
    return context


@Application.route("channel.html", r"^/(?P<server>.+?)/(?P<channel>.*?)/?$")
def handle_channel(environ, server, channel):
    context = handle_server(environ, server)
    context["channel"] = context["server"][channel]
    return context


@Application.redirect(r"^/(?P<server>.+?)/(?P<channel>.*?)/today$")
def redirect_today_log(environ, server, channel):
    date = datetime.date.today()
    return date.strftime("%Y-%m-%d")


@Application.route("log.html", r"^/(?P<server>.+?)/(?P<channel>.*?)"
                               r"/(?P<date>\d{4}-\d\d-\d\d)$")
def handle_log(environ, server, channel, date):
    date = datetime.date(*map(int, date.split("-")))
    context = handle_channel(environ, server, channel)
    context["log"] = context["channel"][date]
    return context


def setup_template_environment(environment):
    """Sets up the Jinja2 environment.

    :param environment: a Jinja2 environment
    :type environment: :class:`jinja2.Environment`

    """
    if not isinstance(environment, jinja2.Environment):
        raise TypeError("expected a jinja2.environment.Environment instance,"
                        "not " + repr(environment))
    def require(module):
        if ":" in module:
            module, var = module.split(":")
        else:
            var = None
        mod = __import__(module)
        for name in module.split(".")[1:]:
            mod = getattr(mod, name)
        if var:
            return getattr(mod, var)
        return mod
    environment.globals["require"] = require
    @jinja2.contextfilter
    def url(context, val):
        return context["__app__"].path_prefix + url_for(val)
    environment.filters["url"] = url
    environment.filters["json"] = json.dumps
    for name in dir(irclog.messages):
        c = getattr(irclog.messages, name)
        if isinstance(c, type) and issubclass(c, irclog.messages.BaseMessage):
            environment.tests[name] = lambda i, c=c: isinstance(i, c)
    for name in dir(irclog.archive):
        c = getattr(irclog.archive, name)
        if isinstance(c, type) and issubclass(c, irclog.archive.BaseArchive):
            environment.tests[name] = lambda i, c=c: isinstance(i, c)
    environment.tests["Log"] = lambda i: isinstance(i, irclog.archive.Log)


def quote_url(object):
    """Quotes as URL.

    .. sourcecode:: pycon

       >>> quote_url(1)
       '1'
       >>> quote_url("hello world")
       'hello%20world'

    :param object: an object to be quoted
    :returns: a quoted string

    """
    return urllib.quote(str(object))


def url_for(object):
    """Makes an URL for the ``object``.

    :param object: an object to create URL
    :returns: an URL

    """
    if isinstance(object, basestring):
        return "/_/static/_/{0}".format(quote_url(object))
    if isinstance(object, irclog.archive.Archive):
        return "/"
    if isinstance(object, irclog.archive.Server):
        return "/{0}/".format(quote_url(object))
    if isinstance(object, irclog.archive.Channel):
        return "/{0}/{1}/".format(quote_url(object.server), quote_url(object))
    if isinstance(object, irclog.archive.Log):
        return "/{0}/{1}/{2}".format(quote_url(object.server),
                                     quote_url(object.channel),
                                     quote_url(object.date))


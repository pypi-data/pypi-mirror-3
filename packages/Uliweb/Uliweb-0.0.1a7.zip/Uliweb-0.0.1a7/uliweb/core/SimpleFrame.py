####################################################################
# Author: Limodou@gmail.com
# License: BSD
####################################################################

import os, sys
import cgi
import inspect
from werkzeug import Request as OriginalRequest, Response as OriginalResponse
from werkzeug import ClosingIterator, Local, LocalManager, BaseResponse
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.routing import Map

import template
from storage import Storage
import dispatch
from uliweb.utils.common import (pkg, log, import_attr, 
    myimport, wraps, norm_path, cache_get)
import uliweb.utils.pyini as pyini
from uliweb.i18n import gettext_lazy
from uliweb.utils.localproxy import LocalProxy, Global
from uliweb import UliwebError

#from rules import Mapping, add_rule
import rules

try:
    set
except:
    from sets import Set as set

local = Local()
__global__ = Global()
local_manager = LocalManager([local])
url_map = Map()
static_views = []
use_urls = False
url_adapters = {}
__app_dirs__ = {}
__app_alias__ = {}

#Initialize pyini env
pyini.set_env({'_':gettext_lazy, 'gettext_lazy':gettext_lazy})
__global__.settings = pyini.Ini()

#User can defined decorator functions in settings DECORATORS
#and user can user @decorators.function_name in views
#and this usage need settings be initialized before decorator invoking
class Decorators(object):
    __decorators__ = {}
    
    def __getattr__(self, name):
        if name in self.__decorators__:
            return self.__decorators__[name]
        if name not in settings.DECORATORS:
            raise UliwebError("decorator %s is not existed!" % name)
        func = import_attr(settings.DECORATORS.get(name))
        self.__decorators__[name] = func
        return func
    
decorators = Decorators()

class Functions(object):
    __functions__ = {}
    
    def __getattr__(self, name):
        if name in self.__functions__:
            return self.__functions__[name]
        if name not in settings.FUNCTIONS:
            raise UliwebError("function %s is not existed!" % name)
        func = import_attr(settings.FUNCTIONS.get(name))
        self.__functions__[name] = func
        return func

functions = Functions()

class Request(OriginalRequest):
    GET = OriginalRequest.args
    POST = OriginalRequest.form
    params = OriginalRequest.values
    FILES = OriginalRequest.files
    
class Response(OriginalResponse):
    def write(self, value):
        self.stream.write(value)
    
class HTTPError(Exception):
    def __init__(self, errorpage=None, **kwargs):
        self.errorpage = errorpage or settings.GLOBAL.ERROR_PAGE
        self.errors = kwargs

    def __str__(self):
        return repr(self.errors)
   
def redirect(location, code=302):
    response = Response(
        '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n'
        '<title>Redirecting...</title>\n'
        '<h1>Redirecting...</h1>\n'
        '<p>You should be redirected automatically to target URL: '
        '<a href="%s">%s</a>.  If not click the link.' %
        (cgi.escape(location), cgi.escape(location)), status=code, content_type='text/html')
    response.headers['Location'] = location
    return response

def error(message='', errorpage=None, request=None, appname=None, **kwargs):
    kwargs.setdefault('message', message)
    if request:
        kwargs.setdefault('link', request.url)
    raise HTTPError(errorpage, **kwargs)

def function(fname, *args, **kwargs):
    func = settings.get_var('FUNCTIONS/'+fname)
    if func:
        if args or kwargs:
            return import_attr(func)(*args, **kwargs)
        else:
            return import_attr(func)
    else:
        raise UliwebError("Can't find the function [%s] in settings" % fname)
 
def json(data):
    from js import json_dumps
        
    if callable(data):
        @wraps(data)
        def f(*arg, **kwargs):
            ret = data(*arg, **kwargs)
            return Response(json_dumps(ret), content_type='application/json; charset=utf-8')
        return f
    else:
        return Response(json_dumps(data), content_type='application/json; charset=utf-8')

def expose(rule=None, **kwargs):
    e = rules.Expose(rule, **kwargs)
    if e.parse_level == 1:
        return rule
    else:
        return e

def POST(rule, **kw):
    kw['methods'] = ['POST']
    return expose(rule, **kw)

def GET(rule, **kw):
    kw['methods'] = ['GET']
    return expose(rule, **kw)

def get_url_adapter(_domain_name):
    """
    Fetch a domain url_adapter object, and bind it to according domain
    """
    domain = application.domains.get(_domain_name, {})
    if domain.get('domain', ''):
        adapter = url_map.bind(domain['host'], url_scheme=domain.get('scheme', 'http'))
    else:
        adapter = url_map.bind_to_environ(request.environ)
    return adapter

def url_for(endpoint, **values):
    if inspect.isfunction(endpoint):
        point = endpoint.__module__ + '.' + endpoint.__name__
    elif inspect.ismethod(endpoint):
        if not endpoint.im_self:    #instance method
            clsname = endpoint.im_class.__name__
        else:                       #class method
            clsname = endpoint.im_self.__name__
        point = '.'.join([endpoint.__module__, clsname, endpoint.__name__])
    else:
        if isinstance(endpoint, (str, unicode)):
            #if the endpoint is string format, then find and replace
            #the module prefix with app alias which matched
            for k, v in __app_alias__.iteritems():
                if endpoint.startswith(k):
                    endpoint = v + endpoint[len(k):]
                    break
        point = endpoint
    _domain_name = values.pop('_domain_name', 'default')
    _external = values.pop('_external', False)
    domain = application.domains.get(_domain_name, {})
    if not _external:
        _external = domain.get('display', False)
    if point in rules.__url_names__:
        point = rules.__url_names__[point]
    adapter = get_url_adapter(_domain_name)
    return adapter.build(point, values, force_external=_external)

def get_app_dir(app):
    """
    Get an app's directory
    """
    path = __app_dirs__.get(app)
    if path is not None:
        return path
    else:
        p = app.split('.')
        try:
            path = pkg.resource_filename(p[0], '')
        except ImportError, e:
            log.exception(e)
            path = ''
        if len(p) > 1:
            path = os.path.join(path, *p[1:])
        
        __app_dirs__[app] = path
        return path

def get_app_depends(app, existed_apps=None):
    if existed_apps is None:
        s = set()
    else:
        s = existed_apps

    if app in s:
        raise StopIteration

    if isinstance(app, (tuple, list)):
        app, name = app
        __app_alias__[name+'.'] = app + '.'

    configfile = os.path.join(get_app_dir(app), 'config.ini')
    if os.path.exists(configfile):
        x = pyini.Ini(configfile)
        apps = x.get_var('DEPENDS/REQUIRED_APPS', [])
        for i in apps:
            if i not in s:
                for j in get_app_depends(i, s):
                    yield j
    s.add(app)
    yield app

def get_apps(apps_dir, include_apps=None, settings_file='settings.ini', local_settings_file='local_settings.ini'):

    include_apps = include_apps or []
    inifile = norm_path(os.path.join(apps_dir, settings_file))
    apps = []
    visited = set()
    if not os.path.exists(apps_dir):
        return apps
    if os.path.exists(inifile):
        x = cache_get(inifile, lambda x:pyini.Ini(x), 'ini')
        if x:
            for app in x.GLOBAL.get('INSTALLED_APPS', []):
                apps.extend(list(get_app_depends(app, visited)))

    local_inifile = norm_path(os.path.join(apps_dir, local_settings_file))
    if os.path.exists(local_inifile):
        x = cache_get(local_inifile, lambda x:pyini.Ini(x), 'ini')
        if x and 'GLOBAL' in x:
            for app in x.GLOBAL.get('INSTALLED_APPS', []):
                apps.extend(list(get_app_depends(app, visited)))

    if not apps and os.path.exists(apps_dir):
        for p in os.listdir(apps_dir):
            if os.path.isdir(os.path.join(apps_dir, p)) and p not in ['.svn', 'CVS', '.git'] and not p.startswith('.') and not p.startswith('_'):
                apps.append(p)
    
    for app in include_apps:
        apps.extend(list(get_app_depends(app, visited)))

    return apps

class Loader(object):
    def __init__(self, tmpfilename, vars, env, dirs, notest=False):
        self.tmpfilename = tmpfilename
        self.dirs = dirs
        self.vars = vars
        self.env = env
        self.notest = notest
        
    def get_source(self, exc_type, exc_value, exc_info, tb):
        from uliweb.core.template import Template
        t = Template('', self.vars, self.env, self.dirs)
        t.set_filename(self.tmpfilename)
        use_temp_flag, filename, text = t.get_parsed_code()
        
        if exc_type is SyntaxError:
            import re
            r = re.search(r'line (\d+)', str(exc_value))
            lineno = int(r.group(1))
        else:
            lineno = tb.tb_frame.f_lineno
        return self.tmpfilename, lineno, text 
    
    def test(self, filename):
        if self.notest:
            return True
        return filename.endswith('.html')
    
class Dispatcher(object):
    installed = False
    def __init__(self, apps_dir='apps', project_dir=None, include_apps=None, start=True, default_settings=None, settings_file='settings.ini', local_settings_file='local_settings.ini'):
        __global__.application = self
        self.debug = False
        self.include_apps = include_apps or []
        self.default_settings = default_settings or {}
        self.settings_file = settings_file
        self.local_settings_file = local_settings_file
        if not Dispatcher.installed:
            self.init(project_dir, apps_dir)
            dispatch.call(self, 'startup_installed')
            self.init_urls()
            
        if start:
            dispatch.call(self, 'startup')
    
    def init(self, project_dir, apps_dir):
        if not project_dir:
            project_dir = norm_path(os.path.join(apps_dir, '..'))
        Dispatcher.project_dir = project_dir
        Dispatcher.apps_dir = norm_path(os.path.join(project_dir, 'apps'))
        Dispatcher.apps = get_apps(self.apps_dir, self.include_apps, self.settings_file, self.local_settings_file)
        Dispatcher.modules = self.collect_modules()
        
        self.install_settings(self.modules['settings'])
        Dispatcher.settings = settings
        
        #process domains
        self.process_domains(settings)
        
        #setup log
        self.set_log()
        
        #set app rules
        rules.set_app_rules(dict(settings.get('URL', {})))
        
        Dispatcher.env = self._prepare_env()
        Dispatcher.template_dirs = self.get_template_dirs()
        
        #begin to start apps
        self.install_apps()
        #process binds
        self.install_binds()
        dispatch.call(self, 'after_init_apps')
        #process views
        self.install_views(self.modules['views'])
        #process exposes
        self.install_exposes()
        #process middlewares
        Dispatcher.middlewares = self.install_middlewares()
        
        self.debug = settings.GLOBAL.get('DEBUG', False)
        dispatch.call(self, 'prepare_default_env', Dispatcher.env)
        Dispatcher.default_template = pkg.resource_filename('uliweb.core', 'default.html')
        
        Dispatcher.installed = True
        
    def _prepare_env(self):
        env = Storage({})
        env['url_for'] = url_for
        env['redirect'] = redirect
        env['error'] = error
        env['application'] = self
        env['settings'] = settings
        env['json'] = json
        return env
    
    def set_log(self):
        import logging
        
        s = self.settings
        
        def _get_level(level):
            return getattr(logging, level.upper())
        
        #get basic configuration
        config = {}
        for k, v in s.LOG.items():
            if k in ['format', 'datefmt', 'filename', 'filemode']:
                config[k] = v
                
        if s.get_var('LOG/level'):
            config['level'] = _get_level(s.get_var('LOG/level'))
        logging.basicConfig(**config)
        
        #process formatters
        formatters = {}
        for f, v in s.get_var('LOG.Formatters', {}).items():
            formatters[f] = logging.Formatter(v)
            
        #process handlers
        handlers = {}
        for h, v in s.get_var('LOG.Handlers', {}).items():
            handler_cls = v.get('class', 'logging.StreamHandler')
            handler_args = v.get('args', ())
            
            handler = import_attr(handler_cls)(*handler_args)
            if v.get('level'):
                handler.setLevel(_get_level(v.get('level')))
            
            format = v.get('format')
            if format in formatters:
                handler.setFormatter(formatters[format])
            elif format:
                fmt = logging.Formatter(format)
                handler.setFormatter(fmt)
                
            handlers[h] = handler
            
        #process loggers
        for logger_name, v in s.get_var('LOG.Loggers', {}).items():
            if logger_name == 'ROOT':
                log = logging.getLogger('')
            else:
                log = logging.getLogger(logger_name)
                
            if v.get('level'):
                log.setLevel(_get_level(v.get('level')))
            if 'propagate' in v:
                log.propagate = v.get('propagate')
            if 'handlers' in v:
                for h in v['handlers']:
                    if h in handlers:
                        log.addHandler(handlers[h])
                    else:
                        raise UliwebError("Log Handler %s is not defined yet!")
                        sys.exit(1)
            elif 'format' in v:
                if v['format'] not in formatters:
                    fmt = logging.Formatter(v['format'])
                else:
                    fmt = formatters[v['format']]
                handler = logging.StreamHandler()
                handler.setFormatter(fmt)
                log.addHandler(handler)
                
    def process_domains(self, settings):
        from urlparse import urlparse

        self.domains = {}
        
        for k, v in settings.DOMAINS.iteritems():
            _domain = urlparse(v['domain'])
            self.domains[k] = {'domain':v.get('domain'), 'domain_parse':_domain, 
                'host':_domain.netloc,
                'scheme':_domain.scheme or 'http', 'display':v.get('display', False)}
        
    def get_file(self, filename, dir='static'):
        """
        get_file will search from apps directory
        """
        if os.path.exists(filename):
            return filename
        dirs = self.apps
        if dir:
            fname = os.path.join(dir, filename)
        else:
            fname = filename
        for d in reversed(dirs):
            path = pkg.resource_filename(d, fname)
            if os.path.exists(path):
                return path
        return None

    def template(self, filename, vars=None, env=None, dirs=None, default_template=None):
        vars = vars or {}
        dirs = dirs or self.template_dirs
        env = env or self.get_view_env()
        
        if self.debug:
            def _compile(code, filename, action, env, Loader=Loader):
                env['__loader__'] = Loader(filename, vars, env, dirs, notest=True)
                try:
                    return compile(code, filename, 'exec')
                except:
#                    file('out.html', 'w').write(code)
                    raise
            
            return template.template_file(filename, vars, env, dirs, default_template, compile=_compile)
        else:
            return template.template_file(filename, vars, env, dirs, default_template)
    
    def render_text(self, text, vars=None, env=None, dirs=None, default_template=None):
        vars = vars or {}
        env = env or self.get_view_env()
        dirs = dirs or self.template_dirs
        
        return template.template(text, vars, env, dirs, default_template)
    
    def render(self, templatefile, vars, env=None, dirs=None, default_template=None, content_type='text/html', status=200):
        return Response(self.template(templatefile, vars, env, dirs, default_template=default_template), status=status, content_type=content_type)
    
    def _page_not_found(self, description=None, **kwargs):
        description = 'The requested URL "{{=url}}" was not found on the server.'
        text = """<h1>Page Not Found</h1>
    <p>%s</p>
    <h3>Current URL Mapping is</h3>
    <table border="1">
    <tr><th>URL</th><th>View Functions</th></tr>
    {{for url, methods, endpoint in urls:}}
    <tr><td>{{=url}} {{=methods}}</td><td>{{=endpoint}}</td></tr>
    {{pass}}
    </table>
    """ % description
        return Response(template.template(text, kwargs), status=404, content_type='text/html')
        
    def not_found(self, e):
        if self.debug:
            urls = []
            for r in url_map.iter_rules():
                if r.methods:
                    methods = ' '.join(list(r.methods))
                else:
                    methods = ''
                urls.append((r.rule, methods, r.endpoint))
            urls.sort()
            return self._page_not_found(url=local.request.path, urls=urls)
        tmp_file = template.get_templatefile('404'+settings.GLOBAL.TEMPLATE_SUFFIX, self.template_dirs)
        if tmp_file:
            response = self.render(tmp_file, {'url':local.request.path}, status=404)
        else:
            response = e
        return response
    
    def internal_error(self, e):
        tmp_file = template.get_templatefile('500'+settings.GLOBAL.TEMPLATE_SUFFIX, self.template_dirs)
        if tmp_file:
            response = self.render(tmp_file, {'url':local.request.path}, status=500)
        else:
            response = e
        log.exception(e)
        return response
    
    def get_env(self, env=None):
        e = Storage(self.env.copy())
        if env:
            e.update(env)
        return e
    
    def prepare_request(self, request, endpoint):
        from uliweb.utils.common import safe_import

        #get handler
        _klass = None
        if isinstance(endpoint, (str, unicode)):
            mod, handler = safe_import(endpoint)
            if inspect.ismethod(handler):
                if not handler.im_self:    #instance method
                    _klass = handler.im_class()
                else:                       #class method
                    _klass = handler.im_self()
                #if _klass is class method, then the mod should be Class
                #so the real mod should be mod.__module__
                mod = sys.modules[mod.__module__]
                
#            module, func = endpoint.rsplit('.', 1)
#            #if the module contains a class name, then import the class
#            #it set by expose()
#            x, last = module.rsplit('.', 1)
#            if last.startswith('views'):
#                mod = __import__(module, {}, {}, [''])
#                handler = getattr(mod, func)
#            else:
#                module = x
#                mod = __import__(module, {}, {}, [''])
#                _klass = getattr(mod, last)()
#                handler = getattr(_klass, func)
        elif callable(endpoint):
            handler = endpoint
            mod = sys.modules[handler.__module__]
        
        request.appname = ''
        for p in self.apps:
            t = p + '.'
            if handler.__module__.startswith(t):
                request.appname = p
                break
        request.function = handler.__name__
        if _klass:
            request.view_class = _klass.__class__.__name__
            handler = getattr(_klass, handler.__name__)
        else:
            request.view_class = None
        return mod, _klass, handler
    
    def call_view(self, mod, cls, handler, request, response=None, wrap_result=None, args=None, kwargs=None):
        #get env
        wrap = wrap_result or self.wrap_result
        env = self.get_view_env()
        
        #if there is __begin__ then invoke it, if __begin__ return None, it'll
        #continue running
        if hasattr(mod, '__begin__'):
            f = getattr(mod, '__begin__')
            result = self._call_function(f, request, response, env)
            if result is not None:
                return wrap(result, request, response, env)
        
        if hasattr(cls, '__begin__'):
            f = getattr(cls, '__begin__')
            result = self._call_function(f, request, response, env)
            if result is not None:
                return wrap(result, request, response, env)
        
        result = self.call_handler(handler, request, response, env, wrap, args, kwargs)

        result1 = None
        if hasattr(mod, '__end__'):
            f = getattr(mod, '__end__')
            result1, env = self._call_function(f, request, response, env)
            if result1 is not None:
                return wrap(result1, request, response, env)
        
        result1 = None
        if hasattr(cls, '__end__'):
            f = getattr(cls, '__end__')
            result1, env = self._call_function(f, request, response, env)
            if result1 is not None:
                return wrap(result1, request, response, env)

        return result
        
    def wrap_result(self, result, request, response, env):
#        #process ajax invoke, return a json response
#        if request.is_xhr and isinstance(result, dict):
#            result = json(result)

        if isinstance(result, dict):
            result = Storage(result)
            if hasattr(response, 'template'):
                tmpfile = response.template
            else:
                args = {'function':request.function, 'view_class':request.view_class, 'appname':request.appname}
                #TEMPLATE_TEMPLATE should be two elements tuple or list, the first one will be used for view_class is not empty
                #and the second one will be used for common functions
                if request.view_class:
                    tmpfile = settings.GLOBAL.TEMPLATE_TEMPLATE[0] % args + settings.GLOBAL.TEMPLATE_SUFFIX
                else:
                    tmpfile = settings.GLOBAL.TEMPLATE_TEMPLATE[1] % args + settings.GLOBAL.TEMPLATE_SUFFIX
                response.template = tmpfile
            content_type = response.content_type
            
            #if debug mode, then display a default_template
            if self.debug:
                d = ['default.html', self.default_template]
            else:
                d = None
            response.write(self.template(tmpfile, result, env, default_template=d))
        elif isinstance(result, (str, unicode)):
            response = Response(result, content_type='text/html')
        elif isinstance(result, (Response, BaseResponse)):
            response = result
        else:
            response = Response(str(result), content_type='text/html')
        return response
    
    def get_view_env(self):
        #prepare local env
        local_env = {}
        
        #process before view call
        dispatch.call(self, 'prepare_view_env', local_env, local.request)
        
        local_env['application'] = __global__.application
        local_env['request'] = local.request
        local_env['response'] = local.response
        local_env['url_for'] = url_for
        local_env['redirect'] = redirect
        local_env['error'] = error
        local_env['settings'] = __global__.settings
        local_env['json'] = json
        local_env['function'] = function
        local_env['functions'] = functions
        
        return self.get_env(local_env)
       
    def _call_function(self, handler, request, response, env, args=None, kwargs=None):
        
        for k, v in env.iteritems():
            handler.func_globals[k] = v
        
        handler.func_globals['env'] = env
        
        args = args or ()
        kwargs = kwargs or {}
        result = handler(*args, **kwargs)
        if isinstance(result, LocalProxy) and result._obj_name == 'response':
            result = local.response
        return result
    
    def call_handler(self, handler, request, response, env, wrap_result=None, args=None, kwargs=None):
        wrap = wrap_result or self.wrap_result
        result = self._call_function(handler, request, response, env, args, kwargs)
        return wrap(result, request, response, env)
            
    def collect_modules(self, check_view=True):
        modules = {}
        views = set()
        settings = []

        inifile = pkg.resource_filename('uliweb.core', 'default_settings.ini')
        settings.insert(0, inifile)
        
        def enum_views(views_path, appname, subfolder=None, pattern=None):
            for f in os.listdir(views_path):
                fname, ext = os.path.splitext(f)
                if os.path.isfile(os.path.join(views_path, f)) and ext in ['.py', '.pyc', '.pyo'] and fname!='__init__':
                    if pattern:
                        import fnmatch
                        if not fnmatch.fnmatch(f, pattern):
                            continue
                    if subfolder:
                        views.add('.'.join([appname, subfolder, fname]))
                    else:
                        views.add('.'.join([appname, fname]))

        for p in self.apps:
            path = get_app_dir(p)
            #deal with views
            if check_view:
                views_path = os.path.join(path, 'views')
                if os.path.exists(views_path) and os.path.isdir(views_path):
                    enum_views(views_path, p, 'views')
                else:
                    enum_views(path, p, pattern='views*')
            #deal with settings
            inifile =os.path.join(get_app_dir(p), 'settings.ini')
            
            if os.path.exists(inifile):
                settings.append(inifile)

        set_ini = os.path.join(self.apps_dir, self.settings_file)
        if os.path.exists(set_ini):
            settings.append(set_ini)
        
        local_set_ini = os.path.join(self.apps_dir, self.local_settings_file)
        if os.path.exists(local_set_ini):
            settings.append(local_set_ini)
        
        modules['views'] = list(views)
        modules['settings'] = settings
        return modules
    
    def install_views(self, views):
        for v in views:
            try:
                myimport(v)
            except Exception, e:
                log.exception(e)
         
    def init_urls(self):
        #initialize urls
        for v in rules.merge_rules():
            appname, endpoint, url, kw = v
            static = kw.pop('static', None)
            if static:
                static_views.append(endpoint)
            rules.add_rule(url_map, url, endpoint, **kw)
    
    def install_apps(self):
        for p in self.apps:
            try:
                myimport(p)
            except ImportError, e:
                pass
            except BaseException, e:
                log.exception(e)
            
    def install_settings(self, s):
#        settings = pyini.Ini()
        for v in s:
            settings.read(v)
        settings.update(self.default_settings)
        
        #process FILESYSTEM_ENCODING
        if not settings.GLOBAL.FILESYSTEM_ENCODING:
            settings.GLOBAL.FILESYSTEM_ENCODING = sys.getfilesystemencoding() or settings.GLOBAL.DEFAULT_ENCODING
            
    def install_binds(self):
        #process DISPATCH hooks
        #BINDS format
        #func = topic              #bind_name will be the same with function
        #bind_name = topic, func        
        #bind_name = topic, func, {args}
        d = settings.get('BINDS', {})
        for bind_name, args in d.iteritems():
            if not args:
                continue
            is_wrong = False
            if isinstance(args, (tuple, list)):
                if len(args) == 2:
                    dispatch.bind(args[0])(args[1])
                elif len(args) == 3:
                    if not isinstance(args[2], dict):
                        is_wrong = True
                    else:
                        dispatch.bind(args[0], **args[2])(args[1])
                else:
                    is_wrong = True
            elif isinstance(args, (str, unicode)):
                dispatch.bind(args)(bind_name)
            else:
                is_wrong = True
            if is_wrong:
                log.error('BINDS definition should be "function=topic" or "bind_name=topic, function" or "bind_name=topic, function, {"args":value1,...}"')
                raise UliwebError('BINDS definition [%s=%r] is not right' % (bind_name, args))
                
    def install_exposes(self):
        #EXPOSES format
        #endpoint = topic              #bind_name will be the same with function
        #expose_name = topic, func        
        #expose_name = topic, func, {args}
        d = settings.get('EXPOSES', {})
        for name, args in d.iteritems():
            if not args:
                continue
            is_wrong = False
            if isinstance(args, (tuple, list)):
                if len(args) == 2:
                    expose(args[0], name=name)(args[1])
                elif len(args) == 3:
                    if not isinstance(args[2], dict):
                        is_wrong = True
                    else:
                        expose(args[0], name=name, **args[2])(args[1])
                else:
                    is_wrong = True
            elif isinstance(args, (str, unicode)):
                expose(args)(name)
            else:
                is_wrong = True
            if is_wrong:
                log.error('EXPOSES definition should be "endpoint=url" or "name=url, endpoint" or "name=url, endpoint, {"args":value1,...}"')
                raise UliwebError('EXPOSES definition [%s=%r] is not right' % (name, args))
       
    def install_middlewares(self):
        #middleware process
        #middleware can be defined as
        #middleware_name = middleware_class_path[, order]
        #middleware_name = <empty> will be skip
        middlewares = []
        index = {}
        for middleware_name, v in settings.get('MIDDLEWARES', {}).iteritems():
            #process duplication of middleware, later will replace former
            if middleware_name in index:
                middlewares.pop(middleware_name)

            if not v:
                continue
            
            order = None
            if isinstance(v, (list, tuple)):
                if len(v) > 2:
                    raise UliwebError('Middleware %s difinition is not right' % middleware_name)
                middleware_path = v[0]
                if len(v) == 2:
                    order = v[1]
            else:
                middleware_path = v
            cls = import_attr(middleware_path)
            
            if order is None:
                order = getattr(cls, 'ORDER', 500)
            middlewares.append((order, cls))
            #remember the middleware index, so that can be used for easily remove
            index[middleware_name] = len(middlewares) - 1
        
        middlewares.sort(cmp=lambda x, y: cmp(x[0], y[0]))
            
        return [x[1] for x in middlewares]
    
    def get_template_dirs(self):
        """
        Get templates directory from apps, but in reversed order, so the same named template
        file will be overrided by latter defined app
        """
        template_dirs = [os.path.join(get_app_dir(p), 'templates') for p in reversed(self.apps)]
        return template_dirs
    
    def get_templateplugins_dirs(self):
        return [os.path.join(get_app_dir(p), 'template_plugins') for p in self.apps]
    
    def __call__(self, environ, start_response):
        local.request = req = Request(environ)
        local.response = res = Response(content_type='text/html')
        
        url_adapter = get_url_adapter('default')
        try:
            endpoint, values = url_adapter.match()
            mod, handler_cls, handler = self.prepare_request(req, endpoint)
            
            #process static
            if endpoint in static_views:
                response = self.call_view(mod, handler_cls, handler, req, res, kwargs=values)
            else:
                response = None
                _clses = {}
                _inss = {}

                for cls in self.middlewares:
                    if hasattr(cls, 'process_request'):
                        ins = cls(self, settings)
                        _inss[cls] = ins
                        response = ins.process_request(req)
                        if response is not None:
                            break
                
                if response is None:
                    try:
                        response = self.call_view(mod, handler_cls, handler, req, res, kwargs=values)
                        
                    except Exception, e:
                        for cls in reversed(self.middlewares):
                            if hasattr(cls, 'process_exception'):
                                ins = _inss.get(cls)
                                if not ins:
                                    ins = cls(self, settings)
                                response = ins.process_exception(req, e)
                                if response:
                                    break
                        raise
                        
                else:
                    response = res
                    
                for cls in reversed(self.middlewares):
                    if hasattr(cls, 'process_response'):
                        ins = _inss.get(cls)
                        if not ins:
                            ins = cls(self, settings)
                        response = ins.process_response(req, response)
                
            #endif
            
        except HTTPError, e:
            response = self.render(e.errorpage, Storage(e.errors))
        except NotFound, e:
            response = self.not_found(e)
        except HTTPException, e:
            response = e
        except Exception, e:
            if not self.settings.get_var('GLOBAL/DEBUG'):
                response = self.internal_error(e)
            else:
#                log.exception(e)
                raise
        return ClosingIterator(response(environ, start_response),
                               [local_manager.cleanup])

response = LocalProxy(local, 'response', Response)
request = LocalProxy(local, 'request', Request)
settings = LocalProxy(__global__, 'settings', pyini.Ini)
application = LocalProxy(__global__, 'application', Dispatcher)

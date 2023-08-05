#! /usr/bin/env python
#coding=utf-8

import re
import os
import StringIO
import cgi

__templates_temp_dir__ = 'tmp/templates_temp'
__options__ = {'use_temp_dir':False}
__nodes__ = {}   #user defined nodes

class TemplateException(Exception): pass
class ContextPopException(TemplateException):
    "pop() has been called more times than push()"
    pass

def use_tempdir(dir=''):
    global __options__, __templates_temp_dir__
    
    if dir:
        __templates_temp_dir__ = dir
        __options__['use_temp_dir'] = True
        if not os.path.exists(__templates_temp_dir__):
            os.makedirs(__templates_temp_dir__)

def set_options(**options):
    """
    default use_temp_dir=False
    """
    __options__.update(options)

def get_temp_template(filename):
    if __options__['use_temp_dir']:
        f, filename = os.path.splitdrive(filename)
        filename = filename.replace('\\', '_')
        filename = filename.replace('/', '_')
        f, ext = os.path.splitext(filename)
        filename = f + '.py'
        return os.path.normcase(os.path.join(__templates_temp_dir__, filename))
    return filename

def register_node(name, node):
    assert issubclass(node, Node)
    __nodes__[name] = node

def reindent(text):
    lines=text.split('\n')
    new_lines=[]
    credit=k=0
    for raw_line in lines:
        line=raw_line.strip()
        if not line or line[0]=='#':
            new_lines.append(line)
            continue
        if line[:5]=='elif ' or line[:5]=='else:' or    \
            line[:7]=='except:' or line[:7]=='except ' or \
            line[:7]=='finally:' or line[:5]=='with ':
                k=k+credit-1
        if k<0: k=0
        new_lines.append('    '*k+line)
        credit=0
        if line=='pass' or line[:5]=='pass ':
            credit=0
            k-=1
        if line=='return' or line[:7]=='return ' or \
            line=='continue' or line[:9]=='continue ' or \
            line=='break' or line[:6]=='break':
            credit=1
            k-=1
        if line[-1:]==':' or line[:3]=='if ':
            k+=1
    text='\n'.join(new_lines)
    return text

def get_templatefile(filename, dirs, default_template=None):
    if os.path.exists(filename):
        return filename
    if filename:
        if dirs:
            for d in dirs:
                path = os.path.join(d, filename)
                if os.path.exists(path):
                    return path
    if default_template:
        if isinstance(default_template, (list, tuple)):
            for i in default_template:
                f = get_templatefile(i, dirs)
                if f:
                    return f
        else:
            return get_templatefile(default_template, dirs)

def parse_arguments(text, key='with'):
    r = re.compile(r'\s+%s\s+' % key)
    k = re.compile(r'^\s*([\w][a-zA-Z_0-9]*\s*)=\s*(.*)')
    b = r.split(text)
    if len(b) == 1:
        name, args, kwargs = b[0], (), {}
    else:
        name = b[0]
        s = b[1].split(',')
        args = []
        kwargs = {}
        for x in s:
            ret = k.search(x)
            if ret:
                kwargs[ret.group(1)] = ret.group(2)
            else:
                args.append(x)
                
    return name, args, kwargs

def eval_vars(vs, vars, env):
    if isinstance(vs, (tuple, list)):
        return [eval_vars(x, vars, env) for x in vs]
    elif isinstance(vs, dict):
        return dict([(x, eval_vars(y, vars, env)) for x, y in vs.iteritems()])
    else:
        return eval(vs, vars, env)

r_tag = re.compile(r'(\{\{.*?\}\})', re.DOTALL|re.M)

class Node(object):
    block = 0
    var = False
    def __init__(self, value=None, content=None, template=None):
        self.value = value
        self.content = content
        self.template = template
        
    def __str__(self):
        return self.render()
        
    def render(self):
        if self.value:
            return self.value
        else:
            return ''
        
class BlockNode(Node):
    block = 1
    def __init__(self, name='', content=None, template=None):
        self.nodes = []
        self.name = name
        self.content = content
        self.template = template
        
    def add(self, node):
        self.nodes.append(node)
        
    def merge(self, content):
        self.nodes.extend(content.nodes)
    
    def output(self, vars):
        s = []
        for x in self.nodes:
            if isinstance(x, BlockNode):
                if x.name in vars:
                    s.append(vars[x.name].output(vars))
                else:
                    s.append(x.output(vars))
            else:
                s.append(str(x))
        return ''.join(s)
    
    def __repr__(self):
        s = ['{{block %s}}' % self.name]
        for x in self.nodes:
            s.append(str(x))
        s.append('{{end}}')
        return ''.join(s)
    
    def render(self):
        if self.name in self.content.vars and self is not self.content.vars[self.name]:
            return str(self.content.vars[self.name])
        else:
            s = []
            for x in self.nodes:
                if not x.__class__ is BlockNode:
                    s.append(str(x))
            return ''.join(s)

class Content(BlockNode):
    def __init__(self):
        self.nodes = []
        self.vars = {}
        self.begin = []
        self.end = []
        
    def add(self, node):
        self.nodes.append(node)
        if isinstance(node, BlockNode):
            self.vars[node.name] = node
        
    def merge(self, content):
        self.nodes.extend(content.nodes)
        self.vars.update(content.vars)
        
    def clear_content(self):
        self.nodes = []
    
    def __str__(self):
        s = self.begin[:]
        for x in self.nodes:
            if x.__class__ is BlockNode:
                if x.name in self.vars:
                    s.append(self.vars[x.name].output(self.vars))
                else:
                    s.append(x.output(self.vars))
            else:
                s.append(str(x))
        s.extend(self.end)
        return ''.join(s)
    
    def __repr__(self):
        s = []
        for x in self.nodes:
            s.append(str(x))
        return ''.join(s)

class Context(object):
    "A stack container for variable context"
    def __init__(self, dict_=None):
        dict_ = dict_ or {}
        self.dicts = [dict_]
        self.dirty = True
        self.result = None

    def __repr__(self):
        return repr(self.dicts)

    def __iter__(self):
        for d in self.dicts:
            yield d

    def push(self):
        d = {}
        self.dicts = [d] + self.dicts
        self.dirty = True
        return d

    def pop(self):
        if len(self.dicts) == 1:
            raise ContextPopException
        return self.dicts.pop(0)
        self.dirty = True

    def __setitem__(self, key, value):
        "Set a variable in the current context"
        self.dicts[0][key] = value
        self.dirty = True

    def __getitem__(self, key):
        "Get a variable's value, starting at the current context and going upward"
        for d in self.dicts:
            if key in d:
                return d[key]
        raise KeyError(key)

    def __delitem__(self, key):
        "Delete a variable from the current context"
        del self.dicts[0][key]
        self.dirty = True

    def has_key(self, key):
        for d in self.dicts:
            if key in d:
                return True
        return False

    __contains__ = has_key

    def get(self, key, otherwise=None):
        for d in self.dicts:
            if key in d:
                return d[key]
        return otherwise

    def update(self, other_dict):
        "Like dict.update(). Pushes an entire dictionary's keys and values onto the context."
        if not hasattr(other_dict, '__getitem__'): 
            raise TypeError('other_dict must be a mapping (dictionary-like) object.')
        self.dicts[0].update(other_dict)
#        self.dicts = [other_dict] + self.dicts
        self.dirty = True
        return other_dict
    
    def to_dict(self):
        if not self.dirty:
            return self.result
        else:
            d = {}
            for i in reversed(self.dicts):
                d.update(i)
            self.result = d
            self.dirty = False
        return d
        
__nodes__['block'] = BlockNode

class Out(object):
    encoding = 'utf-8'
    
    def __init__(self):
        self.buf = StringIO.StringIO()
        
    def _str(self, text):
        if not isinstance(text, (str, unicode)):
            text = str(text)
        if isinstance(text, unicode):
            return text.encode(self.encoding)
        else:
            return text

    def write(self, text, escape=True):
        s = self._str(text)
        if escape:
            self.buf.write(cgi.escape(s))
        else:
            self.buf.write(s)
            
    def xml(self, text):
        self.write(self._str(text), escape=False)
        
#    def json(self, text):
#        from datawrap import dumps
#        self.write(dumps(text))
#
    def getvalue(self):
        return self.buf.getvalue()

class Template(object):
    def __init__(self, text='', vars=None, env=None, dirs=None, 
        default_template=None, use_temp=False, compile=None, skip_error=False, encoding='utf-8'):
        self.text = text
        self.filename = None
        self.vars = vars or {}
        if not isinstance(env, Context):
            env = Context(env)
        self.env = env
        self.dirs = dirs or '.'
        self.default_template = default_template
        self.use_temp = use_temp
        self.compile = compile
        self.writer = 'out.write'
        self.content = Content()
        self.stack = [self.content]
        self.depend_files = []  #used for template dump file check
        self.callbacks = []
        self.exec_env = {}
        self.root = self
        self.skip_error = skip_error
        self.encoding = encoding
        
        for k, v in __nodes__.iteritems():
            if hasattr(v, 'init'):
                v.init(self)
        
    def add_callback(self, callback):
        if not callback in self.root.callbacks:
            self.root.callbacks.append(callback)
            
    def add_exec_env(self, name, obj):
        self.root.exec_env[name] = obj
        
    def add_root(self, root):
        self.root = root
        
    def set_filename(self, filename):
        fname = get_templatefile(filename, self.dirs, self.default_template)
        if not fname:
            raise TemplateException, "Can't find the template %s" % filename
        self.filename = fname
    
    def _get_parameters(self, value):
        def _f(*args, **kwargs):
            return args, kwargs
        d = self.env.to_dict()
        d['_f'] = _f
        try:
            args, kwargs = eval("_f(%s)" % value, self.vars, d)
        except:
            if self.skip_error:
                return (None,), {}
            else:
                raise
        return args, kwargs
    
    def parse(self):
        text = self.text
        in_tag = False
        extend = None  #if need to process extend node
        for i in r_tag.split(text):
            if i:
                if len(self.stack) == 0:
                    raise TemplateException, "The 'end' tag is unmatched, please check if you have more '{{end}}'"
                top = self.stack[-1]
                if in_tag:
                    line = i[2:-2].strip()
                    if not line:
                        continue
                    if line.startswith('T='):
                        name, value = 'T=', line[2:].strip()
                    elif line.startswith('T<<'):
                        name, value = 'T<<', line[3:].strip()
                    elif line.startswith('='):
                        name, value = '=', line[1:].strip()
                    elif line.startswith('<<'):
                        name, value = '<<', line[2:].strip()
                    else:
                        v = line.split(' ', 1)
                        if len(v) == 1:
                            name, value = v[0], ''
                        else:
                            name, value = v
                    if name in __nodes__:
                        node_cls = __nodes__[name]
                        #this will pass top template instance and top content instance to node_cls
                        node = node_cls(value.strip(), self.root.content, self.root)
                        if node.block:
                            top.add(node)
                            self.stack.append(node)
                        else:
                            buf = str(node)
                            if buf:
                                top.add(buf)
                    elif name == 'end':
                        self.stack.pop()
                    elif name == '=':
                        buf = "%s(%s)\n" % (self.writer, value)
                        top.add(buf)
                    elif name == 'BEGIN_TAG':
                        buf = "%s('{{')\n" % self.writer
                        top.add(buf)
                    elif name == 'END_TAG':
                        buf = "%s('}}')\n" % self.writer
                        top.add(buf)
                    elif name == '<<':
                        buf = "%s(%s, escape=False)\n" % (self.writer, value)
                        top.add(buf)
                    elif name == 'T=':
                        if not self._parse_template(top, value):
                            buf = "%s(%s)\n" % (self.writer, value)
                            top.add(buf)
                    elif name == 'T<<':
                        if not self._parse_template(top, value):
                            buf = "%s(%s, escape=False)\n" % (self.writer, value)
                            top.add(buf)
                    elif name == 'include':
                        self._parse_include(top, value)
                    elif name == 'embed':
                        self._parse_text(top, value)
                    elif name == 'extend':
                        extend = value
                    else:
                        if line and in_tag:
                            top.add(line+'\n')
                else:
                    buf = "%s(%r, escape=False)\n" % (self.writer, i)
                    top.add(buf)
                    
            in_tag = not in_tag
        if extend:
            self._parse_extend(extend)
        if self.encoding:
            pre = '#coding=%s\n' % self.encoding
        else:
            pre = ''
        return reindent(pre + str(self.content))
    
    def _parse_template(self, content, var):
        if var in self.vars:
            v = self.vars[var]
        else:
            return False
        
        #add v.__template__ support
        if hasattr(v, '__template__'):
            text = str(v.__template__(var))
            if text:
                t = Template(text, self.vars, self.env, self.dirs)
                t.parse()
                t.add_root(self)
                content.merge(t.content)
                return True
        
        return False

    def _parse_text(self, content, var):
        try:
            text = str(eval(var, self.vars, self.env.to_dict()))
        except:
            if self.skip_error:
                text = ''
            else:
                raise
        if text:
            t = Template(text, self.vars, self.env, self.dirs)
            t.parse()
            t.add_root(self)
            content.merge(t.content)
    
    def _parse_include(self, content, value):
        self.env.push()
        try:
            args, kwargs = self._get_parameters(value)
            filename = args[0]
            self.env.update(kwargs)
            fname = get_templatefile(filename, self.dirs)
            if not fname:
                raise TemplateException, "Can't find the template %s" % filename
            
            self.depend_files.append(fname)
            
            f = open(fname, 'rb')
            text = f.read()
            f.close()
            t = Template(text, self.vars, self.env, self.dirs)
            t.add_root(self)
            t.parse()
            content.merge(t.content)
        finally:
            self.env.pop()
        
    def _parse_extend(self, value):
        self.env.push()
        try:
            args, kwargs = self._get_parameters(value)
            filename = args[0]
            self.env.update(kwargs)
            fname = get_templatefile(filename, self.dirs)
            if not fname:
                raise TemplateException, "Can't find the template %s" % filename
            
            self.depend_files.append(fname)
            
            f = open(fname, 'rb')
            text = f.read()
            f.close()
            t = Template(text, self.vars, self.env, self.dirs)
            t.add_root(self)
            t.parse()
            self.content.clear_content()
            t.content.merge(self.content)
            self.content = t.content
        finally:
            self.env.pop()
            
    def get_parsed_code(self):
        if self.use_temp:
            f = get_temp_template(self.filename)
            if os.path.exists(f):
                fin = file(f, 'r')
                modified = False
                files = [self.filename]
                line = fin.readline()
                if line.startswith('#uliweb-template-files:'):
                    files.extend(line[1:].split())
                else:
                    fin.seek(0)
                
                for x in files:
                    if os.path.getmtime(x) > os.path.getmtime(f):
                        modified = True
                        break
                    
                if not modified:
                    text = fin.read()
                    fin.close()
                    return True, f, text
        
        if self.filename and not self.text:
            self.text = file(self.filename, 'rb').read()        
        return False, self.filename, self.parse()
        
    def __call__(self):
        use_temp_flag, filename, code = self.get_parsed_code()
        
        if not use_temp_flag and self.use_temp:
            f = get_temp_template(filename)
            try:
                fo = file(f, 'wb')
                fo.write('#uliweb-template-files:%s\n' % ' '.join(self.depend_files))
                fo.write(code)
                fo.close()
            except:
                pass
        
        return self._run(code, filename or 'template')
        
    def _run(self, code, filename):
        def f(_vars, _env):
            def defined(v, default=None):
                _v = default
                if v in _vars:
                    _v = _vars[v]
                elif v in _env:
                    _v = _env[v]
                return _v
            return defined

        e = {}
        if isinstance(self.env, Context):
            new_e = self.env.to_dict()
        else:
            new_e = self.env
        e.update(new_e)
        e.update(self.vars)
        out = Out()
        e['out'] = out
        e['Out'] = Out
        e['xml'] = out.xml
        e['_vars'] = self.vars
        e['defined'] = f(self.vars, self.env)
        e['_env'] = e
        
        e.update(self.exec_env)
        
        if isinstance(code, (str, unicode)):
            if self.compile:
                code = self.compile(code, filename, 'exec', e)
            else:
                code = compile(code, filename, 'exec')
        exec code in e
        text = out.getvalue()
        
        for f in self.callbacks:
            text = f(text, self, self.vars, e)

        return text
    
def template_file(filename, vars=None, env=None, dirs=None, default_template=None, compile=None):
    t = Template('', vars, env, dirs, default_template, use_temp=__options__['use_temp_dir'], compile=compile)
    t.set_filename(filename)
    return t()

def template(text, vars=None, env=None, dirs=None, default_template=None):
    t = Template(text, vars, env, dirs, default_template)
    return t()


def test():
    """
    >>> print template("Hello, {{=name}}", {'name':'uliweb'})
    Hello, uliweb
    >>> print template("Hello, {{ =name}}", {'name':'uliweb'})
    Hello, uliweb
    >>> print template("Hello, {{ = name}}", {'name':'uliweb'})
    Hello, uliweb
    >>> print template("Hello, {{=name}}", {'name':'<h1>Uliweb</h1>'})
    Hello, &lt;h1&gt;Uliweb&lt;/h1&gt;
    >>> print template("Hello, {{<<name}}", {'name':'<h1>Uliweb</h1>'})
    Hello, <h1>Uliweb</h1>
    >>> print template('''{{import datetime}}{{=datetime.date( # this breaks
    ...   2009,1,8)}}''')
    2009-01-08
    """

if __name__ == '__main__':
    print template("Hello, {{=name}}", {'name':'uliweb'})
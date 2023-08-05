from uliweb.core.html import Tag, begin_tag, end_tag

def safe_str(s, encoding='utf-8'):
    if isinstance(s, unicode):
        return s.encode(encoding)
    else:
        return s

class Build(object):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def to_html(self):
        raise NotImplementedError
    
    def pre_html(self):
        return ''
    
    def post_html(self):
        return ''
    
    def html(self):
        return ''.join([self.pre_html() % self.kwargs] + [self.to_html()] + 
            [self.post_html() % self.kwargs])

    def __str__(self):
        return self.html()

class Text(Build):
    type = 'text'

    def __init__(self, **kwargs):
        super(Text, self).__init__(**kwargs)

    def to_html(self):
        args = self.kwargs.copy()
        args.setdefault('type', self.type)
        return str(Tag('input', '', **args))

class Password(Text): type = 'password'
class TextArea(Build):
    def __init__(self, value='', **kwargs):
        self.value = value
        super(TextArea, self).__init__(**kwargs)

    def to_html(self):
        args = self.kwargs
        args.setdefault('rows', 5)
        args.setdefault('cols', 40)
        return str(Tag('textarea', self.value, **args))
class Hidden(Text): type = 'hidden'
class Button(Text): type = 'button'
class Submit(Text): type = 'submit'
class Reset(Text): type = 'reset'
class File(Text): type = 'file'
class Radio(Text): type = 'radio'
class Select(Build):
    def __init__(self, choices, value=None, multiple=False, size=10, **kwargs):
        self.choices = choices
        self.value = value
        self.multiple = multiple
        self.size = size
        super(Select, self).__init__(**kwargs)

    def to_html(self):
        from itertools import groupby
        
        def _make(v, caption):
            v = safe_str(v)
            args = {'value': v}
            if isinstance(self.value, (tuple, list)) and v in [safe_str(x) for x in self.value]:
                args['selected'] = None
            elif v == safe_str(self.value):
                args['selected'] = None
            return str(Tag('option', safe_str(caption), **args))
            
        s = []
        #if the choices is 3-elements, then will do the group process
        group = False
        if self.choices:
            group = len(self.choices[0]) > 2
        if group:
            for k, g in groupby(self.choices, lambda x:x[0]):
                s.append(begin_tag('optgroup', label=k))
                for x in g:
                    s.append(_make(x[1], x[2]))
                s.append(end_tag('optgroup'))
                
        else:
            for v, caption in self.choices:
                s.append(_make(v, caption))
                
        args = self.kwargs.copy()
        if self.multiple:
            args['multiple'] = None
            args['size'] = self.size
        return str(Tag('select', '\n'.join(s), **args))
    
class RadioSelect(Select):
    _id = 0
    def __init__(self, choices, value=None, **kwargs):
        super(RadioSelect, self).__init__(choices, value, **kwargs)

    def to_html(self):
        s = []
        for v, caption in self.choices:
            args = {'value': v}
            id = args.setdefault('id', 'radio_%d' % self.get_id())
            args['name'] = self.kwargs.get('name')
            if v == self.value:
                args['checked'] = None
            s.append(str(Radio(**args)))
            s.append(str(Tag('label', caption, _for=id)))
        return ''.join(s)
    
    def get_id(self):
        RadioSelect._id += 1
        return self._id
    
class Checkbox(Build):
    def __init__(self, value=False, **kwargs):
        self.value = value
        super(Checkbox, self).__init__(**kwargs)

    def to_html(self):
        args = self.kwargs.copy()
        if self.value:
            args.setdefault('checked', None)
        args.setdefault('type', 'checkbox')
        return str(Tag('input', '', **args))

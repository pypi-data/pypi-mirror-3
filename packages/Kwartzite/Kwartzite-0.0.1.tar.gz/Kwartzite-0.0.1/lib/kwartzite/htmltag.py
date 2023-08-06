###
### $Release: 0.0.1 $
### $Copyright: copyright(c) 2007-2011 kuwata-lab.com all rights reserved $
### $License: MIT License $
###


from kwartzite.util import escape_html


encoding = 'utf-8'


def to_str(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, unicode):
        return value.encode(encoding)
    return str(value)


class Tag(object):

    def __init__(self, name=None, attrs=None):
        if attrs is not None and not isinstance(attrs, dict):
            raise TypeError("%r: attrs should be a dict but got %s." % (attrs, type(attrs)))
        self.name = name
        self.attrs = attrs
        self.children = None

    def __call__(self, *children):
        if self.children is not None:
            raise ValueError("allowed to call only once.")
        self.children = children
        return self

    def __str__(self):
        esc = escape_html
        if self.name:
            tagname = esc(self.name)
            buf = ["<", esc(self.name)]
            append = buf.append
            extend = buf.extend
            if self.attrs:
                self._attrs2str(self.attrs, extend, esc)
            if self.children:
                append(">")
                self._children2str(self.children, append, esc)
                extend(("</", tagname, ">"))
            else:
                append(" />")
        else:
            tagname = None
            buf = []
            #if self.attrs:
            #    self._attrs2str(self.attrs, buf.extend, esc)
            if self.children:
                self._children2str(self.children, buf.append, esc)
        return "".join(buf)

    def _attrs2str(self, attrs, extend, esc):
        if attrs:
            for k in attrs:
                v = attrs[k]
                if v is None:
                    pass
                else:
                    extend((' ', esc(k), '="', esc(v), '"'))

    def _children2str(self, children, append, esc):
        _str = str
        _to_str = to_str
        for child in children:
            if isinstance(child, Tag):
                append(_str(child))
            else:
                append(esc(_to_str(child)))


class Html(object):

    def __getattr__(self, name):
        #def fn(attrs=None, **kwargs):
        #    return Tag(name, attrs, **kwargs)
        def fn(attrs=None, _name=name, **kwargs):
            if attrs is None:
                attrs = kwargs
            return Tag(_name, attrs)
        return fn

    def __call__(self, *args):
        return Tag(None)(*args)

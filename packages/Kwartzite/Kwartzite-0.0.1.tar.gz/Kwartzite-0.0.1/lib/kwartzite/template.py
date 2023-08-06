###
### $Release: 0.0.1 $
### $Copyright: copyright(c) 2007-2011 kuwata-lab.com all rights reserved $
### $License: MIT License $
###


from kwartzite import KwartziteError
from kwartzite.util import Bunch

__all__ = ('Template', 'Element', 'Attribute')



class Template(object):

    def render(self, context=None):
        if context is None: context = {}
        self.set_context(context)
        buf = []
        self.set_buffer(buf)
        self.create_document()
        return ''.join(buf)

    def create_document(self, buf, context=None):
        raise NotImplementedError(self.__class__.__name__ + "#create_document(): not implemented yet")

    def set_context(self, context):
        self._context = context
        self._bunch = Bunch(context)
        #self.__getitem__ = context.__getitem__
        #self.__setitem__ = context.__setitem__

    def __getitem__(self, name):
        #raise KwartziteError("'Template: []' is available only after render() is called.")
        return self._context[name]

    def __setitem__(self, name, value):
        #raise KwartziteError("Template: '[]=' is available only after render() is called.")
        self._context[name] = value

    def set_buffer(self, _buf):
        self._buf = _buf
        self._append = _buf.append
        self._extend = _buf.extend



class Element(object):

    text = None

    def __init__(self, attr, stag, cont, etag):
        self.attr = attr
        self.stag = stag
        self.cont = cont
        self.etag = etag

    def elem(self):
        self.stag()
        self.cont()
        self.etag()

    def __setitem__(self, key, value):
        self.attr[key] = value

    def __getitem__(self, key):
        return self.attr[key]



class Attribute(object):

    def __init__(self, pairs=()):
        if pairs is not None:
            self._names = names = []
            self._values = values = {}
            for k, v in pairs:
                names.append(k)
                values[k] = v

    def copy(self):
        obj = Attribute()
        obj._names = self._names[:]
        obj._values = self._values.copy()
        return obj

    def __getitem__(self, name):
        return self._values[name]

    def __setitem__(self, name, value):
        if name not in self._values:
            self._names.append(name)
        self._values[name] = value

    def __delitem__(self, name):
        del self._values[name]
        index = self._names.index(name)
        del self[index]

    def __contains__(self, name):
        return name in self._values

    def __iter__(self):
        values = self._values
        for name in self._names:
            yield name, values[name]

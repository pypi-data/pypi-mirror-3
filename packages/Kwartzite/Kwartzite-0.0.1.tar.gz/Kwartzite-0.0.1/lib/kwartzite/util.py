###
### $Release: 0.0.1 $
### $Copyright: copyright(c) 2007-2011 kuwata-lab.com all rights reserved $
### $License: MIT License $
###


import sys, os, re


_python2 = sys.version_info[0] == 2
_python3 = sys.version_info[0] == 3


if _python2:
    def is_string(value):
        """returns true if value is str or unicode."""
        return isinstance(value, (str, unicode))
    def is_unicode(value):
            """returns true if value is unicode."""
            return isinstance(value, unicode)
    def is_binary(value):
            """returns true if value is str."""
            return isinstance(value, str)
elif _python3:
    def is_string(value):
        """returns true if value is str or bytes."""
        return isinstance(value, (str, bytes))
    def is_unicode(value):
            """returns true if value is str."""
            return isinstance(value, str)
    def is_binary(value):
            """returns true if value is bytes."""
            return isinstance(value, bytes)
else:
    raise Exception("** unreachable **")


NULL = object()


def _super(self):
    """
    utility function which is more convenient than super().
    ex.
      class Parent(object):
          def message(self):
              print '* Parent class'
      class Child(Parent):
          def message(self):
              _super(self).message()   # equivarent to super(Child, self).message()
              print '* Chld class'
      Child().message()
    """
    return super(self.__class__, self)



def to_str(val):
    if val is None: return ''
    if is_string(val): return val
    return str(val)


def generate_tostrfunc(encoding):
    def to_str(val):
        if val is None: return ''
        if isinstance(val, str): return val
        if isinstance(val, unicode): return val.encode(encoding)
        return str(val)
    return to_str



_escape_table = { '<':'&lt;', '>':'&gt;', '&':'&amp;', '"':'&quot;', "'":'&#039;'}
_escape_callable = lambda m: _escape_table[m.group(0)]
_escape_pattern = re.compile(r'[<>&"]')

def escape_xml(string):
    return _escape_pattern.sub(_escape_callable, string)

h = escape_xml


def escape_html(string):
    return string.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def unescape_html(string):
    return string.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&apos;', "'")


_quote_table = { "'":"\\'", '"':'\\"', '\\':'\\\\' }
_quote_callable = lambda m: _quote_table[m.group(0)]
_quote_pattern = re.compile(r"['\\]")
_qquote_pattern = re.compile(r'["\\]')

def quote(string):
    return _quote_pattern.sub(_quote_callable, string)

def qquote(string):
    return _qquote_pattern.sub(_quote_callable, string)



_isword_pattern = re.compile('^\w+$')

def isword(s):
    return bool(_isword_pattern.match(s))



def camelize(string):
    return ''.join([ s[0].upper() + s[1:] for s in re.split(r'[^a-zA-Z0-9]', string) if s ])



def build_values_from_filename(filename):
    dirname, basename = os.path.split(filename)
    base, ext = os.path.splitext(basename)
    values = { 'b':base, 'x':ext[1:], 'd':dirname, 'f':basename,
               'u':re.sub(r'[^\w]', '_', base), }
    return values



def parse_name_pattern(pattern, values={}):
    """
    replace '%x' in pattern string with values['x'].
    if 'x' is upper then value is camelized.
    if 'x' is '%' then '%' is used. in other words, '%%' are replaced with '%'.
    ex.
      >>> values = {'c':'class', 'b':'base', 'f':'foo-bar-baz.html'}
      >>> parse_name_pattern('<%c><%%><%x><%F>', values)
      '<class><%><><FooBarBazHtml>'
    """
    i = pattern.find('%')
    if i < 0:
        return pattern
    n = len(pattern)
    buf = [ pattern[:i] ]
    while i < n:
        ch = pattern[i]
        if ch == '%':
            i += 1
            if i == n:
                buf.append('%')
                break
            ch = pattern[i]
            if   ch == '%':     val = '%'
            elif ch.isupper():  val = camelize(values.get(ch.lower()) or '')
            else:               val = values.get(ch) or ''
            if val:
                buf.append(val)
        else:
            buf.append(ch)
        i += 1
    return ''.join(buf)



class Bunch(object):


    def __init__(self, dictionary):
        self.__dict__ = dictionary



class OrderedDict(dict):


    def __init__(self, *args):
        dict.__init__(self, *args)
        self._keys = []


    def __setitem__(self, key, value):
        if key in self:
            self._keys.remove(key)
        self._keys.append(key)
        return dict.__setitem__(self, key, value)


    def keys(self):
        return self._keys[:]


    def __iter__(self):
        return self._keys.__iter__()


    def iteritems(self):
        return [ (k, self[k]) for k in self._keys ].__iter__()


    def __delitem__(self, key):
        if key in self:
            self._keys.remove(key)
        return dict.__delitem__(self, key)


    def clear(self):
        self._keys = []
        dict.clear(self)


    def copy(self):
        new = dict.copy(self)
        new._keys = self._keys[:]
        return new


    def pop(self, key):
        if key in self:
            self._keys.remove(key)
        return dict.pop(self, key)


    def popitem(self, key):
        if key in self:
            self._keys.remove(key)
        return dict.pop(self, key)


    def update(self, other):
        if other:
            for key, val in other.iteritems():
                self[key] = value



import kwartzite.config


def define_properties(tuple_list, _locals=None, **kwargs):
    if _locals is None:
        _locals = sys._getframe(1).f_locals
    config = kwartzite.config
    for t in tuple_list:
        name = t[0]
        value = getattr(config, name.upper(), None)
        if value is None and name in kwargs:
            value = kwargs[name]
        _locals[name] = value

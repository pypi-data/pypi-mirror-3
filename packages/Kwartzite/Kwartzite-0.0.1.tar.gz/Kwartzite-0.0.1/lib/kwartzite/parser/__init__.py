###
### $Release: 0.0.1 $
### $Copyright: copyright(c) 2007-2011 kuwata-lab.com all rights reserved $
### $License: MIT License $
###

import re

from kwartzite import KwartziteError
from kwartzite.util import escape_html, is_unicode, is_string



class Parser(object):


    filename = None


    def __init__(self, **properties):
        self.properties = properties


    def parse(self, input, filename=None, **kwargs):
        """parse input string and return TemplateInfo object."""
        raise NotImplementedError("%s#parser() is not implemented." % self.__class__.__name__)


    def parse_file(self, filename, **kwargs):
        """parse template file and return TemplateInfo object."""
        input = open(filename).read()
        return self.parse(input, filename, **kwargs)



class TemplateInfo(object):


    declaration = None


    def __init__(self, stmt_list, elem_table, filename=None):
        self.stmt_list  = self.pack(stmt_list)
        self.elem_table = elem_table
        self.filename   = filename
        for name, elem in self.elem_table.iteritems():
            if elem.cont:
                elem.cont = self.pack(elem.cont)


    def pack(self, stmt_list):
        if not stmt_list or len(stmt_list) == 1:
            return stmt_list
        pos = 0
        i = -1
        L = []
        for item in stmt_list:
            i += 1
            if is_string(item):
                pass
            else:
                if pos < i:
                    L.append(''.join(stmt_list[pos:i]))
                pos = i + 1
                L.append(item)
        if pos <= i:
            L.append(''.join(stmt_list[pos:]))
        new_stmt_list = L
        return new_stmt_list



class TagInfo(object):


    def __init__(self, tagname, attr, is_etag=None, is_empty=None, linenum=None,
                 string=None, head_space=None, tail_space=None, extra_space=None):
        self.name        = tagname
        self.attr        = AttrInfo(attr)
        self.is_etag     = is_etag and '/' or ''
        self.is_empty    = is_empty and '/' or ''
        self.linenum     = linenum
        self.string      = string
        self.head_space  = head_space
        self.tail_space  = tail_space
        self.extra_space = extra_space
        #if isinstance(attr, (str, unicode)):
        #    self.attr_str = attr
        #elif isinstance(attr, (tuple, list)):
        #    self.attr_str = ''.join([ ' %s="%s"' % (t[0], t[1]) for t in attr ])
        #elif isinstance(attr, dict):
        #    self.attr_str = ''.join([ ' %s="%s"' % (k, v) for k, v in attr.iteritems() ])
        #else:
        #    self.attr_str = attr


    def set_attr(self, attr):
        self.attr = attr
        self.rebuild_string(attr)


#    def rebuild_string(self, attr=None):
#        if attr:
#            buf = []
#            for space, name, value in attr:
#                buf.extend((space, name, '="', value, '"', ))
#            self.attr_str = ''.join(buf)
#        t = (self.head_space or '', self.is_etag and '</' or '<',
#             self.name, self.attr_str or '', self.extra_space or '',
#             self.is_empty and '/>' or '>', self.tail_space or '')
#        self.string = ''.join(t)
#        return self.string


    def clear_as_dummy_tag(self):      # delete <span> tag
        assert self.attr.is_empty()
        self.name = None
        if self.head_space is not None and self.tail_space is not None:
            self.head_space = self.tail_space = None


#    def _inspect(self):
#        return repr([ self.head_space, self.is_etag, self.name, self.attr_str,
#                      self.extra_space, self.is_empty, self.tail_space ])


    def _to_string(self):
        if self.name is None:
            return ''.join((self.head_space or '', self.tail_space or ''))
        buf = [self.head_space or '', self.is_etag and '</' or '<', self.name]
        for space, name, value in self.attr:
            buf.extend((space, name, '="', value, '"', ))
        buf.extend((self.extra_space or '', self.is_empty and '/>' or '>', self.tail_space or ''))
        return ''.join(buf)


    def to_string(self):
        if not self.string:
            self.string = self._to_string()
        return self.string


    #__repr__ = to_string
    def __repr__(self):
        buf = [self.head_space or '', self.is_etag and '</' or '<', self.name]
        for space, name, value in self.attr:
            buf.extend((space, name, '="', value, '"', ))
        if self.linenum is not None: buf.extend((' linenum="', str(self.linenum), '"'))
        buf.extend((self.extra_space or '', self.is_empty and '/>' or '>', self.tail_space or ''))
        return ''.join(buf)



class AttrInfo(object):


    def __init__(self, arg=None, escape=False):
        self.names  = names  = []
        self.values = values = {}
        self.spaces = spaces = {}
        if arg is not None:
            if is_string(arg):
                self.parse_str(arg)
            elif isinstance(arg, (tuple, list)):
                self.parse_tuples(arg)
            elif isinstance(arg, dict):
                self.parse_dict(arg)


    _pattern = re.compile(r'(\s+)([-:_\w]+)="([^"]*?)"')


    def parse_str(self, attr_str, escape=False):
        for m in AttrInfo._pattern.finditer(attr_str):
            space = m.group(1)
            name  = m.group(2)
            value = m.group(3)
            self.set(name, value, space, escape)


    def parse_tuples(self, tuples, escape=False):
        for t in tuples:
            n = len(t)
            if n == 2:
                name, value = t
                space = ' '
            elif n == 3:
                space, name, value = t
            else:
                assert False, "** t=%s" % repr(t)
            self.set(name, value, space, escape)


    def parse_dict(self, dictionary, escape=False):
        for name, value in dictionary.iteritems():
            self.set(name, value, ' ', escape)


    def has(self, name):
        return name in self.values


    def __getitem__(self, name):
        return self.values[name]


    def __setitem__(self, name, value):
        self.set(name, value, ' ')


    def get(self, name, default=None):
        return self.values.get(name, default)


    def set(self, name, value, space=' ', escape=False):
        if escape:
            name  = escape_html(name)
            value = escape_html(value)
        if name not in self.values:
            self.names.append(name)
            self.spaces[name] = space
        self.values[name] = value


    def __iter__(self):
        return [ (self.spaces[k], k, self.values[k]) for k in self.names ].__iter__()


    def delete(self, name):
        if self.has(name):
            self.names.remove(name)
            self.spaces.pop(name)
            return self.values.pop(name)
        return None


    def is_empty(self):
        return len(self.names) == 0



class ElementInfo(object):


    def __init__(self, stag, etag, cont_stmts, attr):
        self.stag = stag      # TagInfo
        self.etag = etag      # TagInfo
        self.cont = cont_stmts     # list of Statement
        self.attr = attr      # AttrInfo
        self.name = None
        self.directive = None


    def cont_text_p(self):
        L = self.cont
        return L and len(L) == 1 and is_string(L[0])
        #if not self.cont:
        #    return False
        #for item in self.cont:
        #    if not isinstance(item, (str, unicode)):
        #        return False
        #return True


    def to_list(self):
        buf = []; extend = buf.extend
        ## start tag
        stag = self.stag
        if stag.name:
            extend((stag.head_space or '', '<', stag.name))
            for space, name, value in stag.attr:
                if isinstance(value, Expression):
                    extend((space + name + '="', value, '"', ))
                else:
                    extend((space, name, '="', value, '"'))
            extend((stag.is_empty and ' />' or '>', stag.tail_space or ''))
        else:
            extend((stag.head_space or '', stag.tail_space or ''))
        #
        if not stag.is_empty:
            ## content
            assert isinstance(self.cont, list), "*** type(self.cont)=%s" % type(self.cont)
            extend(self.cont)
            ## end tag
            etag = self.etag
            if stag.name:
                extend((etag.head_space or '', '</', stag.name, '>', etag.tail_space or ''))
        return buf
        #
        #buf2 = []
        #i = 0
        #n = len(buf)
        #while i < n:
        #    j = i
        #    while j < n and not isinstance(buf[j], Expression):
        #        j += 1
        #    buf2.append(''.join(buf[i:j]))
        #    while j < n and isinstance(buf[j], Expression):
        #        buf2.append(buf[j])
        #        j += 1
        #    i = j
        #return buf2



class Expression(object):


    def __init__(self, code_str, name=None, kind='native'):
        self.code = code_str
        self.name = name
        self.kind = kind



class Directive(object):


    def __init__(self, directive_name, directive_arg, attr_name, attr_value, linenum=None):
        self.name       = directive_name
        self.arg        = directive_arg
        self.attr_name  = attr_name
        self.attr_value = attr_value
        self.linenum    = linenum


    def attr_string(self):
        return '%s="%s"' % (self.attr_name, self.attr_value)



class ParseError(KwartziteError):


    def __init__(self, message, filename=None, linenum=None, column=None):
        KwartziteError.__init__(self, message)
        self.filename = filename
        self.linenum = linenum
        self.column = column


    def to_string(self):
        "%s:%s:%s: %s: %s" % (self.filename, self.linenum, self.column,
                              self.__class__.__name__, self.message)

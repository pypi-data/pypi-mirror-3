###
### $Release: 0.0.1 $
### $Copyright: copyright(c) 2007-2011 kuwata-lab.com all rights reserved $
### $License: MIT License $
###


import re
from kwartzite.config import PythonTranslatorConfig
from kwartzite.util import quote, define_properties, unescape_html, is_string
from kwartzite.parser.TextParser import ElementInfo, Expression
from kwartzite.translator import Translator



def q(string):
    s = quote(string)
    if s.endswith("\r\n"):
        return s[0:-2] + "\\r\\n"
    if s.endswith("\n"):
        return s[0:-1] + "\\n"
    return s


def c(name):
    return re.sub(r'[^\w]+', '_', name)



class PythonTranslator(Translator, PythonTranslatorConfig):


    _property_descriptions = (
        ('classname' , 'str'  , 'classname pattern'),
        ('baseclass' , 'str'  , 'parent class name'),
        ('encoding'  , 'str'  , 'encoding name'),
        ('mainprog'  , 'bool' , 'define main program or not'),
        ('fragment'  , 'bool' , 'define element_xxx() and content_xxx()'),
        ('attrobj'   , 'bool' , 'use kwartzite.attribute.Attribute instead of dict'),
    )
    define_properties(_property_descriptions, baseclass='object', context=True)


    def __init__(self, classname=None, baseclass=None, encoding=None, mainprog=None, fragment=None, attrobj=None, **properties):
        Translator.__init__(self, **properties)
        if classname   is not None:  self.CLASSNAME = classname
        if baseclass   is not None:  self.BASECLASS = baseclass
        if encoding    is not None:  self.ENCODING  = encoding
        if mainprog    is not None:  self.MAINPROG  = mainprog
        if fragment    is not None:  self.FRAGMENT  = fragment
        if attrobj     is not None:  self.ATTROBJ   = attrobj


    def translate(self, template_info, **properties):
        stmt_list  = template_info.stmt_list
        elem_table = template_info.elem_table
        filename   = properties.get('filename') or template_info.filename
        classname  = properties.get('classname') or self.CLASSNAME
        classname = self.build_classname(filename, pattern=classname, **properties)
        buf = []
        extend = buf.extend
        #
        if self.ENCODING:
            extend(('# -*- coding: ', self.ENCODING, " -*-\n", ))
        if filename:
            extend(('## generated from ', filename, '\n', ))
        buf.append('\n')
        #
        extend((    'from kwartzite.template import Template, Element, Attribute\n', ))
        if self.ENCODING:
            extend(('from kwartzite.util import escape_html, generate_tostrfunc, Bunch\n'
                    'to_str = generate_tostrfunc(', repr(self.ENCODING), ')\n', ))
        else:
            extend(('from kwartzite.util import escape_html, to_str, Bunch\n', ))
        #
        extend((    '\n'
                    'class ', classname, '(', self.BASECLASS, '):\n'
                    '\n'
                    '    def __init__(self):\n'
                    ,))
        for name, elem in elem_table.iteritems():
            name = c(name)
            directive = elem.directive
            if directive.name == 'mark':
                extend((
                    '        self.', name, ' = Element(self._attr_', name, '.copy(),\n'
                    '             self.stag_', name, ', self.cont_', name, ', self.etag_', name, ')\n'
                    ,))
            else:
                assert False, "*** directive.name=%r" % (directive.name,)
        if not elem_table:
            extend(('        pass\n', ))
        extend((    '\n'
                   ,))
        #
        self.expand_utils(buf)
        #
        extend((    '    def create_document(self):\n'
                    '        _append = self._append\n'
                    '        _extend = self._extend\n'
                    ,))
        self.expand_stmt_list(buf, stmt_list)
        extend((    '\n'
                    ,))
        #
        for name, elem in elem_table.iteritems():
            extend(("\n"
                    "    ## element '", name, "'\n"
                    "\n"
                    ,))
            name = c(name)
            if elem.directive.name == 'mark':
                self.expand_init(buf, elem); buf.append("\n")
                self.expand_elem(buf, elem); buf.append("\n")
                self.expand_stag(buf, elem); buf.append("\n")
                self.expand_cont(buf, elem); buf.append("\n")
                self.expand_etag(buf, elem); buf.append("\n")
                if self.FRAGMENT:
                    self.expand_fragment(buf, elem); buf.append("\n")
            else:
                self.expand_init(buf, elem); buf.append("\n")
        #
        if self.MAINPROG:
            extend(("\n"
                    "# for test\n"
                    "if __name__ == '__main__':\n"
                    "    import sys\n"
                    "    sys.stdout.write(", classname, "().render())\n"
                    ,))
        return ''.join(buf)


    def expand_stmt_list(self, buf, stmt_list):
        def flush(L, buf):
            if not L:
                return
            elif len(L) == 1:
                buf.extend(("        _append(", L[0][:-2], ")\n", ))
            else:
                if L[-1].endswith('\n'):
                    L[-1] = L[-1][:-1] + ' '
                buf.append("        _extend((")
                buf.extend(L)
                buf.append("))\n")
            L[:] = ()
        L = []
        extend = buf.extend
        for item in stmt_list:
            if is_string(item):
                s = item.endswith('\n') and '\n' or ' '
                L.append("'''" + q(item) + "'''," + s)
            elif isinstance(item, ElementInfo):
                flush(L, buf)
                elem = item
                assert elem.directive.name == 'mark'
                extend(("        self.elem_", c(elem.name), "()\n", ))
            elif isinstance(item, Expression):
                expr = item
                assert expr.kind == 'native'
                L.append("escape_html(to_str(self._bunch." + expr.code + ")), ")
            else:
                assert False, "** unreachable"
        flush(L, buf)


    def expand_attr(self, buf, name):
        extend = buf.extend
        extend((    "        self._append_attr(self.", name, ".attr)\n"
            ,))


    def expand_init(self, buf, elem):
        name = c(elem.name)
        extend = buf.extend
        d_name = elem.directive.name
        ## _text_xxx
        if d_name in ('mark', ):
            if elem.cont_text_p():
                s = elem.cont[0]
                extend(("    _text_", name, " = '''", q(s), "'''\n", ))
            else:
                extend(("    _text_", name, " = None\n", ))
        ## _attr_xxx
        if d_name not in ('mark', ):
            pass
        elif not self.ATTROBJ:
            extend(('    _attr_', name, ' = ', ))
            attr = elem.attr
            if attr.is_empty():
                buf.append('{}\n')
            else:
                buf.append('{\n')
                u = unescape_html
                for space, aname, avalue in attr:
                    extend(("        '", q(u(aname)), "':'", q(u(avalue)), "',\n", ))
                buf.append('    }\n')
        else:
            extend(('    _attr_', name, ' = Attribute', ))
            attr = elem.attr
            if attr.is_empty():
                buf.append('()\n')
            else:
                buf.append('((\n')
                u = unescape_html
                for space, aname, avalue in attr:
                    extend(("        ('", q(u(aname)), "', '", q(u(avalue)), "'),\n", ))
                buf.append('    ))\n')


    def expand_elem(self, buf, elem):
        name = c(elem.name)
        buf.extend((
            '    def elem_', name, '(self):\n'
            '        self.', name, '.stag()\n'
            '        self.', name, '.cont()\n'
            '        self.', name, '.etag()\n'
            ,))


    def expand_stag(self, buf, elem):
        name = c(elem.name)
        extend = buf.extend
        stag = elem.stag
        extend((
            "    def stag_", name, "(self):\n"
            ,))
        if stag.name:
            extend((
            "        _append = self._append\n"
            "        _append('''", stag.head_space or "", "<", stag.name, "''')\n"
            ,))
            self.expand_attr(buf, name)
            extend((
            "        _append('''", stag.extra_space or "", stag.is_empty and "/>" or ">", q(stag.tail_space or ""), "''')\n"
            ,))
        else:
            s = (stag.head_space or '') + (stag.tail_space or '')
            if s:
                extend(("        self._append('", s, "')\n", ))
            else:
                extend(("        pass\n", ))


    def expand_cont(self, buf, elem):
        name = c(elem.name)
        extend = buf.extend
        extend((    '    def cont_', name, '(self):\n', ))
        if elem.cont_text_p():
            extend(('        if self.', name, '.text is not None:\n', ))
            extend(('            self._append(escape_html(to_str(self.', name, '.text)))\n', ))
            extend(('        else:\n', ))
            extend(('            self._append(self._text_', name, ')\n', ))
        else:
            extend(('        _append = self._append\n', ))
            extend(('        _extend = self._extend\n', ))
            self.expand_stmt_list(buf, elem.cont)


    def expand_etag(self, buf, elem):
        name = c(elem.name)
        extend = buf.extend
        etag = elem.etag
        extend((
            "    def etag_", name, "(self):\n"
            ,))
        if not etag:
            extend((
            "        pass\n"
            ,))
        elif etag.name:
            extend((
            "        self._append('''", etag.head_space or "", "</", etag.name,
                                 ">", q(etag.tail_space or ""), "''')\n"
            ,))
        else:
            s = (etag.head_space or '') + (etag.tail_space or '')
            if s:
                extend((
            "        self._append('", q(s), "')\n"
            ,))
            else:
                extend((
            "        pass\n"
            ,))


    def expand_fragment(self, buf, elem):
        name = c(elem.name)
        extend = buf.extend
        extend((
            "    def render_", name, "(self, context=None, flag_elem=True):\n"
            "        if context is None: context = {}\n"
            "        self.set_context(context)\n"
            "        self.set_buffer([])\n"
            "        if flag_elem:  self.elem_", name, "()\n"
            "        else:          self.cont_", name, "()\n"
            "        return ''.join(self._buf)\n"
            ,))


    def expand_utils(self, buf):
        extend = buf.extend
        extend((    '    def echo(self, value):\n'
                    '        self._append(escape_html(to_str(value)))\n'
                    '\n'
                    ,))
        #
        if self.ATTROBJ:
            extend(('    def _append_attr(self, attr):\n'
                    '        s = to_str\n'
                    '        e = escape_html\n'
                    '        _extend = self._buf.extend\n'
                    '        for k, v in attr:\n'
                    '            if v is not None:\n'
                    '                _extend((\' \', e(s(k)), \'="\', e(s(v)), \'"\'))\n'
                    '\n'
                    ,))
        else:
            extend(('    def _append_attr(self, attr):\n'
                    '        s = to_str\n'
                    '        e = escape_html\n'
                    '        _extend = self._buf.extend\n'
                    '        for k in attr:\n'
                    '            v = attr[k]\n'
                    '            if v is not None:\n'
                    '                _extend((\' \', e(s(k)), \'="\', e(s(v)), \'"\'))\n'
                    '\n'
                    ,))

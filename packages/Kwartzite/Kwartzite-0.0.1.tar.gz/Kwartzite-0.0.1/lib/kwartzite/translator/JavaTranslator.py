###
### $Release: 0.0.1 $
### $Copyright: copyright(c) 2007-2011 kuwata-lab.com all rights reserved $
### $License: MIT License $
###


import os, re
#import kwartzite.config as config
import kwartzite
from kwartzite.config import JavaTranslatorConfig
from kwartzite.util import qquote, define_properties, is_string
from kwartzite.parser.TextParser import ElementInfo, Expression
from kwartzite.translator import Translator


def q(string):
    s = qquote(string)
    L = []
    for line in s.splitlines(True):
        if line.endswith("\r\n"):  line = line[0:-2] + "\\r\\n"
        elif line.endswith("\n"):  line = line[0:-1] + "\\n"
        L.append(line)
    return '"\n             + "'.join(L)


def c(name, _rexp=re.compile(r'[-_]')):
    #return ''.join([ s.capitalize() for s in name.split('_') ])
    #return name.title().replace('_', '')
    return re.sub(r'[^a-zA-Z0-9]', '', name.title())
    #return ''.join(s[0:1].upper() + s[1:] for s in _rexp.split(name))


class JavaTranslator(Translator, JavaTranslatorConfig):

    _property_descriptions = (
        ('classname' , 'str'  , 'classname pattern'),
        ('baseclass' , 'str'  , 'parent class name'),
        ('interface' , 'str'  , 'interface name to implements'),
        ('package'   , 'str'  , 'package name'),
        ('encoding'  , 'str'  , 'encoding name'),
        ('mainprog'  , 'bool' , 'define main program or not'),
        ('fragment'  , 'bool' , 'define renderXxx()'),
    )
    define_properties(_property_descriptions)

    def __init__(self, classname=None, baseclass=None, interface=None, package=None, encoding=None, mainprog=None, fragment=None, **properties):
        if classname is not None:  self.CLASSNAME = classname
        if baseclass is not None:  self.BASECLASS = baseclass
        if interface is not None:  self.INTERFACE = interface
        if package   is not None:  self.PACKAGE   = package
        if encoding  is not None:  self.ENCODING  = encoding
        if mainprog  is not None:  self.MAINPROG  = mainprog
        if fragment  is not None:  self.FRAGMENT  = fragment

    def translate(self, template_info, **properties):
        stmt_list   = template_info.stmt_list
        elem_table  = template_info.elem_table
        declaration = template_info.declaration
        filename    = properties.get('filename') or template_info.filename
        classpat    = properties.get('classname') or self.CLASSNAME
        classname   = self.build_classname(filename, pattern=classpat, **properties)
        buf = []; _ = lambda *args: buf.extend(args)
        self._define_header(buf, filename)        ; _('\n')
        self._define_classdecl(buf, classname, declaration) ; _('\n')
        self._define_methods(buf, stmt_list)      ; _('\n')
        self._define_helpers(buf)                 ; _('\n')
        for name, elem in elem_table.iteritems():
            self._define_node(buf, elem)          ; _('\n')
        if self.MAINPROG:
            self._define_main(buf, classname)     ; _('\n')
        _(    '}\n')
        return ''.join(buf)

    def _to_java_expr(self, code):
        buf = []
        endpos = 0
        for m in re.finditer(r'(.*?)\.(\w+)(\(.*?\))?', code):
            if m.group(3):
                buf.append(m.group(0))
            else:
                prop = m.group(2)
                buf.extend((m.group(1), '.get', prop[0].upper(), prop[1:], "()"))
            endpos = m.end(0)
        buf.append(code[endpos:])
        return "".join(buf)

    def _define_header(self, buf, filename):
        _ = lambda *args: buf.extend(args)
        if self.ENCODING:
            _('// -*- coding: ', self.ENCODING, ' -*-\n')
        if filename:
            _('// generated from ', filename, ' by pykwartzite\n'
              '\n')
        if self.PACKAGE:
            _('package ', self.PACKAGE, ';\n'
              '\n')
        _(    'import java.util.Map;\n'
              #'import java.util.HashMap;\n'
              '\n'
              'import kwartzite.Template;\n'
              'import kwartzite.Elem;\n'
              'import kwartzite.Dom;\n'
              '\n')

    def _define_classdecl(self, buf, classname, declaration):
        _ = lambda *args: buf.extend(args)
        s = self.INTERFACE and ' implements ' + self.INTERFACE or ''
        _(    'public class ', classname, ' extends ', self.BASECLASS, s, ' {\n'
              '\n'
              '    // *** Begin Declaration ***\n',
              declaration or '    \n',
              '    // *** End Declaration ***\n'
              '\n'
              '\n'
              '    private StringBuilder _buf;\n'
              '\n'
              '    public ', classname, '(int bufsize) {\n'
              '        _buf = new StringBuilder(bufsize);\n'
              '    }\n'
              '\n'
              '    public ', classname, '() {\n'
              '        this(1024);\n'
              '    }\n'
              '\n')

    def _define_methods(self, buf, stmt_list):
        _ = lambda *args: buf.extend(args)
        _(    '    public String render() {\n'
              '        createDocument();\n'
              '        return _buf.toString();\n'
              '    }\n'
              '\n'
              #'    public String render(Map<String, Object> values) {\n'
              #'        context(values);\n'
              #'        return render();\n'
              #'    }\n'
              #'\n'
              #'    public void context(Map<String, Object> values) {\n'
              #'    }\n'
              #'\n'
              '    public void createDocument() {\n')
        self.expand_stmt_list(buf, stmt_list)
        _(    '    }\n'
              '\n')

    def expand_stmt_list(self, buf, stmt_list):
        def flush(L, buf):
            if L:
                buf.append('            _buf')
                for s in L:
                    buf.extend(('.append(', s, ')', ))
                buf.append(';\n')
                L[:] = ()
        L = []
        for item in stmt_list:
            if is_string(item):
                #s = item.endswith('\n') and '\n            ' or ''
                s = ''
                L.append('"' + q(item) + '"' + s)
            elif isinstance(item, ElementInfo):
                flush(L, buf)
                elem = item
                assert elem.directive.name == 'mark'
                #buf.extend(("            element", c(elem.name), "();\n", ))
                buf.extend(("            elem", c(elem.name), "();\n", ))
            elif isinstance(item, Expression):
                expr = item
                kind = expr.kind
                #if   kind == 'text':
                #    L.append("escape(elem" + c(expr.name) + ".text())")
                #elif kind == 'attr':
                #    flush(L, buf)
                #    buf.extend(("            elem", c(expr.name), ".attribute(attr", c(expr.name), ");\n", ))
                #elif kind == 'node':
                #    L.append("toStr(self.node" + c(expr.name) + ")")
                #elif kind == 'native':
                #    L.append("toStr(" + expr.code + ")")
                #else:
                #    assert False, "** unreachable"
                L.append("escape(" + self._to_java_expr(expr.code) + ")")
            else:
                assert False, "** unreachable"
        flush(L, buf)

    def _define_helpers(self, buf):
        _ = lambda *args: buf.extend(args)
        _(    '    public void echo(String arg)  {\n'
              '        if (arg == null) return;\n'
              '        _buf.append(escape(arg));\n'
              '    }\n'
              '    public void echo(Dom.Node arg)  {\n'
              '        if (arg == null) return;\n'
              '        _buf.append(arg.toHtml());\n'
              '    }\n'
              '    public void echo(Object arg) {\n'
              '        if (arg == null) return;\n'
              '        if (arg instanceof Dom.Node) {\n'
              #'            _buf.append(((Dom.Node)arg).toHtml());\n'
              '            echo((Dom.Node)arg);\n'
              '        }\n'
              '        else {\n'
              #'            _buf.append(escape(arg.toString()));\n'
              '            echo(arg.toString());\n'
              '        }\n'
              '    }\n'
              '    public void echo(int arg)     { _buf.append(arg); }\n'
              '    public void echo(double arg)  { _buf.append(arg); }\n'
              '    public void echo(char arg)    { _buf.append(arg); }\n'
              '    public void echo(char[] arg)  { _buf.append(arg); }\n'
              '    public void echo(boolean arg) { _buf.append(arg); }\n'
              '\n')

    def _define_node(self, buf, elem):
        _ = lambda *args: buf.extend(args)
        cname = c(elem.name)
        _(    '    ///\n'
              '    /// element \'', elem.name, '\'\n'
              '    ///\n'
              '\n')
        _(    '    protected Elem elem', cname, ' = new Elem() {\n'
              '        //protected Attrs  _attr = new Attrs();  // defined in Elem class\n'
              '        //protected Object _text = null;         // defined in Elem class\n'
              '\n')
        self._define_stag(buf, elem)
        self._define_cont(buf, elem)
        self._define_etag(buf, elem)
        _(    '    };\n'
              '\n')
        self._define_elem(buf, elem)
        if self.FRAGMENT:
            self._define_render(buf, elem)

    def _define_stag(self, buf, elem):
        _ = lambda *args: buf.extend(args)
        cname = c(elem.name)
        stag = elem.stag
        hspace = q(stag.head_space or '')
        espace = q(stag.extra_space or '')
        tspace = q(stag.tail_space or '')
        _(    '        public void stag() {\n')
        if stag.name:
            lt = stag.is_empty and '/>' or '>'
            attr_buf1 = []
            attr_buf2 = ['']
            for space, aname, avalue in elem.attr:
                attr_buf1.append('%s%s=\\"%s\\"' % (space, aname, avalue))
                attr_buf2.append('if (! _attrs.has("%s")) _buf.append("%s%s=\\"%s\\"");\n' % (aname, space, aname, avalue))
            attr_str = ''.join(attr_buf1)
            _('            if (_attrs.isEmpty()) {\n'
              '                _buf.append("', hspace, '<', stag.name, attr_str, espace, lt, tspace, '");\n'
              '            } else {\n'
              '                _buf.append("', hspace, '<', stag.name, '");\n')
            _('                '.join(attr_buf2))
            _('                appendAttrs(_attrs, _buf);\n'
              '                _buf.append("', espace, lt, tspace, '");\n'
              '            }\n')
        elif hspace or tspace:
            _('            _buf.append("', hspace, tspace, '");\n')
        _(    '        }\n')
        _(    '\n')

    def _define_cont(self, buf, elem):
        _ = lambda *args: buf.extend(args)
        cname = c(elem.name)
        _(    '        public void cont() {\n')
        #if elem.cont_text_p():
        #    _('            if (text', cname, ' != ', self.nullvalue, ')\n')
        #    _('                echo(text', cname, ');\n')
        #else:
        if True:
            _('            if (_text != null) {\n'
              '                echo(_text);\n'
              '                return;\n'
              '            }\n')
            if elem.cont:
                self.expand_stmt_list(buf, elem.cont)
        _(    '        }\n')
        _(    '\n')

    def _define_etag(self, buf, elem):
        _ = lambda *args: buf.extend(args)
        cname = c(elem.name)
        etag = elem.etag
        hspace = q(etag and etag.head_space or '')
        tspace = q(etag and etag.tail_space or '')
        _(    '        public void etag() {\n')
        if not etag:
            _('            //\n')
        elif etag.name:
            _('            _buf.append("', hspace, '</', etag.name, '>', tspace, '");\n')
        elif hspace or tspace:
            _('            _buf.append("', hspace, tspace, '");\n')
        else:
            _('            //\n')
        _(    '        }\n')
        _(    '\n')

    def _define_elem(self, buf, elem):
        _ = lambda *args: buf.extend(args)
        cname = c(elem.name)
        _(    #'    protected void element', cname, '() {\n'
              '    protected void elem', cname, '() {\n'
              '        elem', cname, '(this.elem', cname, ');\n'
              '    }\n'
              '    protected void elem', cname, '(Elem e) {\n'
              '        e.stag();\n'
              '        e.cont();\n'
              '        e.etag();\n'
              '    }\n'
              '\n')

    def _define_render(self, buf, elem):
        _ = lambda *args: buf.extend(args)
        cname = c(elem.name)
        _(    '    public String render', cname, '() {\n'
              '        return render', cname, '(true);\n'
              '    }\n'
              '    public String render', cname, '(boolean flagElem) {\n'
              '        _buf = new StringBuilder();\n'
              '        if (flagElem) this.elem', cname, '.elem();\n'
              '        else          this.elem', cname, '.cont();\n'
              '        return _buf.toString();\n'
              '    }\n'
              '\n')

    def _define_main(self, buf, classname):
        _ = lambda *args: buf.extend(args)
        _(    '    // for test\n'
              '    public static void main(String[] args) throws Exception {\n'
              '        System.out.print(new ', classname, '().render());\n'
              '    }\n'
              '\n')

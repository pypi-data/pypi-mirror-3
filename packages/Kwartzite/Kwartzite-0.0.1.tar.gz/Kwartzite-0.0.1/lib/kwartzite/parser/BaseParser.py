###
### $Release: 0.0.1 $
### $Copyright: copyright(c) 2007-2011 kuwata-lab.com all rights reserved $
### $License: MIT License $
###


import re
from kwartzite.config import ParserConfig
from kwartzite.util import isword, OrderedDict, define_properties
from kwartzite.parser import Parser, TemplateInfo, TagInfo, ElementInfo, AttrInfo, Expression, Directive, ParseError



class BaseParser(Parser, ParserConfig):


    _property_descriptions = (
        ('dattr'    , 'str'  , 'directive attribute name'),
        ('encoding' , 'str'  ,  'encoding name'),
        ('delspan'  , 'bool' , 'delete dummy <span> tag or not'),
    )
    define_properties(_property_descriptions)


    def __init__(self, dattr=None, encoding=None, delspan=None, escape=None, **properties):
        Parser.__init__(self, **properties)
        self.filename = None
        if dattr    is not None:  self.DATTR    = dattr
        if encoding is not None:  self.ENCODING = encoding
        if delspan  is not None:  self.DELSPAN  = delspan


    def _setup(self, input, filename):
        self.filename = filename
        self._elem_names = []
        self.elem_table = OrderedDict() # {}


    def _teardown(self):
        self.elem_table._keys = self._elem_names


    def parse(self, input, filename=''):
        self._setup(input, filename)
        stmt_list = []
        self._parse(stmt_list)
        self._teardown()
        return TemplateInfo(stmt_list, self.elem_table, filename)


    def _parse(self, stmt_list, start_tag=None):
        if start_tag:
            start_tagname = start_tag.name
            start_linenum = start_tag.linenum
        else:
            start_tagname = ""
            start_linenum = 1
        ##
        text, tag = self._fetch()
        while tag:
            ## prev text
            if text:
                stmt_list.append(text)
            ## end tag
            if tag.is_etag:
                if tag.name == start_tagname:
                    return tag
                else:
                    stmt_list.append(tag.to_string())
            ## empty tag
            elif tag.is_empty or self._skip_etag_p(tag.name):
                directives = self._get_directives(tag)   # data-kw="..."
                if directives:
                    self._add_elem_names_if_marking_directive(directives)
                    stag = tag
                    cont = []
                    etag = None
                    elem = self._create_elem(stag, etag, cont, tag.attr)
                    self._handle_directives(directives, elem, stmt_list, tag.linenum)
                else:
                    stmt_list.append(tag.to_string())
            ## start tag
            else:
                directives = self._get_directives(tag)   # data-kw="..."
                if directives:
                    self._add_elem_names_if_marking_directive(directives)
                    stag = tag
                    cont = []
                    etag = self._parse(cont, stag)
                    elem = self._create_elem(stag, etag, cont, tag.attr)
                    self._handle_directives(directives, elem, stmt_list, tag.linenum)
                elif tag.name == start_tagname:
                    stag = tag
                    stmt_list.append(stag.to_string())
                    etag = self._parse(stmt_list, stag)  # recursive call
                    stmt_list.append(etag.to_string())
                else:
                    stmt_list.append(tag.to_string())
            ## continue while-loop
            text, tag = self._fetch()
        ## control flow reaches here only if _parse() is called by parse()
        if start_tag:
            msg = "'<%s>' is not closed." % start_tagname
            raise self._parse_error(msg, start_tag.linenum)
        if text:
            stmt_list.append(text)
        return None


    def _add_elem_names_if_marking_directive(self, directives):
        is_markings = ('mark', )
        for directive in directives:
            if directive.name in is_markings:
                elem_name = directive.arg
                self._elem_names.append(elem_name)


    def _parse_error(self, msg, linenum, column=None):
        return ParseError(msg, self.filename, linenum, column)


    def _create_elem(self, stag, etag, cont, attr):
        elem = ElementInfo(stag, etag, cont, attr)
        if self.DELSPAN and elem.stag.name == 'span' and elem.attr.is_empty():
            elem.stag.clear_as_dummy_tag()
            if elem.etag:
                elem.etag.clear_as_dummy_tag()
        return elem


    _skip_etag_table = dict([ (tagname, True) for tagname in ParserConfig.NO_ETAGS ])


    def _skip_etag_p(self, tagname):
        return BaseParser._skip_etag_table.get(tagname) and True or False


    def _get_directives(self, tag):
        if not tag.attr.has(self.DATTR):        # data-kw="..."
            return None
        dattr = tag.attr.get(self.DATTR)
        tag.attr.delete(self.DATTR)
        tag.string = None #tag.rebuild_string(attr)
        directives = []
        for value in re.split(r';\s*', dattr):
            m = re.match(r'(\w+):(.*)', value)
            if m:
                name, arg = m.groups()
                directive = Directive(name, arg, self.DATTR, value)
            elif re.match(r'\w+$', dattr):
                directive = Directive('mark', value, self.DATTR, value)
            else:
                msg = "%s=\"%s\": invalid directive." % (self.DATTR, value)
                raise self._parse_error(msg, tag.linenum)
            directive.linenum = tag.linenum
            directives.append(directive)
        return directives


    def _handle_directives(self, directives, elem, stmt_list, linenum):
        flag_elem = False
        flag_list = False
        for d in directives:
            func = getattr(self, '_handle_directive_%s' % d.name, None)
            if not func:
                msg = '%s="%s": unknown directive.' % (d.attr_name, d.attr_value)
                raise self._parse_error(msg, d.linenum)
            is_empty_tag = elem.stag.is_empty
            if is_empty_tag and d.name in ('text', ):
                msg = '%s="%s": not available with empty tag.' % (d.attr_name, d.attr_value)
                raise self._parse_error(msg, d.linenum)
            elem.directive = d
            flag = func(d, elem, stmt_list)
            if   flag is True:  flag_elem = True     # 'mark:'
            elif flag is False: flag_list = True     # 'text:' or 'attr:'
            else:               pass                 # 'dummy:'
        if   flag_elem: stmt_list.append(elem)
        elif flag_list: stmt_list.extend(elem.to_list())


    def _handle_directive_mark(self, directive, elem, stmt_list):
        d = directive
        name = d.arg
        if not re.match(r'^[-.\w]+$', name):
            msg = '%s="%s": invalid marking name.' % (d.attr_name, d.attr_value)
            raise self._parse_error(msg, d.linenum)
        #
        if not re.match(r'^[a-zA-Z_]', name):
            msg = '%s="%s": marking name should be start with alphabet or \'_\'.' % (d.attr_name, d.attr_value)
            raise self._parse_error(msg, d.linenum)
        #
        e = self.elem_table.get(name)
        if e:
            msg = '%s="%s": marking name duplicated (at line %s).' % (d.attr_name, d.attr_value, d.linenum)
            raise self._parse_error(msg, d.linenum)
        #
        name = directive.arg
        elem.name = name
        self.elem_table[name] = elem
        return True


    def _handle_directive_text(self, directive, elem, stmt_list):
        code = directive.arg
        elem.cont = [Expression(code)]
        return False


    def _handle_directive_attr(self, directive, elem, stmt_list):
        m = re.match('^(\w+(?::\w+)?)=(.*)', directive.arg)
        if not m:
            msg = "'attr:" + directive.arg + "': invalid attr directive."
            raise self._parse_error(msg, directive.linenum)
        aname, code = m.groups()
        elem.attr[aname] = Expression(code)
        return False


    def _handle_directive_dummy(self, directive, elem, stmt_list):
        return None   # ignore element

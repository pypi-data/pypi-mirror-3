###
### $Release: 0.0.1 $
### $Copyright: copyright(c) 2007-2011 kuwata-lab.com all rights reserved $
### $License: MIT License $
###

import sys, unittest
import oktest
from oktest import ok, NG, test

from kwartzite.parser import TemplateInfo, ElementInfo, TagInfo, Expression, Directive, ParseError
from kwartzite.parser.BaseParser import BaseParser
from kwartzite.parser.TextParser import TextParser



class BaseParser_TC(unittest.TestCase):


    @test("directive 'mark:' takes an element name.")
    def _(self):
        input = r"""
<table>
  <tr class="odd" data-kw="mark:list1">
    <td data-kw="mark:item1">foo</td>
  </tr>
</table>
"""[1:]
        self._marking_directives_are_handled_correctly(input)


    @test("directive 'mark:' allows to omit prefix (='mark:').")
    def _(self):
        input = r"""
<table>
  <tr class="odd" data-kw="list1">
    <td data-kw="item1">foo</td>
  </tr>
</table>
"""[1:]
        self._marking_directives_are_handled_correctly(input)


    def _marking_directives_are_handled_correctly(self, input):
        template_info = TextParser().parse(input)
        ok (template_info.elem_table).contains('list1')
        ok (template_info.elem_table).contains('item1')
        stmt_list = template_info.stmt_list
        ok (stmt_list).is_a(list).length(3)
        ok (stmt_list[0]) == "<table>\n"
        ok (stmt_list[1]).is_a(ElementInfo).attr('name', 'list1')
        ok (stmt_list[2]) == "</table>\n"


    @test("raises error when invalid name is specified in 'mark:'.")
    def _(self):
        def parse(marking):
            TextParser().parse("""<b data-kw="mark:%s">foo</b>""" % marking)
        ok (lambda s="user_name": parse(s)).not_raise()
        ok (lambda s="user-name": parse(s)).not_raise()
        ok (lambda s="user.name": parse(s)).not_raise()
        ok (lambda s="_username": parse(s)).not_raise()
        #
        ok (lambda s="$foo": parse(s)).raises(ParseError, 'data-kw="mark:$foo": invalid marking name.')
        ok (lambda s="foo[]": parse(s)).raises(ParseError, 'data-kw="mark:foo[]": invalid marking name.')
        #
        ok (lambda s="-foo": parse(s)).raises(ParseError, 'data-kw="mark:-foo": marking name should be start with alphabet or \'_\'.')
        ok (lambda s="0foo": parse(s)).raises(ParseError, 'data-kw="mark:0foo": marking name should be start with alphabet or \'_\'.')


    @test("directive 'text:' takes an expression as content.")
    def _(self):
        input = r"""
<p><b data-kw="text:item.name">foo</b></p>
"""[1:]
        template_info = TextParser().parse(input)
        stmt_list = template_info.stmt_list
        ok (stmt_list).is_a(list).length(3)
        ok (stmt_list[0]) == "<p><b>"
        ok (stmt_list[1]).is_a(Expression)
        ok (stmt_list[2]) == "</b></p>\n"
        expr = stmt_list[1]
        ok (expr).attr('code', 'item.name').attr('kind', 'native').attr('name', None)


    @test("directive 'attr:' takes name and expression as attribute value.")
    def _(self):
        input = r"""
<p><a data-kw="attr:href=item.url">foo</a></p>
"""[1:]
        template_info = TextParser().parse(input)
        stmt_list = template_info.stmt_list
        ok (stmt_list).is_a(list).length(3)
        ok (stmt_list[0]) == '<p><a href="'
        ok (stmt_list[1]).is_a(Expression)
        ok (stmt_list[2]) == '">foo</a></p>\n'
        expr = stmt_list[1]
        ok (expr).attr('code', 'item.url').attr('kind', 'native').attr('name', None)


    @test("directive 'attr:' raises error when invalid directive pattern.")
    def _(self):
        input = r"""
<p><a data-kw="attr:item.url">foo</a></p>
"""[1:]
        def fn(): TextParser().parse(input)
        ok (fn).raises(ParseError, "'attr:item.url': invalid attr directive.")


    @test("directive 'text:' and 'attr:' are available in an attribute.")
    def _(self):
        input = r"""
<p><a data-kw="attr:href=item.url;text:item.name" class="link">foo</a></p>
"""[1:]
        template_info = TextParser().parse(input)
        stmt_list = template_info.stmt_list
        ok (stmt_list).is_a(list).length(5)
        ok (stmt_list[0]) == '<p><a class="link" href="'
        ok (stmt_list[1]).is_a(Expression)
        ok (stmt_list[2]) == '">'
        ok (stmt_list[3]).is_a(Expression)
        ok (stmt_list[4]) == '</a></p>\n'
        expr = stmt_list[1]
        ok (expr).attr('code', 'item.url').attr('kind', 'native').attr('name', None)
        expr = stmt_list[3]
        ok (expr).attr('code', 'item.name').attr('kind', 'native').attr('name', None)


    @test("directive 'text:' and 'attr:' are available with 'mark:'.")
    def _(self):
        input = r"""
<p><a data-kw="attr:href=item.url;mark:anchor;text:item.name" class="link">foo</a></p>
"""[1:]
        template_info = TextParser().parse(input)
        stmt_list = template_info.stmt_list
        ok (stmt_list).is_a(list).length(3)
        ok (stmt_list[0]) == '<p>'
        ok (stmt_list[1]).is_a(ElementInfo)
        ok (stmt_list[2]) == '</p>\n'
        elem = stmt_list[1]
        ok (elem.stag.name) == 'a'
        ok (elem.stag.attr['href']).is_a(Expression)
        expr = elem.stag.attr['href']
        ok (expr).attr('code', 'item.url').attr('kind', 'native').attr('name', None)
        ok (elem.cont).is_a(list).length(1)
        ok (elem.cont[0]).is_a(Expression)
        expr = elem.cont[0]
        ok (expr).attr('code', 'item.name').attr('kind', 'native').attr('name', None)


    @test("directive 'dummy:' ignores element.")
    def _(self):
        input = r"""
<p><a data-kw="dummy:d1">foo</a></p>
"""[1:]
        template_info = TextParser().parse(input)
        stmt_list = template_info.stmt_list
        ok (stmt_list).is_a(list).length(1)
        ok (stmt_list[0]) == '<p></p>\n'


    @test("#parse() throws ParserError when directive is invalid.")
    def _(self):
        input = r"""
<div>
  <span data-kw="mark=items"></span>
</div>
"""[1:]
        parser = TextParser()
        def fn(): parser.parse(input, "test.html")
        ok (fn).raises(ParseError, 'data-kw="mark=items": invalid directive.')


    @test("marking name should be a word.")
    def _(self):
        input = r"""
<div>
  <span data-kw="mark: foo"></span>
</div>
"""[1:]
        parser = TextParser()
        def fn(): parser.parse(input)
        ok (fn).raises(ParseError, 'data-kw="mark: foo": invalid marking name.')


    @test("marking name should be start with alphabet or '_'.")
    def _(self):
        input = r"""
<div>
  <span data-kw="mark:123"></span>
</div>
"""[1:]
        parser = TextParser()
        def fn(): parser.parse(input)
        ok (fn).raises(ParseError, 'data-kw="mark:123": marking name should be start with alphabet or \'_\'.')


    @test("marking name should not be duplicated in a template.")
    def _(self):
        input = r"""
<div>
  <span data-kw="mark:name"></span>
  <span data-kw="mark:name"></span>
</div>
"""[1:]
        parser = TextParser()
        def fn(): parser.parse(input)
        ok (fn).raises(ParseError, 'data-kw="mark:name": marking name duplicated (at line 3).')



if __name__ == '__main__':
    oktest.run()

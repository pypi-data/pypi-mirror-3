###
### $Release: 0.0.1 $
### $Copyright: copyright(c) 2007-2011 kuwata-lab.com all rights reserved $
### $License: MIT License $
###

import sys, unittest
import oktest
from oktest import ok, NG, test

from kwartzite.parser import TemplateInfo, ElementInfo, TagInfo, Directive
from kwartzite.parser.XmlParser import XmlParser



class XmlParser_TC(unittest.TestCase):


    @test("#parse() parses html string.")
    def _(self):
        input = r"""
<div>
  <ul data-kw="mark:items">
    <!-- comment -->
    <li data-kw="mark:item">foo</li>
  </ul>
</div>
"""[1:]
        parser = XmlParser()
        ret = parser.parse(input, "test.html")
        #
        ok (ret).is_a(TemplateInfo)
        #
        ok (ret.declaration).is_(None)
        ok (ret.filename) == "test.html"
        #
        ok (ret.stmt_list).is_a(list).length(3)
        ok (ret.stmt_list[0]) == "<div>\n  "
        ok (ret.stmt_list[1]).is_a(ElementInfo)
        ok (ret.stmt_list[2]) == "\n</div>\n"
        #
        ok (ret.elem_table).is_a(dict).length(2).contains('items').contains('item')
        ok (ret.elem_table['items']).is_a(ElementInfo).attr('name', 'items')
        ok (ret.elem_table['item']).is_a(ElementInfo)
        #
        ok (ret.elem_table['items'].stag).is_a(TagInfo).attr('name', 'ul').attr('linenum', 2)
        ok (ret.elem_table['items'].etag).is_a(TagInfo).attr('name', 'ul').attr('linenum', 5)
        ok (ret.elem_table['items'].cont).is_a(list).length(3)
        ok (ret.elem_table['items'].cont[0]) == "\n    <!-- comment -->\n    "
        ok (ret.elem_table['items'].cont[1]).is_(ret.elem_table['item'])
        ok (ret.elem_table['items'].cont[2]) == "\n  "
        #
        ok (ret.elem_table['item'].stag).is_a(TagInfo).attr('name', 'li').attr('linenum', 4)
        ok (ret.elem_table['item'].etag).is_a(TagInfo).attr('name', 'li').attr('linenum', 4)
        ok (ret.elem_table['item'].cont) == ["foo"]



if __name__ == '__main__':
    oktest.run()

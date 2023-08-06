###
### $Release: 0.0.1 $
### $Copyright: copyright(c) 2007-2011 kuwata-lab.com all rights reserved $
### $License: MIT License $
###

import sys, unittest
import oktest
from oktest import ok, NG, test

from kwartzite.parser.TextParser import Directive
from kwartzite.parser.ElementTreeParser import ElementTreeParser



class ElementTreeParser_TC(unittest.TestCase):


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
        parser = ElementTreeParser()
        ret = parser.parse(input, "test.html")
        #
        ok (ret).is_a(tuple).length(3)
        xmldoc, elem_table, filename = ret
        ok (filename) == "test.html"
        #
        try:
            ## cElementTree.XMLParser doesn't support 'doctype' handler
            #import xml.etree.cElementTree as ET
            import xml.etree.ElementTree as ET
        except ImportError:
            import elementtree.ElementTree as ET
        ok (xmldoc).is_a(ET.ElementTree)
        #
        ok (elem_table).is_a(dict).length(2)
        for k, v in elem_table.items():
            ok (v).is_a(tuple).length(2)
            ok (v[1]).is_a(Directive)
            elem, directive = v
            #ok (elem).is_a(ET.Element)      # TODO
            ok (directive).is_a(Directive)
            ok (id(elem)) == k



if __name__ == '__main__':
    oktest.run()

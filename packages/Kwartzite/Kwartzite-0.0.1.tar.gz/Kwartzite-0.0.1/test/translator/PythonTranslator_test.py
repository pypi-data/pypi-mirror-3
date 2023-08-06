###
### $Release: 0.0.1 $
### $Copyright: copyright(c) 2007-2011 kuwata-lab.com all rights reserved $
### $License: MIT License $
###

import sys, re, unittest
import oktest
from oktest import ok, NG, test

from kwartzite.parser.TextParser import TextParser
from kwartzite.translator.PythonTranslator import PythonTranslator
from kwartzite import util



class PythonTranslator_TC(unittest.TestCase):


    INPUT = r"""
<!doctype html>
<div>
  <ul data-kw="mark:items" class="list">
    <!-- comment -->
    <li data-kw="mark:item">foo</li>
  </ul>
</div>
"""[1:]


    TRANSLATED = r"""
## generated from views/test.html

from kwartzite.template import Template, Element, Attribute
from kwartzite.util import escape_html, to_str, Bunch

class TestHtml_(Template):

    def __init__(self):
        self.items = Element(self._attr_items.copy(),
             self.stag_items, self.cont_items, self.etag_items)
        self.item = Element(self._attr_item.copy(),
             self.stag_item, self.cont_item, self.etag_item)

    def echo(self, value):
        self._append(escape_html(to_str(value)))

    def _append_attr(self, attr):
        s = to_str
        e = escape_html
        _extend = self._buf.extend
        for k, v in attr:
            if v is not None:
                _extend((' ', e(s(k)), '="', e(s(v)), '"'))

    def create_document(self):
        _append = self._append
        _extend = self._extend
        _append('''<!doctype html>
<div>\n''')
        self.elem_items()
        _append('''</div>\n''')


    ## element 'items'

    _text_items = None
    _attr_items = Attribute((
        ('class', 'list'),
    ))

    def elem_items(self):
        self.items.stag()
        self.items.cont()
        self.items.etag()

    def stag_items(self):
        _append = self._append
        _append('''  <ul''')
        self._append_attr(self.items.attr)
        _append('''>\n''')

    def cont_items(self):
        _append = self._append
        _extend = self._extend
        _append('''    <!-- comment -->\n''')
        self.elem_item()

    def etag_items(self):
        self._append('''  </ul>\n''')

    def render_items(self, context=None, flag_elem=True):
        if context is None: context = {}
        self.set_context(context)
        self.set_buffer([])
        if flag_elem:  self.elem_items()
        else:          self.cont_items()
        return ''.join(self._buf)


    ## element 'item'

    _text_item = '''foo'''
    _attr_item = Attribute()

    def elem_item(self):
        self.item.stag()
        self.item.cont()
        self.item.etag()

    def stag_item(self):
        _append = self._append
        _append('''    <li''')
        self._append_attr(self.item.attr)
        _append('''>''')

    def cont_item(self):
        if self.item.text is not None:
            self._append(escape_html(to_str(self.item.text)))
        else:
            self._append(self._text_item)

    def etag_item(self):
        self._append('''</li>\n''')

    def render_item(self, context=None, flag_elem=True):
        if context is None: context = {}
        self.set_context(context)
        self.set_buffer([])
        if flag_elem:  self.elem_item()
        else:          self.cont_item()
        return ''.join(self._buf)


# for test
if __name__ == '__main__':
    import sys
    sys.stdout.write(TestHtml_().render())
"""[1:]


    @test("#translate() translates TemplateInfo into Python code.")
    def _(self):
        template_info = TextParser().parse(self.INPUT, "views/test.html")
        python_code = PythonTranslator().translate(template_info)
        ok (python_code) == self.TRANSLATED
        #
        vars = {}
        exec(python_code, vars, vars)
        ok (vars).contains('TestHtml_')
        klass = vars['TestHtml_']
        ok (klass).is_a(type)
        expected = r"""
<!doctype html>
<div>
  <ul class="list">
    <!-- comment -->
    <li>foo</li>
  </ul>
</div>
"""[1:]
        ok (klass().render()) == expected


    def _compile(self, input=None, filename="views/test.html", **properties):
        if input is None: input = self.INPUT
        template_info = TextParser().parse(input, filename)
        translator = PythonTranslator(**properties)
        python_code = translator.translate(template_info)
        try:
            import __builtin__
        except ImportError:
            import builtins as __builtin__
        vars = {'__builtin__': __builtin__}
        exec(python_code, vars, vars)
        return python_code, vars


    @test("property 'classname' speicifies class name.")
    def _(self):
        name = 'TestPage'
        pycode, vars = self._compile(classname=name)
        ok (vars).contains(name)
        ok (vars[name]).is_a(type)


    @test("property 'baseclass' specifies parent class name.")
    def _(self):
        name = '__builtin__.object'
        pycode, vars = self._compile(baseclass=name)
        ok (pycode).matches(r'class TestHtml_\(__builtin__\.object\):')


    @test("property 'encoding' adds encoding.")
    def _(self):
        pycode, vars = self._compile(encoding='utf-8')
        s = self.TRANSLATED
        s = '# -*- coding: utf-8 -*-\n' + s
        s = s.replace("from kwartzite.util import escape_html, to_str, Bunch",
                      "from kwartzite.util import escape_html, generate_tostrfunc, Bunch\n" + \
                      "to_str = generate_tostrfunc('utf-8')")
        expected = s
        ok (pycode) == expected


    @test("property 'mainprog' controls main program definition.")
    def _(self):
        s = r"""
if __name__ == '__main__':
    import sys
    sys.stdout.write(TestHtml_().render())
"""[1:]
        pycode, vars = self._compile(mainprog=True)
        ok (pycode).contains(s)
        pycode, vars = self._compile(mainprog=False)
        NG (pycode).contains(s)


    @test("property 'fragment' defines 'renderXxx()'.")
    def _(self):
        pycode, vars = self._compile()
        klass = vars['TestHtml_']
        obj = klass()
        ok (obj).has_attr('render_items')
        ok (obj).has_attr('render_item')
        obj.items.attr['class'] = 'list items'
        ok (obj.render_items()) == r'''
  <ul class="list items">
    <!-- comment -->
    <li>foo</li>
  </ul>
'''[1:]
        obj.item.text = 'SOS'
        ok (obj.render_item()) == '    <li>SOS</li>\n'
        #
        pycode, vars = self._compile(fragment=False)
        klass = vars['TestHtml_']
        obj = klass()
        NG (obj).has_attr('render_items')
        NG (obj).has_attr('render_item')


    @test("property 'attrobj' uses kwartzite.attribute.Attribute instead of dict.")
    def _(self):
        pycode, vars = self._compile()
        obj = vars['TestHtml_']()
        from kwartzite.template import Attribute
        ok (obj._attr_items).is_a(Attribute)
        ok (obj._attr_item).is_a(Attribute)
        obj.item.attr['x'] = 'X'
        obj.item.attr['a'] = 'A'
        obj.item.attr['k'] = 'K'
        ok (obj.render()).matches('<li x="X" a="A" k="K">foo</li>')
        #
        pycode, vars = self._compile(attrobj=False)
        obj = vars['TestHtml_']()
        ok (obj._attr_items).is_a(dict)
        ok (obj._attr_item).is_a(dict)
        obj.item.attr['x'] = 'X'
        obj.item.attr['a'] = 'A'
        obj.item.attr['k'] = 'K'
        NG (obj.render()).matches('<li x="X" a="A" k="K">foo</li>')
        ok (obj.render()).matches('<li.*x="X".*>foo</li>')
        ok (obj.render()).matches('<li.*a="A".*>foo</li>')
        ok (obj.render()).matches('<li.*k="K".*>foo</li>')
        #
        s = self.TRANSLATED
        s = s.replace(("        for k, v in attr:\n"
                       "            if v is not None:\n"
                       "                _extend((' ', e(s(k)), '=\"', e(s(v)), '\"'))\n"),
                      ("        for k in attr:\n"
                       "            v = attr[k]\n"
                       "            if v is not None:\n"
                       "                _extend((' ', e(s(k)), '=\"', e(s(v)), '\"'))\n"))
        s = s.replace(("    _attr_items = Attribute((\n"
                       "        ('class', 'list'),\n"
                       "    ))\n"),
                      ("    _attr_items = {\n"
                       "        'class':'list',\n"
                       "    }\n"))
        s = s.replace(("    _attr_item = Attribute()\n"),
                      ("    _attr_item = {}\n"))
        expected = s
        ok (pycode) == expected


    @test("supports 'text:' directive.")
    def _(self):
        input = r"""
<h1 data-kw="text:doctitle">TITLE</h1>
"""[1:]
        expected = r"""
## generated from views/test.html

from kwartzite.template import Template, Element, Attribute
from kwartzite.util import escape_html, to_str, Bunch

class TestHtml_(Template):

    def __init__(self):
        pass

    def echo(self, value):
        self._append(escape_html(to_str(value)))

    def _append_attr(self, attr):
        s = to_str
        e = escape_html
        _extend = self._buf.extend
        for k, v in attr:
            if v is not None:
                _extend((' ', e(s(k)), '="', e(s(v)), '"'))

    def create_document(self):
        _append = self._append
        _extend = self._extend
        _extend(('''<h1>''', escape_html(to_str(self._bunch.doctitle)), '''</h1>\n''', ))


# for test
if __name__ == '__main__':
    import sys
    sys.stdout.write(TestHtml_().render())
"""[1:]
        pycode, vars = self._compile(input)
        ok (pycode) == expected
        #
        klass = vars['TestHtml_']
        html = klass().render({'doctitle': '"Disappearance of Haruhi Suzumiya"'})
        ok (html) == "<h1>&quot;Disappearance of Haruhi Suzumiya&quot;</h1>\n"


    @test("supports 'attr:' directive.")
    def _(self):
        input = r"""
<div>
  <ul data-kw="mark:items">
    <li><a href="#" data-kw="attr:href=item.url;text:item.name">foo</a></li>
  </ul>
</div>
"""[1:]
        expected = r"""
## generated from views/test.html

from kwartzite.template import Template, Element, Attribute
from kwartzite.util import escape_html, to_str, Bunch

class TestHtml_(Template):

    def __init__(self):
        self.items = Element(self._attr_items.copy(),
             self.stag_items, self.cont_items, self.etag_items)

    def echo(self, value):
        self._append(escape_html(to_str(value)))

    def _append_attr(self, attr):
        s = to_str
        e = escape_html
        _extend = self._buf.extend
        for k, v in attr:
            if v is not None:
                _extend((' ', e(s(k)), '="', e(s(v)), '"'))

    def create_document(self):
        _append = self._append
        _extend = self._extend
        _append('''<div>\n''')
        self.elem_items()
        _append('''</div>\n''')


    ## element 'items'

    _text_items = None
    _attr_items = Attribute()

    def elem_items(self):
        self.items.stag()
        self.items.cont()
        self.items.etag()

    def stag_items(self):
        _append = self._append
        _append('''  <ul''')
        self._append_attr(self.items.attr)
        _append('''>\n''')

    def cont_items(self):
        _append = self._append
        _extend = self._extend
        _extend(('''    <li><a href="''', escape_html(to_str(self._bunch.item.url)), '''">''', escape_html(to_str(self._bunch.item.name)), '''</a></li>\n''', ))

    def etag_items(self):
        self._append('''  </ul>\n''')

    def render_items(self, context=None, flag_elem=True):
        if context is None: context = {}
        self.set_context(context)
        self.set_buffer([])
        if flag_elem:  self.elem_items()
        else:          self.cont_items()
        return ''.join(self._buf)


# for test
if __name__ == '__main__':
    import sys
    sys.stdout.write(TestHtml_().render())
"""[1:]
        pycode, vars = self._compile(input)
        ok (pycode) == expected
        #
        expected = r"""
<div>
  <ul>
    <li><a href="/link?x=1&amp;y=2">&lt;SOS&gt;</a></li>
  </ul>
</div>
"""[1:]
        klass = vars['TestHtml_']
        from kwartzite.util import Bunch
        item = Bunch({'url': '/link?x=1&y=2', 'name': '<SOS>'})
        html = klass().render({'item': item})
        ok (html) == expected


    @test("'-' and '.' in marking name are converted into '_'.")
    def _(self):
        input = r"""<p data-kw="mark:foo.bar-baz">xxx</p>\n"""
        expected = r"""
## generated from views/test.html

from kwartzite.template import Template, Element, Attribute
from kwartzite.util import escape_html, to_str, Bunch

class TestHtml_(Template):

    def __init__(self):
        self.foo_bar_baz = Element(self._attr_foo_bar_baz.copy(),
             self.stag_foo_bar_baz, self.cont_foo_bar_baz, self.etag_foo_bar_baz)

    def echo(self, value):
        self._append(escape_html(to_str(value)))

    def _append_attr(self, attr):
        s = to_str
        e = escape_html
        _extend = self._buf.extend
        for k, v in attr:
            if v is not None:
                _extend((' ', e(s(k)), '="', e(s(v)), '"'))

    def create_document(self):
        _append = self._append
        _extend = self._extend
        self.elem_foo_bar_baz()
        _append('''\\n''')


    ## element 'foo.bar-baz'

    _text_foo_bar_baz = '''xxx'''
    _attr_foo_bar_baz = Attribute()

    def elem_foo_bar_baz(self):
        self.foo_bar_baz.stag()
        self.foo_bar_baz.cont()
        self.foo_bar_baz.etag()

    def stag_foo_bar_baz(self):
        _append = self._append
        _append('''<p''')
        self._append_attr(self.foo_bar_baz.attr)
        _append('''>''')

    def cont_foo_bar_baz(self):
        if self.foo_bar_baz.text is not None:
            self._append(escape_html(to_str(self.foo_bar_baz.text)))
        else:
            self._append(self._text_foo_bar_baz)

    def etag_foo_bar_baz(self):
        self._append('''</p>''')

    def render_foo_bar_baz(self, context=None, flag_elem=True):
        if context is None: context = {}
        self.set_context(context)
        self.set_buffer([])
        if flag_elem:  self.elem_foo_bar_baz()
        else:          self.cont_foo_bar_baz()
        return ''.join(self._buf)


# for test
if __name__ == '__main__':
    import sys
    sys.stdout.write(TestHtml_().render())
"""[1:]
        #pycode, vars = self._compile(input)
        template_info = TextParser().parse(input, 'views/test.html')
        translator = PythonTranslator()
        python_code = translator.translate(template_info)
        pycode = python_code
        ok (pycode) == expected



if __name__ == '__main__':
    oktest.run()

###
### $Release: 0.0.1 $
### $Copyright: copyright(c) 2007-2011 kuwata-lab.com all rights reserved $
### $License: MIT License $
###

import sys, re, unittest
import oktest
from oktest import ok, NG, test

from kwartzite.parser.TextParser import TextParser
from kwartzite.translator.JavaTranslator import JavaTranslator



class JavaTranslator_TC(unittest.TestCase):


    INPUT = r"""
<!doctype html>
<div>
  <ul data-kw="mark:list" class="items">
    <!-- comment -->
    <li data-kw="mark:item">foo</li>
  </ul>
</div>
"""[1:]


    TRANSLATED = r"""
// generated from views/test.html by pykwartzite

import java.util.Map;

import kwartzite.Template;
import kwartzite.Elem;
import kwartzite.Dom;


public class TestHtml_ extends kwartzite.Template {

    // *** Begin Declaration ***
    
    // *** End Declaration ***


    private StringBuilder _buf;

    public TestHtml_(int bufsize) {
        _buf = new StringBuilder(bufsize);
    }

    public TestHtml_() {
        this(1024);
    }


    public String render() {
        createDocument();
        return _buf.toString();
    }

    public void createDocument() {
            _buf.append("<!doctype html>\n"
             + "<div>\n");
            elemList();
            _buf.append("</div>\n");
    }


    public void echo(String arg)  {
        if (arg == null) return;
        _buf.append(escape(arg));
    }
    public void echo(Dom.Node arg)  {
        if (arg == null) return;
        _buf.append(arg.toHtml());
    }
    public void echo(Object arg) {
        if (arg == null) return;
        if (arg instanceof Dom.Node) {
            echo((Dom.Node)arg);
        }
        else {
            echo(arg.toString());
        }
    }
    public void echo(int arg)     { _buf.append(arg); }
    public void echo(double arg)  { _buf.append(arg); }
    public void echo(char arg)    { _buf.append(arg); }
    public void echo(char[] arg)  { _buf.append(arg); }
    public void echo(boolean arg) { _buf.append(arg); }


    ///
    /// element 'list'
    ///

    protected Elem elemList = new Elem() {
        //protected Attrs  _attr = new Attrs();  // defined in Elem class
        //protected Object _text = null;         // defined in Elem class

        public void stag() {
            if (_attrs.isEmpty()) {
                _buf.append("  <ul class=\"items\">\n");
            } else {
                _buf.append("  <ul");
                if (! _attrs.has("class")) _buf.append(" class=\"items\"");
                appendAttrs(_attrs, _buf);
                _buf.append(">\n");
            }
        }

        public void cont() {
            if (_text != null) {
                echo(_text);
                return;
            }
            _buf.append("    <!-- comment -->\n");
            elemItem();
        }

        public void etag() {
            _buf.append("  </ul>\n");
        }

    };

    protected void elemList() {
        elemList(this.elemList);
    }
    protected void elemList(Elem e) {
        e.stag();
        e.cont();
        e.etag();
    }

    public String renderList() {
        return renderList(true);
    }
    public String renderList(boolean flagElem) {
        _buf = new StringBuilder();
        if (flagElem) this.elemList.elem();
        else          this.elemList.cont();
        return _buf.toString();
    }


    ///
    /// element 'item'
    ///

    protected Elem elemItem = new Elem() {
        //protected Attrs  _attr = new Attrs();  // defined in Elem class
        //protected Object _text = null;         // defined in Elem class

        public void stag() {
            if (_attrs.isEmpty()) {
                _buf.append("    <li>");
            } else {
                _buf.append("    <li");
                appendAttrs(_attrs, _buf);
                _buf.append(">");
            }
        }

        public void cont() {
            if (_text != null) {
                echo(_text);
                return;
            }
            _buf.append("foo");
        }

        public void etag() {
            _buf.append("</li>\n");
        }

    };

    protected void elemItem() {
        elemItem(this.elemItem);
    }
    protected void elemItem(Elem e) {
        e.stag();
        e.cont();
        e.etag();
    }

    public String renderItem() {
        return renderItem(true);
    }
    public String renderItem(boolean flagElem) {
        _buf = new StringBuilder();
        if (flagElem) this.elemItem.elem();
        else          this.elemItem.cont();
        return _buf.toString();
    }


    // for test
    public static void main(String[] args) throws Exception {
        System.out.print(new TestHtml_().render());
    }


}
"""[1:]


    @test("#translate() translates TemplateInfo into Java code.")
    def _(self):
        template_info = TextParser().parse(self.INPUT, "views/test.html")
        java_code = JavaTranslator().translate(template_info)
        ok (java_code) == self.TRANSLATED


    def _translate(self, input=None, filename="views/test.html", **properties):
        if input is None: input = self.INPUT
        template_info = TextParser().parse(input, filename)
        translator = JavaTranslator(**properties)
        java_code = translator.translate(template_info)
        return java_code


    @test("property 'classname' speicifies class name.")
    def _(self):
        java_code = self._translate(classname="TestPage")
        ok (java_code).contains("class TestPage extends kwartzite.Template {")


    @test("property 'baseclass' speicifies parent class name.")
    def _(self):
        java_code = self._translate(baseclass="BaseTemplate")
        ok (java_code).contains("class TestHtml_ extends BaseTemplate {")


    @test("property 'interface' speicifies interface name.")
    def _(self):
        java_code = self._translate(interface="kwartzite.Renderable")
        ok (java_code).contains("class TestHtml_ extends kwartzite.Template implements kwartzite.Renderable {")


    @test("property 'package' speicifies package name.")
    def _(self):
        java_code = self._translate(package="my.app.views")
        ok (java_code).contains("package my.app.views;\n")


    @test("property 'encoding' adds encoding.")
    def _(self):
        java_code = self._translate(encoding='iso8859-1')
        ok (java_code).contains("// -*- coding: iso8859-1 -*-")


    @test("property 'mainprog' controls main program definition.")
    def _(self):
        java_code = self._translate()
        ok (java_code).contains("public static void main(String[] args)")
        java_code = self._translate(mainprog=False)
        NG (java_code).contains("public static void main(String[] args)")


    @test("property 'fragment' defines renderXxx().")
    def _(self):
        java_code = self._translate()
        ok (java_code).contains("public String renderList()")
        java_code = self._translate(fragment=False)
        NG (java_code).contains("public String renderList()")


    @test("supports 'text:' directive.")
    def _(self):
        input = r"""
<h1 data-kw="text:doctitle">TITLE</h1>
"""[1:]
        expected = r"""
// generated from views/test.html by pykwartzite

import java.util.Map;

import kwartzite.Template;
import kwartzite.Elem;
import kwartzite.Dom;


public class TestHtml_ extends kwartzite.Template {

    // *** Begin Declaration ***
    
    // *** End Declaration ***


    private StringBuilder _buf;

    public TestHtml_(int bufsize) {
        _buf = new StringBuilder(bufsize);
    }

    public TestHtml_() {
        this(1024);
    }


    public String render() {
        createDocument();
        return _buf.toString();
    }

    public void createDocument() {
            _buf.append("<h1>").append(escape(doctitle)).append("</h1>\n");
    }


    public void echo(String arg)  {
        if (arg == null) return;
        _buf.append(escape(arg));
    }
    public void echo(Dom.Node arg)  {
        if (arg == null) return;
        _buf.append(arg.toHtml());
    }
    public void echo(Object arg) {
        if (arg == null) return;
        if (arg instanceof Dom.Node) {
            echo((Dom.Node)arg);
        }
        else {
            echo(arg.toString());
        }
    }
    public void echo(int arg)     { _buf.append(arg); }
    public void echo(double arg)  { _buf.append(arg); }
    public void echo(char arg)    { _buf.append(arg); }
    public void echo(char[] arg)  { _buf.append(arg); }
    public void echo(boolean arg) { _buf.append(arg); }


    // for test
    public static void main(String[] args) throws Exception {
        System.out.print(new TestHtml_().render());
    }


}
"""[1:]
        java_code = self._translate(input)
        ok (java_code) == expected


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
// generated from views/test.html by pykwartzite

import java.util.Map;

import kwartzite.Template;
import kwartzite.Elem;
import kwartzite.Dom;


public class TestHtml_ extends kwartzite.Template {

    // *** Begin Declaration ***
    
    // *** End Declaration ***


    private StringBuilder _buf;

    public TestHtml_(int bufsize) {
        _buf = new StringBuilder(bufsize);
    }

    public TestHtml_() {
        this(1024);
    }


    public String render() {
        createDocument();
        return _buf.toString();
    }

    public void createDocument() {
            _buf.append("<div>\n");
            elemItems();
            _buf.append("</div>\n");
    }


    public void echo(String arg)  {
        if (arg == null) return;
        _buf.append(escape(arg));
    }
    public void echo(Dom.Node arg)  {
        if (arg == null) return;
        _buf.append(arg.toHtml());
    }
    public void echo(Object arg) {
        if (arg == null) return;
        if (arg instanceof Dom.Node) {
            echo((Dom.Node)arg);
        }
        else {
            echo(arg.toString());
        }
    }
    public void echo(int arg)     { _buf.append(arg); }
    public void echo(double arg)  { _buf.append(arg); }
    public void echo(char arg)    { _buf.append(arg); }
    public void echo(char[] arg)  { _buf.append(arg); }
    public void echo(boolean arg) { _buf.append(arg); }


    ///
    /// element 'items'
    ///

    protected Elem elemItems = new Elem() {
        //protected Attrs  _attr = new Attrs();  // defined in Elem class
        //protected Object _text = null;         // defined in Elem class

        public void stag() {
            if (_attrs.isEmpty()) {
                _buf.append("  <ul>\n");
            } else {
                _buf.append("  <ul");
                appendAttrs(_attrs, _buf);
                _buf.append(">\n");
            }
        }

        public void cont() {
            if (_text != null) {
                echo(_text);
                return;
            }
            _buf.append("    <li><a href=\"").append(escape(item.getUrl())).append("\">").append(escape(item.getName())).append("</a></li>\n");
        }

        public void etag() {
            _buf.append("  </ul>\n");
        }

    };

    protected void elemItems() {
        elemItems(this.elemItems);
    }
    protected void elemItems(Elem e) {
        e.stag();
        e.cont();
        e.etag();
    }

    public String renderItems() {
        return renderItems(true);
    }
    public String renderItems(boolean flagElem) {
        _buf = new StringBuilder();
        if (flagElem) this.elemItems.elem();
        else          this.elemItems.cont();
        return _buf.toString();
    }


    // for test
    public static void main(String[] args) throws Exception {
        System.out.print(new TestHtml_().render());
    }


}
"""[1:]
        java_code = self._translate(input)
        ok (java_code) == expected


    @test("'-' and '.' in marking name are converted into '_'.")
    def _(self):
        input = r"""<p data-kw="mark:foo.bar-baz">xxx</p>\n"""
        expected = r"""
// generated from views/test.html by pykwartzite

import java.util.Map;

import kwartzite.Template;
import kwartzite.Elem;
import kwartzite.Dom;


public class TestHtml_ extends kwartzite.Template {

    // *** Begin Declaration ***
    
    // *** End Declaration ***


    private StringBuilder _buf;

    public TestHtml_(int bufsize) {
        _buf = new StringBuilder(bufsize);
    }

    public TestHtml_() {
        this(1024);
    }


    public String render() {
        createDocument();
        return _buf.toString();
    }

    public void createDocument() {
            elemFooBarBaz();
            _buf.append("\\n");
    }


    public void echo(String arg)  {
        if (arg == null) return;
        _buf.append(escape(arg));
    }
    public void echo(Dom.Node arg)  {
        if (arg == null) return;
        _buf.append(arg.toHtml());
    }
    public void echo(Object arg) {
        if (arg == null) return;
        if (arg instanceof Dom.Node) {
            echo((Dom.Node)arg);
        }
        else {
            echo(arg.toString());
        }
    }
    public void echo(int arg)     { _buf.append(arg); }
    public void echo(double arg)  { _buf.append(arg); }
    public void echo(char arg)    { _buf.append(arg); }
    public void echo(char[] arg)  { _buf.append(arg); }
    public void echo(boolean arg) { _buf.append(arg); }


    ///
    /// element 'foo.bar-baz'
    ///

    protected Elem elemFooBarBaz = new Elem() {
        //protected Attrs  _attr = new Attrs();  // defined in Elem class
        //protected Object _text = null;         // defined in Elem class

        public void stag() {
            if (_attrs.isEmpty()) {
                _buf.append("<p>");
            } else {
                _buf.append("<p");
                appendAttrs(_attrs, _buf);
                _buf.append(">");
            }
        }

        public void cont() {
            if (_text != null) {
                echo(_text);
                return;
            }
            _buf.append("xxx");
        }

        public void etag() {
            _buf.append("</p>");
        }

    };

    protected void elemFooBarBaz() {
        elemFooBarBaz(this.elemFooBarBaz);
    }
    protected void elemFooBarBaz(Elem e) {
        e.stag();
        e.cont();
        e.etag();
    }

    public String renderFooBarBaz() {
        return renderFooBarBaz(true);
    }
    public String renderFooBarBaz(boolean flagElem) {
        _buf = new StringBuilder();
        if (flagElem) this.elemFooBarBaz.elem();
        else          this.elemFooBarBaz.cont();
        return _buf.toString();
    }


    // for test
    public static void main(String[] args) throws Exception {
        System.out.print(new TestHtml_().render());
    }


}
"""[1:]
        java_code = self._translate(input)
        ok (java_code) == expected



if __name__ == '__main__':
    oktest.run()

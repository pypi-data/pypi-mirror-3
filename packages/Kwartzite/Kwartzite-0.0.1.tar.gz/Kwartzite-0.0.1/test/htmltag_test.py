###
### $Release: 0.0.1 $
### $Copyright: copyright(c) 2007-2011 kuwata-lab.com all rights reserved $
### $License: MIT License $
###

import oktest
from oktest import ok, NG, test

from kwartzite.htmltag import Tag, Html



class Tag_TC(object):


    @test("#__init__() takes name and attrs.")
    def _(self):
        t = Tag("div", {'class': "even", 'data-ex': "example"})
        ok (t.name) == "div"
        ok (t.attrs) == {'class': "even", 'data-ex': "example"}
        #
        t = Tag("div")
        ok (t.name) == "div"
        ok (t.attrs) == None


    #@test("#__init__() can take kwargs as attrs.")
    #def _(self):
    #    t = Tag("div", klass="even", data_ex="example")
    #    ok (t.name) == "div"
    #    ok (t.attrs) == {'klass': "even", 'data_ex': "example"}


    @test("#__call__() returns self.")
    def _(self):
        t = Tag("p")
        ok (t("text")).is_(t)


    @test("#__call__() takes children.")
    def _(self):
        t = Tag("div", {'class': "main"}) (
                Tag("p") (
                    "message",
                    Tag("a", {'href': "#"}) (
                        Tag("img", {'src': "image.png"})
                    )
                )
            )
        empty = None
        ok (t.children).length(1)
        ok (t).attr('name', "div").attr('attrs', {'class': "main"})
        ok (t.children[0]).is_a(Tag).attr('name', "p").attr('attrs', empty)
        ok (t.children[0].children).length(2)
        ok (t.children[0].children[0]) == "message"
        ok (t.children[0].children[1]).is_a(Tag).attr('name', "a").attr('attrs', {'href': "#"})
        ok (t.children[0].children[1].children).length(1)
        ok (t.children[0].children[1].children[0]).is_a(Tag).attr('name', "img").attr('attrs', {'src': "image.png"})


    @test("#__str__() returns html string.")
    def _(self):
        t = Tag("p", {'class': "body"}) ("foobar")
        ok (str(t)) == '<p class="body">foobar</p>'
        #
        t = Tag("div", {'class': "main"}) (
                Tag("p") ("text")
            )
        ok (str(t)) == '<div class="main"><p>text</p></div>'


    @test("#__str__() returns empty tag string when no children.")
    def _(self):
        t = Tag("br")
        ok (str(t)) == '<br />'
        t = Tag("meta", {'charset': "utf-8"})
        ok (str(t)) == '<meta charset="utf-8" />'


    @test("#__str__() escapes tag name, attributes, and children.")
    def _(self):
        ok (str(Tag('<A&A>'))) == '<&lt;A&amp;A&gt; />'
        ok (str(Tag('span', {'<B&B>': '& < > "'}))) == '<span &lt;B&amp;B&gt;="&amp; &lt; &gt; &quot;" />'
        ok (str(Tag('span')('< " > &'))) == '<span>&lt; &quot; &gt; &amp;</span>'


    @test("#__str__() omit tags when tag name is falsy-value.")
    def _(self):
        t = Tag(None) ('foo"bar', Tag("br"), 'baz"')
        ok (str(t)) == 'foo&quot;bar<br />baz&quot;'



class Html_TC(object):


    @test("#__getattr__() returns function object.")
    def _(self):
        h = Html()
        ok (h.div).is_a(type(lambda: None))


    @test("#__call__() helps to create texts.")
    def _(self):
        h = Html()
        t = h("msg1 ", h.b()("A & B"), " X & Y")
        ok (t).is_a(Tag)
        ok (t.name).is_(None)
        ok (str(t)) == "msg1 <b>A &amp; B</b> X &amp; Y"


    @test("supports to generate html tags.")
    def _(self):
        h = Html()
        t = h.div({'class': "main"}) (
                h.p() (
                    "message",
                    h.a(href="#") (
                        h.img(src="image.png")
                    )
                )
            )
        empty = {}
        ok (t.children).length(1)
        ok (t).attr('name', "div").attr('attrs', {'class': "main"})
        ok (t.children[0]).is_a(Tag).attr('name', "p").attr('attrs', empty)
        ok (t.children[0].children).length(2)
        ok (t.children[0].children[0]) == "message"
        ok (t.children[0].children[1]).is_a(Tag).attr('name', "a").attr('attrs', {'href': "#"})
        ok (t.children[0].children[1].children).length(1)
        ok (t.children[0].children[1].children[0]).is_a(Tag).attr('name', "img").attr('attrs', {'src': "image.png"})



if __name__ == '__main__':
    oktest.run()

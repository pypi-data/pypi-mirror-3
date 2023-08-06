## generated from testdata/test_main/input.html

try:
    import xml.etree.cElementTree as ET
except ImportError:
    try:
        import elementtree.cElementTree as ET
    except ImportError:
        import elementtree.ElementTree as ET
Element = ET.Element
SubElement = ET.SubElement


__all__ = ['input_html']


class input_html(object):

    def __init__(self, **_context):
        for k, v in _context.iteritems():
            setattr(self, k, v)
        self._context = _context
        self.attr_Title = self.attr_Title.copy()
        self.attr_secnum = self.attr_secnum.copy()
        self.attr_sectitle = self.attr_sectitle.copy()
        self.attr_span1 = self.attr_span1.copy()
        self.attr_span2 = self.attr_span2.copy()
        self.attr_anchor1 = self.attr_anchor1.copy()
        self.attr_table1 = self.attr_table1.copy()
        self.attr_list1 = self.attr_list1.copy()
        self.attr_item1 = self.attr_item1.copy()

    def create_document(self):
        root = e1 = Element('html', {})
        e1.text = '\n  '
        e1.tail = None
        e2 = SubElement(e1, 'head', {})
        e2.text = '\n    '
        e2.tail = '\n  '
        self.elem_Title(e2)
        e4 = SubElement(e2, 'meta', {'content': 'text/html; charset=UTF8', 'http-equiv': 'Content-Type'})
        e4.text = None
        e4.tail = '\n    '
        e5 = SubElement(e2, 'script', {'src': 'js/jquery.js', 'type': 'text/javascript', 'language': 'javascript'})
        e5.text = None
        e5.tail = '\n  '
        e6 = SubElement(e1, 'body', {})
        e6.text = '\n    '
        e6.tail = '\n'
        e7 = SubElement(e6, 'h1', {})
        e7.text = 'Section '
        e7.tail = '\n    '
        self.elem_secnum(e7)
        self.elem_sectitle(e7)
        e10 = SubElement(e6, 'p', {})
        e10.text = None
        e10.tail = '\n    '
        e11 = SubElement(e10, 'span', {})
        e11.text = 'Span tag'
        e11.tail = ' example.'
        e12 = SubElement(e6, 'p', {})
        e12.text = None
        e12.tail = '\n    '
        self.elem_span1(e12)
        e14 = SubElement(e6, 'p', {})
        e14.text = None
        e14.tail = '\n    '
        self.elem_span2(e14)
        e16 = SubElement(e6, 'p', {})
        e16.text = 'Empty Tag example.'
        e16.tail = '\n    '
        e17 = SubElement(e16, 'br', {})
        e17.text = None
        e17.tail = None
        e18 = SubElement(e16, 'br', {})
        e18.text = None
        e18.tail = '\n       '
        self.elem_anchor1(e16)
        e20 = SubElement(e16, 'a', {'href': '/cgi-bin/bar.cgi?a=1&b=&c=', 'onclick': "javascript:alert('NG?');return false"})
        e20.text = 'another spaces example'
        e20.tail = '\n    '
        e21 = SubElement(e6, 'table', self.attr_table1)
        e21.text = '\n      '
        e21.tail = '\n  '
        self.elem_list1(e21)
        #self.elem_d1(e21)
        return ET.ElementTree(root)


    ## element 'Title'

    text_Title = 'Title'
    attr_Title = {'id': 'Title'}

    def elem_Title(self, parent):
        e24 = SubElement(parent, 'title', self.attr_Title.copy())
        e24.text = self.text_Title
        e24.tail = '\n    '
        self.cont_Title(e24)
        return e24

    def cont_Title(self, element):
        pass

    _elem_Title = elem_Title
    _cont_Title = cont_Title


    ## element 'secnum'

    text_secnum = '99'
    attr_secnum = {}

    def elem_secnum(self, parent):
        e25 = SubElement(parent, 'span', self.attr_secnum.copy())
        e25.text = self.text_secnum
        e25.tail = ': '
        self.cont_secnum(e25)
        return e25

    def cont_secnum(self, element):
        pass

    _elem_secnum = elem_secnum
    _cont_secnum = cont_secnum


    ## element 'sectitle'

    text_sectitle = 'TITLE'
    attr_sectitle = {'class': 'title'}

    def elem_sectitle(self, parent):
        e26 = SubElement(parent, 'span', self.attr_sectitle.copy())
        e26.text = self.text_sectitle
        e26.tail = None
        self.cont_sectitle(e26)
        return e26

    def cont_sectitle(self, element):
        pass

    _elem_sectitle = elem_sectitle
    _cont_sectitle = cont_sectitle


    ## element 'span1'

    text_span1 = 'Dummy span tag'
    attr_span1 = {}

    def elem_span1(self, parent):
        e27 = SubElement(parent, 'span', self.attr_span1.copy())
        e27.text = self.text_span1
        e27.tail = ' example.'
        self.cont_span1(e27)
        return e27

    def cont_span1(self, element):
        pass

    _elem_span1 = elem_span1
    _cont_span1 = cont_span1


    ## element 'span2'

    text_span2 = 'Non-dummy span tag'
    attr_span2 = {'class': 'foo'}

    def elem_span2(self, parent):
        e28 = SubElement(parent, 'span', self.attr_span2.copy())
        e28.text = self.text_span2
        e28.tail = ' example.'
        self.cont_span2(e28)
        return e28

    def cont_span2(self, element):
        pass

    _elem_span2 = elem_span2
    _cont_span2 = cont_span2


    ## element 'anchor1'

    text_anchor1 = 'attr spaces and extra spaces example'
    attr_anchor1 = {'href': '/cgi-bin/foo.cgi?a=1&b=&c=', 'id': 'anchor1', 'onclick': "javascript:alert('OK?');return false"}

    def elem_anchor1(self, parent):
        e29 = SubElement(parent, 'a', self.attr_anchor1.copy())
        e29.text = self.text_anchor1
        e29.tail = '\n       '
        self.cont_anchor1(e29)
        return e29

    def cont_anchor1(self, element):
        pass

    _elem_anchor1 = elem_anchor1
    _cont_anchor1 = cont_anchor1


    ## element 'table1'

    attr_table1 = {'style': 'background:#DDDDDD', 'summary': 'items'}


    ## element 'list1'

    text_list1 = '\n        '
    attr_list1 = {'bgcolor': '#FFCCCC', 'title': '"<A&B>"', 'class': 'odd'}

    def elem_list1(self, parent):
        e30 = SubElement(parent, 'tr', self.attr_list1.copy())
        e30.text = self.text_list1
        e30.tail = '\n      '
        self.cont_list1(e30)
        return e30

    def cont_list1(self, element):
        e31 = SubElement(element, 'td', {})
        e31.text = None
        e31.tail = '\n      '
        e32 = SubElement(e31, 'a', self.attr_item1)
        e32.text = self.text_item1
        e32.tail = None

    _elem_list1 = elem_list1
    _cont_list1 = cont_list1


    ## element 'item1'

    text_item1 = 'foo'
    attr_item1 = {'href': '#'}


    ## element 'd1'


# for test
if __name__ == '__main__':
    ET.dump(input_html().create_document()),


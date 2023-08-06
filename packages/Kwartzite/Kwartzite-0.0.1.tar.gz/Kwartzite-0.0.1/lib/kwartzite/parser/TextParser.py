###
### $Release: 0.0.1 $
### $Copyright: copyright(c) 2007-2011 kuwata-lab.com all rights reserved $
### $License: MIT License $
###


import re
from kwartzite.config import TextParserConfig
from kwartzite.parser import Parser, TemplateInfo, TagInfo, ElementInfo, AttrInfo, Expression, Directive, ParseError
from kwartzite.parser.BaseParser import BaseParser



class TextParser(BaseParser, TextParserConfig):
    """
    convert presentation data (html) into a list of Statement.
    notice that TextConverter class hanlde html file as text format, not html format.
    """

    #FETCH_PATTERN = re.compile(r'(^[ \t]*)?<(/?)([-:_\w]+)((?:\s+[-:_\w]+="[^"]*?")*)(\s*)(/?)>([ \t]*\r?\n)?')
    FETCH_PATTERN = re.compile(r'([ \t]*)<(/?)([-:_\w]+)((?:\s+[-:_\w]+="[^"]*?")*)(\s*)(/?)>([ \t]*\r?\n)?')


    def _create_fetch_generator(self, input, pattern):
        pos = 0
        linenum = 1
        linenum_delta = 0
        prev_tagstr = ''
        column = None
        for m in pattern.finditer(input):
            start = m.start()
            if start == 0 or input[start-1] == "\n":  # beginning of line
                head_space = m.group(1)
            else:
                head_space = None
                start += len(m.group(1))
            text = input[pos:start]
            pos = m.end()
            linenum += text.count("\n") + prev_tagstr.count("\n")
            prev_tagstr = m.group(0)
            g = m.group
            string, is_etag, tagname, attr_str, extra_space, is_empty, tail_space = \
                g(0), g(2), g(3), g(4), g(5), g(6), g(7)
            tag = TagInfo(tagname, attr_str, is_etag, is_empty, linenum,
                          string, head_space, tail_space, extra_space)
            yield text, tag
        rest = pos == 0 and input or input[pos:]
        yield rest, None


    ##
    def _setup(self, input, filename):
        BaseParser._setup(self, input, filename)
        generator = self._create_fetch_generator(input, TextParser.FETCH_PATTERN)
        self._fetch = hasattr(generator, '__next__') and generator.__next__ or generator.next

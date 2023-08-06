###
### $Release: 0.0.1 $
### $Copyright: copyright(c) 2007-2011 kuwata-lab.com all rights reserved $
### $License: MIT License $
###


class BaseConfig(object):
    ESCAPE    = False
    ENCODING  = None    # or 'utf-8'
    CLASSNAME = '%u_%x'

class ParserConfig(BaseConfig):
    NO_ETAGS  = [ 'input', 'img' ,'br', 'hr', 'meta', 'link' ]   # end-tag is omittable
    DELSPAN   = True    # delete dummy <span> tag
    DATTR     = 'data-kw'

class TextParserConfig(ParserConfig):
    pass

class XmlParserConfig(ParserConfig):
    pass

class ElementTreeParserConfig(ParserConfig):
    pass

class TranslatorConfig(BaseConfig):
    CLASSNAME = '%F_'   # '%u_%x'
    BASECLASS = 'object'
    MAINPROG  = True
    FRAGMENT  = True
    ATTROBJ   = True
    SUFFIX    = None

class PythonTranslatorConfig(TranslatorConfig):
    BASECLASS = 'Template'
    SUFFIX    = '.py'

class JavaTranslatorConfig(TranslatorConfig):
    #BASECLASS = 'kwartzite.AbstractTemplate'
    #BASECLASS = 'Object'
    BASECLASS = 'kwartzite.Template'
    INTERFACE = None
    PACKAGE   = None
    SUFFIX    = '.java'

class ElementTreeTranslatorConfig(TranslatorConfig):
    pass

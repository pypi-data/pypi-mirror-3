from itertools import chain
from xml.sax.saxutils import XMLGenerator
from .filestructure import VERSION
from .dataio import typed_struct_attributes, Struct, ArrayType, FlagsType, EnumType, WCHAR
from .dataio import HWPUNIT, HWPUNIT16, SHWPUNIT
from .dataio import hexdump
from .binmodel import typed_model_attributes, COLORREF, BinStorageId, Margin, Text
from .xmlmodel import ModelEventHandler

import logging
logger = logging.getLogger(__name__)

def xmlattrval(value):
    if isinstance(value, basestring):
        return value
    elif isinstance(type(value), EnumType):
        return type(value).name_for(value).lower()
    elif isinstance(value, type):
        return value.__name__
    else:
        return str(value)

def expanded_xmlattribute((name, (t, value))):
    if isinstance(t, FlagsType):
        yield name, hex(int(value))
        for k, v in t.dictvalue(t(value)).iteritems():
            yield k, xmlattrval(v)
    elif t is Margin:
        for pos in ('left', 'right', 'top', 'bottom'):
            yield '-'.join([name, pos]), xmlattrval(value.get(pos))
    elif t is COLORREF:
        yield name, xmlattrval( t(value) )
    elif t is VERSION:
        yield name, '.'.join(str(x) for x in value)
    elif t in (HWPUNIT, SHWPUNIT, HWPUNIT16):
        yield name, str(value)
    elif t is WCHAR:
        if value == 0:
            yield name, u''
        else:
            yield name, unichr(value)
    elif t is BinStorageId:
        yield name, 'BIN%04X'%value
    else:
        yield name, xmlattrval(value)

def xmlattr_dashednames(attrs):
    for k, v in attrs:
        yield k.replace('_', '-'), v

def xmlattr_uniqnames(attrs):
    names = set([])
    for k, v in attrs:
        assert not k in names, 'name clashes: %s'%k
        yield k, v
        names.add(k)

def xmlattributes_for_plainvalues(context, plainvalues):
    ntvs = plainvalues.iteritems()
    ntvs = chain(*(expanded_xmlattribute(ntv) for ntv in ntvs))
    return dict(xmlattr_uniqnames(xmlattr_dashednames(ntvs)))

def separate_plainvalues(typed_attributes):
    d = []
    p = dict()
    for named_item in typed_attributes:
        name, item = named_item
        t, value = item
        try:
            if t is Margin:
                p[name] = item
            elif isinstance(value, dict):
                if not issubclass(t, Struct):
                    logger.warning('%s is not a Struct', name)
                d.append( named_item )
            elif isinstance(t, ArrayType) and issubclass(t.itemtype, Struct):
                d.append( named_item )
            else:
                p[name] = item
        except Exception, e:
            logger.error('%s', (name, t, value))
            logger.error('%s', t.__dict__)
            logger.exception(e)
            raise e
    return d, p

def startelement(context, xmlgen, (model, attributes)):
    if issubclass(model, Struct):
        typed_attributes = typed_struct_attributes(model, attributes, context)
    elif model is dict:
        typed_attributes = ((k, (type(v), v)) for k, v in attributes.iteritems())
    else:
        typed_attributes = typed_model_attributes(model, attributes, context)

    typed_attributes, plainvalues = separate_plainvalues(typed_attributes)
    yield xmlgen.startElement, model.__name__, xmlattributes_for_plainvalues(context, plainvalues)
    for _name, (_type, _value) in typed_attributes:
        if isinstance(_value, dict):
            assert isinstance(_value, dict)
            _value = dict(_value)
            _value['attribute-name'] = _name
            for x in element(context, xmlgen, (_type, _value)): yield x
        else:
            assert isinstance(_value, (tuple, list)) and issubclass(_type.itemtype, Struct), (_value, _type)
            yield xmlgen.startElement, 'Array', {'name':_name}
            for _itemvalue in _value:
                for x in element(context, xmlgen, (_type.itemtype, _itemvalue)): yield x
            yield xmlgen.endElement, 'Array'

def element(context, xmlgen, (model, attributes)):
    for x in startelement(context, xmlgen, (model, attributes)): yield x
    yield xmlgen.endElement, model.__name__

class XmlFormat(ModelEventHandler):
    def __init__(self, out):
        self.xmlgen = XMLGenerator(out, 'utf-8')
    def startDocument(self):
        self.xmlgen.startDocument()
    def startModel(self, model, attributes, **context):
        logger.debug('xmlmodel.XmlFormat: model: %s, %s', model.__name__, attributes)
        logger.debug('xmlmodel.XmlFormat: context: %s', context)
        recordid = context.get('recordid', ('UNKNOWN', 'UNKNOWN', -1))
        hwptag = context.get('hwptag', '')
        logger.info('xmlmodel.XmlFormat: rec:%d %s', recordid[2], hwptag)
        if model is Text:
            text = attributes.pop('text')
        else:
            text = None

        for x in startelement(context, self.xmlgen, (model, attributes)): x[0](*x[1:])

        if model is Text and text is not None:
            self.xmlgen.characters(text)

        unparsed = context.get('unparsed', '')
        if len(unparsed) > 0:
            logger.debug('UNPARSED: %s', hexdump(unparsed, True))
    def endModel(self, model):
        self.xmlgen.endElement(model.__name__)
    def endDocument(self):
        self.xmlgen.endDocument()

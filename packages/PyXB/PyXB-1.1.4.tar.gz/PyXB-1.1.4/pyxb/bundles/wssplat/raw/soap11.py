# ./pyxb/bundles/wssplat/raw/soap11.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:124ab58ff634848548cf6d9d1320f856ff23519e
# Generated 2012-06-15 14:42:55.310024 by PyXB version 1.1.4
# Namespace http://schemas.xmlsoap.org/soap/envelope/

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:4d635862-b722-11e1-8e3e-c8600024e903')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes

Namespace = pyxb.namespace.NamespaceForURI(u'http://schemas.xmlsoap.org/soap/envelope/', create_if_missing=True)
Namespace.configureCategories(['typeBinding', 'elementBinding'])
ModuleRecord = Namespace.lookupModuleRecordByUID(_GenerationUID, create_if_missing=True)
ModuleRecord._setModule(sys.modules[__name__])

def CreateFromDocument (xml_text, default_namespace=None, location_base=None):
    """Parse the given XML and use the document element to create a
    Python instance.
    
    @kw default_namespace The L{pyxb.Namespace} instance to use as the
    default namespace where there is no default namespace in scope.
    If unspecified or C{None}, the namespace of the module containing
    this function will be used.

    @keyword location_base: An object to be recorded as the base of all
    L{pyxb.utils.utility.Location} instances associated with events and
    objects handled by the parser.  You might pass the URI from which
    the document was obtained.
    """

    if pyxb.XMLStyle_saxer != pyxb._XMLStyle:
        dom = pyxb.utils.domutils.StringToDOM(xml_text)
        return CreateFromDOM(dom.documentElement)
    if default_namespace is None:
        default_namespace = Namespace.fallbackNamespace()
    saxer = pyxb.binding.saxer.make_parser(fallback_namespace=default_namespace, location_base=location_base)
    handler = saxer.getContentHandler()
    saxer.parse(StringIO.StringIO(xml_text))
    instance = handler.rootObject()
    return instance

def CreateFromDOM (node, default_namespace=None):
    """Create a Python instance from the given DOM node.
    The node tag must correspond to an element declaration in this module.

    @deprecated: Forcing use of DOM interface is unnecessary; use L{CreateFromDocument}."""
    if default_namespace is None:
        default_namespace = Namespace.fallbackNamespace()
    return pyxb.binding.basis.element.AnyCreateFromDOM(node, _fallback_namespace=default_namespace)


# Atomic SimpleTypeDefinition
class STD_ANON (pyxb.binding.datatypes.boolean):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON._CF_pattern = pyxb.binding.facets.CF_pattern()
STD_ANON._CF_pattern.addPattern(pattern=u'0|1')
STD_ANON._InitializeFacetMap(STD_ANON._CF_pattern)

# List SimpleTypeDefinition
# superclasses pyxb.binding.datatypes.anySimpleType
class encodingStyle (pyxb.binding.basis.STD_list):

    """
	    'encodingStyle' indicates any canonicalization conventions followed in the contents of the containing element.  For example, the value 'http://schemas.xmlsoap.org/soap/encoding/' indicates the pattern described in SOAP specification
	  """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'encodingStyle')
    _Documentation = u"\n\t    'encodingStyle' indicates any canonicalization conventions followed in the contents of the containing element.  For example, the value 'http://schemas.xmlsoap.org/soap/encoding/' indicates the pattern described in SOAP specification\n\t  "

    _ItemType = pyxb.binding.datatypes.anyURI
encodingStyle._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'encodingStyle', encodingStyle)

# Complex type detail with content type ELEMENT_ONLY
class detail (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'detail')
    # Base type is pyxb.binding.datatypes.anyType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'detail', detail)


# Complex type Header_ with content type ELEMENT_ONLY
class Header_ (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'Header')
    # Base type is pyxb.binding.datatypes.anyType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/soap/envelope/'))
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'Header', Header_)


# Complex type Body_ with content type ELEMENT_ONLY
class Body_ (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'Body')
    # Base type is pyxb.binding.datatypes.anyType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'Body', Body_)


# Complex type Fault_ with content type ELEMENT_ONLY
class Fault_ (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'Fault')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element faultstring uses Python identifier faultstring
    __faultstring = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(None, u'faultstring'), 'faultstring', '__httpschemas_xmlsoap_orgsoapenvelope_Fault__faultstring', False)

    
    faultstring = property(__faultstring.value, __faultstring.set, None, None)

    
    # Element faultcode uses Python identifier faultcode
    __faultcode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(None, u'faultcode'), 'faultcode', '__httpschemas_xmlsoap_orgsoapenvelope_Fault__faultcode', False)

    
    faultcode = property(__faultcode.value, __faultcode.set, None, None)

    
    # Element detail uses Python identifier detail
    __detail = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(None, u'detail'), 'detail', '__httpschemas_xmlsoap_orgsoapenvelope_Fault__detail', False)

    
    detail = property(__detail.value, __detail.set, None, None)

    
    # Element faultactor uses Python identifier faultactor
    __faultactor = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(None, u'faultactor'), 'faultactor', '__httpschemas_xmlsoap_orgsoapenvelope_Fault__faultactor', False)

    
    faultactor = property(__faultactor.value, __faultactor.set, None, None)


    _ElementMap = {
        __faultstring.name() : __faultstring,
        __faultcode.name() : __faultcode,
        __detail.name() : __detail,
        __faultactor.name() : __faultactor
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'Fault', Fault_)


# Complex type Envelope_ with content type ELEMENT_ONLY
class Envelope_ (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'Envelope')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://schemas.xmlsoap.org/soap/envelope/}Header uses Python identifier Header
    __Header = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Header'), 'Header', '__httpschemas_xmlsoap_orgsoapenvelope_Envelope__httpschemas_xmlsoap_orgsoapenvelopeHeader', False)

    
    Header = property(__Header.value, __Header.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/soap/envelope/}Body uses Python identifier Body
    __Body = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Body'), 'Body', '__httpschemas_xmlsoap_orgsoapenvelope_Envelope__httpschemas_xmlsoap_orgsoapenvelopeBody', False)

    
    Body = property(__Body.value, __Body.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/soap/envelope/'))
    _HasWildcardElement = True

    _ElementMap = {
        __Header.name() : __Header,
        __Body.name() : __Body
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'Envelope', Envelope_)


Body = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Body'), Body_)
Namespace.addCategoryObject('elementBinding', Body.name().localName(), Body)

Fault = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Fault'), Fault_)
Namespace.addCategoryObject('elementBinding', Fault.name().localName(), Fault)

Header = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Header'), Header_)
Namespace.addCategoryObject('elementBinding', Header.name().localName(), Header)

Envelope = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Envelope'), Envelope_)
Namespace.addCategoryObject('elementBinding', Envelope.name().localName(), Envelope)


detail._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any), min_occurs=0L, max_occurs=None)
    )
detail._ContentModel = pyxb.binding.content.ParticleModel(detail._GroupModel, min_occurs=1, max_occurs=1)


Header_._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/soap/envelope/')), min_occurs=0L, max_occurs=None)
    )
Header_._ContentModel = pyxb.binding.content.ParticleModel(Header_._GroupModel, min_occurs=1, max_occurs=1)


Body_._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any), min_occurs=0L, max_occurs=None)
    )
Body_._ContentModel = pyxb.binding.content.ParticleModel(Body_._GroupModel, min_occurs=1, max_occurs=1)



Fault_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, u'faultstring'), pyxb.binding.datatypes.string, scope=Fault_))

Fault_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, u'faultcode'), pyxb.binding.datatypes.QName, scope=Fault_))

Fault_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, u'detail'), detail, scope=Fault_))

Fault_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, u'faultactor'), pyxb.binding.datatypes.anyURI, scope=Fault_))
Fault_._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(Fault_._UseForTag(pyxb.namespace.ExpandedName(None, u'faultcode')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(Fault_._UseForTag(pyxb.namespace.ExpandedName(None, u'faultstring')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(Fault_._UseForTag(pyxb.namespace.ExpandedName(None, u'faultactor')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(Fault_._UseForTag(pyxb.namespace.ExpandedName(None, u'detail')), min_occurs=0L, max_occurs=1)
    )
Fault_._ContentModel = pyxb.binding.content.ParticleModel(Fault_._GroupModel, min_occurs=1, max_occurs=1)



Envelope_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Header'), Header_, scope=Envelope_))

Envelope_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Body'), Body_, scope=Envelope_))
Envelope_._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(Envelope_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Header')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(Envelope_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Body')), min_occurs=1L, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/soap/envelope/')), min_occurs=0L, max_occurs=None)
    )
Envelope_._ContentModel = pyxb.binding.content.ParticleModel(Envelope_._GroupModel, min_occurs=1, max_occurs=1)

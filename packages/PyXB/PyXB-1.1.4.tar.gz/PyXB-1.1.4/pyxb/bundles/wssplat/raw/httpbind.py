# ./pyxb/bundles/wssplat/raw/httpbind.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:700d4ca8e0588f8b897f9c60d123e08fa4d56b36
# Generated 2012-06-15 14:42:54.964490 by PyXB version 1.1.4
# Namespace http://schemas.xmlsoap.org/wsdl/http/

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:4d2dd872-b722-11e1-9520-c8600024e903')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes
import pyxb.bundles.wssplat.wsdl11

Namespace = pyxb.namespace.NamespaceForURI(u'http://schemas.xmlsoap.org/wsdl/http/', create_if_missing=True)
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


# Complex type CTD_ANON with content type EMPTY
class CTD_ANON (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type operationType with content type EMPTY
class operationType (pyxb.bundles.wssplat.wsdl11.tExtensibilityElement):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'operationType')
    # Base type is pyxb.bundles.wssplat.wsdl11.tExtensibilityElement
    
    # Attribute location uses Python identifier location
    __location = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'location'), 'location', '__httpschemas_xmlsoap_orgwsdlhttp_operationType_location', pyxb.binding.datatypes.anyURI, required=True)
    
    location = property(__location.value, __location.set, None, None)

    
    # Attribute required inherited from {http://schemas.xmlsoap.org/wsdl/}tExtensibilityElement

    _ElementMap = pyxb.bundles.wssplat.wsdl11.tExtensibilityElement._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = pyxb.bundles.wssplat.wsdl11.tExtensibilityElement._AttributeMap.copy()
    _AttributeMap.update({
        __location.name() : __location
    })
Namespace.addCategoryObject('typeBinding', u'operationType', operationType)


# Complex type bindingType with content type EMPTY
class bindingType (pyxb.bundles.wssplat.wsdl11.tExtensibilityElement):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'bindingType')
    # Base type is pyxb.bundles.wssplat.wsdl11.tExtensibilityElement
    
    # Attribute verb uses Python identifier verb
    __verb = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'verb'), 'verb', '__httpschemas_xmlsoap_orgwsdlhttp_bindingType_verb', pyxb.binding.datatypes.NMTOKEN, required=True)
    
    verb = property(__verb.value, __verb.set, None, None)

    
    # Attribute required inherited from {http://schemas.xmlsoap.org/wsdl/}tExtensibilityElement

    _ElementMap = pyxb.bundles.wssplat.wsdl11.tExtensibilityElement._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = pyxb.bundles.wssplat.wsdl11.tExtensibilityElement._AttributeMap.copy()
    _AttributeMap.update({
        __verb.name() : __verb
    })
Namespace.addCategoryObject('typeBinding', u'bindingType', bindingType)


# Complex type addressType with content type EMPTY
class addressType (pyxb.bundles.wssplat.wsdl11.tExtensibilityElement):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'addressType')
    # Base type is pyxb.bundles.wssplat.wsdl11.tExtensibilityElement
    
    # Attribute location uses Python identifier location
    __location = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'location'), 'location', '__httpschemas_xmlsoap_orgwsdlhttp_addressType_location', pyxb.binding.datatypes.anyURI, required=True)
    
    location = property(__location.value, __location.set, None, None)

    
    # Attribute required inherited from {http://schemas.xmlsoap.org/wsdl/}tExtensibilityElement

    _ElementMap = pyxb.bundles.wssplat.wsdl11.tExtensibilityElement._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = pyxb.bundles.wssplat.wsdl11.tExtensibilityElement._AttributeMap.copy()
    _AttributeMap.update({
        __location.name() : __location
    })
Namespace.addCategoryObject('typeBinding', u'addressType', addressType)


# Complex type CTD_ANON_ with content type EMPTY
class CTD_ANON_ (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



urlEncoded = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'urlEncoded'), CTD_ANON)
Namespace.addCategoryObject('elementBinding', urlEncoded.name().localName(), urlEncoded)

operation = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'operation'), operationType)
Namespace.addCategoryObject('elementBinding', operation.name().localName(), operation)

binding = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'binding'), bindingType)
Namespace.addCategoryObject('elementBinding', binding.name().localName(), binding)

address = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'address'), addressType)
Namespace.addCategoryObject('elementBinding', address.name().localName(), address)

urlReplacement = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'urlReplacement'), CTD_ANON_)
Namespace.addCategoryObject('elementBinding', urlReplacement.name().localName(), urlReplacement)

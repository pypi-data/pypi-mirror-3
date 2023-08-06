# ./pyxb/bundles/wssplat/raw/soapbind12.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:fe6dee6f975d5202c12c3e364c8df804f68deab8
# Generated 2012-06-15 14:42:56.205425 by PyXB version 1.1.4
# Namespace http://schemas.xmlsoap.org/wsdl/soap12/

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:4de86d4a-b722-11e1-8e23-c8600024e903')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes
import pyxb.bundles.wssplat.wsdl11

Namespace = pyxb.namespace.NamespaceForURI(u'http://schemas.xmlsoap.org/wsdl/soap12/', create_if_missing=True)
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
class useChoice (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'useChoice')
    _Documentation = None
useChoice._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=useChoice, enum_prefix=None)
useChoice.literal = useChoice._CF_enumeration.addEnumeration(unicode_value=u'literal', tag=u'literal')
useChoice.encoded = useChoice._CF_enumeration.addEnumeration(unicode_value=u'encoded', tag=u'encoded')
useChoice._InitializeFacetMap(useChoice._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'useChoice', useChoice)

# List SimpleTypeDefinition
# superclasses pyxb.binding.datatypes.anySimpleType
class tParts (pyxb.binding.basis.STD_list):

    """Simple type that is a list of pyxb.binding.datatypes.NMTOKEN."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tParts')
    _Documentation = None

    _ItemType = pyxb.binding.datatypes.NMTOKEN
tParts._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'tParts', tParts)

# Atomic SimpleTypeDefinition
class tStyleChoice (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tStyleChoice')
    _Documentation = None
tStyleChoice._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=tStyleChoice, enum_prefix=None)
tStyleChoice.rpc = tStyleChoice._CF_enumeration.addEnumeration(unicode_value=u'rpc', tag=u'rpc')
tStyleChoice.document = tStyleChoice._CF_enumeration.addEnumeration(unicode_value=u'document', tag=u'document')
tStyleChoice._InitializeFacetMap(tStyleChoice._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'tStyleChoice', tStyleChoice)

# Complex type tHeaderFault with content type EMPTY
class tHeaderFault (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tHeaderFault')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute message uses Python identifier message
    __message = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'message'), 'message', '__httpschemas_xmlsoap_orgwsdlsoap12_tHeaderFault_message', pyxb.binding.datatypes.QName, required=True)
    
    message = property(__message.value, __message.set, None, None)

    
    # Attribute encodingStyle uses Python identifier encodingStyle
    __encodingStyle = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'encodingStyle'), 'encodingStyle', '__httpschemas_xmlsoap_orgwsdlsoap12_tHeaderFault_encodingStyle', pyxb.binding.datatypes.anyURI)
    
    encodingStyle = property(__encodingStyle.value, __encodingStyle.set, None, None)

    
    # Attribute use uses Python identifier use
    __use = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'use'), 'use', '__httpschemas_xmlsoap_orgwsdlsoap12_tHeaderFault_use', useChoice, required=True)
    
    use = property(__use.value, __use.set, None, None)

    
    # Attribute namespace uses Python identifier namespace
    __namespace = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'namespace'), 'namespace', '__httpschemas_xmlsoap_orgwsdlsoap12_tHeaderFault_namespace', pyxb.binding.datatypes.anyURI)
    
    namespace = property(__namespace.value, __namespace.set, None, None)

    
    # Attribute part uses Python identifier part
    __part = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'part'), 'part', '__httpschemas_xmlsoap_orgwsdlsoap12_tHeaderFault_part', pyxb.binding.datatypes.NMTOKEN, required=True)
    
    part = property(__part.value, __part.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/soap12/'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __message.name() : __message,
        __encodingStyle.name() : __encodingStyle,
        __use.name() : __use,
        __namespace.name() : __namespace,
        __part.name() : __part
    }
Namespace.addCategoryObject('typeBinding', u'tHeaderFault', tHeaderFault)


# Complex type tExtensibilityElementOpenAttrs with content type EMPTY
class tExtensibilityElementOpenAttrs (pyxb.bundles.wssplat.wsdl11.tExtensibilityElement):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tExtensibilityElementOpenAttrs')
    # Base type is pyxb.bundles.wssplat.wsdl11.tExtensibilityElement
    
    # Attribute required inherited from {http://schemas.xmlsoap.org/wsdl/}tExtensibilityElement
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/soap12/'))

    _ElementMap = pyxb.bundles.wssplat.wsdl11.tExtensibilityElement._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = pyxb.bundles.wssplat.wsdl11.tExtensibilityElement._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tExtensibilityElementOpenAttrs', tExtensibilityElementOpenAttrs)


# Complex type tBody with content type EMPTY
class tBody (tExtensibilityElementOpenAttrs):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tBody')
    # Base type is tExtensibilityElementOpenAttrs
    
    # Attribute encodingStyle uses Python identifier encodingStyle
    __encodingStyle = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'encodingStyle'), 'encodingStyle', '__httpschemas_xmlsoap_orgwsdlsoap12_tBody_encodingStyle', pyxb.binding.datatypes.anyURI)
    
    encodingStyle = property(__encodingStyle.value, __encodingStyle.set, None, None)

    
    # Attribute use uses Python identifier use
    __use = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'use'), 'use', '__httpschemas_xmlsoap_orgwsdlsoap12_tBody_use', useChoice)
    
    use = property(__use.value, __use.set, None, None)

    
    # Attribute parts uses Python identifier parts
    __parts = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'parts'), 'parts', '__httpschemas_xmlsoap_orgwsdlsoap12_tBody_parts', tParts)
    
    parts = property(__parts.value, __parts.set, None, None)

    
    # Attribute required inherited from {http://schemas.xmlsoap.org/wsdl/}tExtensibilityElement
    
    # Attribute namespace uses Python identifier namespace
    __namespace = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'namespace'), 'namespace', '__httpschemas_xmlsoap_orgwsdlsoap12_tBody_namespace', pyxb.binding.datatypes.anyURI)
    
    namespace = property(__namespace.value, __namespace.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/soap12/'))

    _ElementMap = tExtensibilityElementOpenAttrs._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibilityElementOpenAttrs._AttributeMap.copy()
    _AttributeMap.update({
        __encodingStyle.name() : __encodingStyle,
        __use.name() : __use,
        __parts.name() : __parts,
        __namespace.name() : __namespace
    })
Namespace.addCategoryObject('typeBinding', u'tBody', tBody)


# Complex type tFaultRes with content type EMPTY
class tFaultRes (tBody):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tFaultRes')
    # Base type is tBody
    
    # Attribute required is restricted from parent
    
    # Attribute {http://schemas.xmlsoap.org/wsdl/}required uses Python identifier required
    __required = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://schemas.xmlsoap.org/wsdl/'), u'required'), 'required', '__httpschemas_xmlsoap_orgwsdl_tExtensibilityElement_httpschemas_xmlsoap_orgwsdlrequired', pyxb.binding.datatypes.boolean)
    
    required = property(__required.value, __required.set, None, None)

    
    # Attribute use is restricted from parent
    
    # Attribute use uses Python identifier use
    __use = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'use'), 'use', '__httpschemas_xmlsoap_orgwsdlsoap12_tBody_use', useChoice)
    
    use = property(__use.value, __use.set, None, None)

    
    # Attribute parts is restricted from parent
    
    # Attribute parts uses Python identifier parts
    __parts = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'parts'), 'parts', '__httpschemas_xmlsoap_orgwsdlsoap12_tBody_parts', tParts, prohibited=True)
    
    parts = property()

    
    # Attribute encodingStyle is restricted from parent
    
    # Attribute encodingStyle uses Python identifier encodingStyle
    __encodingStyle = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'encodingStyle'), 'encodingStyle', '__httpschemas_xmlsoap_orgwsdlsoap12_tBody_encodingStyle', pyxb.binding.datatypes.anyURI)
    
    encodingStyle = property(__encodingStyle.value, __encodingStyle.set, None, None)

    
    # Attribute namespace is restricted from parent
    
    # Attribute namespace uses Python identifier namespace
    __namespace = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'namespace'), 'namespace', '__httpschemas_xmlsoap_orgwsdlsoap12_tBody_namespace', pyxb.binding.datatypes.anyURI)
    
    namespace = property(__namespace.value, __namespace.set, None, None)


    _ElementMap = tBody._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tBody._AttributeMap.copy()
    _AttributeMap.update({
        __required.name() : __required,
        __use.name() : __use,
        __parts.name() : __parts,
        __encodingStyle.name() : __encodingStyle,
        __namespace.name() : __namespace
    })
Namespace.addCategoryObject('typeBinding', u'tFaultRes', tFaultRes)


# Complex type tFault with content type EMPTY
class tFault (tFaultRes):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tFault')
    # Base type is tFaultRes
    
    # Attribute use_ inherited from {http://schemas.xmlsoap.org/wsdl/soap12/}tFaultRes
    
    # Attribute required_ inherited from {http://schemas.xmlsoap.org/wsdl/soap12/}tFaultRes
    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgwsdlsoap12_tFault_name', pyxb.binding.datatypes.NCName, required=True)
    
    name = property(__name.value, __name.set, None, None)

    
    # Attribute namespace_ inherited from {http://schemas.xmlsoap.org/wsdl/soap12/}tFaultRes
    
    # Attribute parts_ inherited from {http://schemas.xmlsoap.org/wsdl/soap12/}tFaultRes
    
    # Attribute encodingStyle_ inherited from {http://schemas.xmlsoap.org/wsdl/soap12/}tFaultRes

    _ElementMap = tFaultRes._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tFaultRes._AttributeMap.copy()
    _AttributeMap.update({
        __name.name() : __name
    })
Namespace.addCategoryObject('typeBinding', u'tFault', tFault)


# Complex type tAddress with content type EMPTY
class tAddress (tExtensibilityElementOpenAttrs):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tAddress')
    # Base type is tExtensibilityElementOpenAttrs
    
    # Attribute location uses Python identifier location
    __location = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'location'), 'location', '__httpschemas_xmlsoap_orgwsdlsoap12_tAddress_location', pyxb.binding.datatypes.anyURI, required=True)
    
    location = property(__location.value, __location.set, None, None)

    
    # Attribute required inherited from {http://schemas.xmlsoap.org/wsdl/}tExtensibilityElement
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/soap12/'))

    _ElementMap = tExtensibilityElementOpenAttrs._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibilityElementOpenAttrs._AttributeMap.copy()
    _AttributeMap.update({
        __location.name() : __location
    })
Namespace.addCategoryObject('typeBinding', u'tAddress', tAddress)


# Complex type tOperation with content type EMPTY
class tOperation (tExtensibilityElementOpenAttrs):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tOperation')
    # Base type is tExtensibilityElementOpenAttrs
    
    # Attribute soapActionRequired uses Python identifier soapActionRequired
    __soapActionRequired = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'soapActionRequired'), 'soapActionRequired', '__httpschemas_xmlsoap_orgwsdlsoap12_tOperation_soapActionRequired', pyxb.binding.datatypes.boolean)
    
    soapActionRequired = property(__soapActionRequired.value, __soapActionRequired.set, None, None)

    
    # Attribute soapAction uses Python identifier soapAction
    __soapAction = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'soapAction'), 'soapAction', '__httpschemas_xmlsoap_orgwsdlsoap12_tOperation_soapAction', pyxb.binding.datatypes.anyURI)
    
    soapAction = property(__soapAction.value, __soapAction.set, None, None)

    
    # Attribute required inherited from {http://schemas.xmlsoap.org/wsdl/}tExtensibilityElement
    
    # Attribute style uses Python identifier style
    __style = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'style'), 'style', '__httpschemas_xmlsoap_orgwsdlsoap12_tOperation_style', tStyleChoice)
    
    style = property(__style.value, __style.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/soap12/'))

    _ElementMap = tExtensibilityElementOpenAttrs._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibilityElementOpenAttrs._AttributeMap.copy()
    _AttributeMap.update({
        __soapActionRequired.name() : __soapActionRequired,
        __soapAction.name() : __soapAction,
        __style.name() : __style
    })
Namespace.addCategoryObject('typeBinding', u'tOperation', tOperation)


# Complex type tBinding with content type EMPTY
class tBinding (tExtensibilityElementOpenAttrs):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tBinding')
    # Base type is tExtensibilityElementOpenAttrs
    
    # Attribute style uses Python identifier style
    __style = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'style'), 'style', '__httpschemas_xmlsoap_orgwsdlsoap12_tBinding_style', tStyleChoice)
    
    style = property(__style.value, __style.set, None, None)

    
    # Attribute required inherited from {http://schemas.xmlsoap.org/wsdl/}tExtensibilityElement
    
    # Attribute transport uses Python identifier transport
    __transport = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'transport'), 'transport', '__httpschemas_xmlsoap_orgwsdlsoap12_tBinding_transport', pyxb.binding.datatypes.anyURI, required=True)
    
    transport = property(__transport.value, __transport.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/soap12/'))

    _ElementMap = tExtensibilityElementOpenAttrs._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibilityElementOpenAttrs._AttributeMap.copy()
    _AttributeMap.update({
        __style.name() : __style,
        __transport.name() : __transport
    })
Namespace.addCategoryObject('typeBinding', u'tBinding', tBinding)


# Complex type tHeader with content type ELEMENT_ONLY
class tHeader (tExtensibilityElementOpenAttrs):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tHeader')
    # Base type is tExtensibilityElementOpenAttrs
    
    # Element {http://schemas.xmlsoap.org/wsdl/soap12/}headerfault uses Python identifier headerfault
    __headerfault = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'headerfault'), 'headerfault', '__httpschemas_xmlsoap_orgwsdlsoap12_tHeader_httpschemas_xmlsoap_orgwsdlsoap12headerfault', True)

    
    headerfault = property(__headerfault.value, __headerfault.set, None, None)

    
    # Attribute encodingStyle uses Python identifier encodingStyle
    __encodingStyle = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'encodingStyle'), 'encodingStyle', '__httpschemas_xmlsoap_orgwsdlsoap12_tHeader_encodingStyle', pyxb.binding.datatypes.anyURI)
    
    encodingStyle = property(__encodingStyle.value, __encodingStyle.set, None, None)

    
    # Attribute namespace uses Python identifier namespace
    __namespace = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'namespace'), 'namespace', '__httpschemas_xmlsoap_orgwsdlsoap12_tHeader_namespace', pyxb.binding.datatypes.anyURI)
    
    namespace = property(__namespace.value, __namespace.set, None, None)

    
    # Attribute part uses Python identifier part
    __part = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'part'), 'part', '__httpschemas_xmlsoap_orgwsdlsoap12_tHeader_part', pyxb.binding.datatypes.NMTOKEN, required=True)
    
    part = property(__part.value, __part.set, None, None)

    
    # Attribute message uses Python identifier message
    __message = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'message'), 'message', '__httpschemas_xmlsoap_orgwsdlsoap12_tHeader_message', pyxb.binding.datatypes.QName, required=True)
    
    message = property(__message.value, __message.set, None, None)

    
    # Attribute required inherited from {http://schemas.xmlsoap.org/wsdl/}tExtensibilityElement
    
    # Attribute use uses Python identifier use
    __use = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'use'), 'use', '__httpschemas_xmlsoap_orgwsdlsoap12_tHeader_use', useChoice, required=True)
    
    use = property(__use.value, __use.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/soap12/'))

    _ElementMap = tExtensibilityElementOpenAttrs._ElementMap.copy()
    _ElementMap.update({
        __headerfault.name() : __headerfault
    })
    _AttributeMap = tExtensibilityElementOpenAttrs._AttributeMap.copy()
    _AttributeMap.update({
        __encodingStyle.name() : __encodingStyle,
        __namespace.name() : __namespace,
        __part.name() : __part,
        __message.name() : __message,
        __use.name() : __use
    })
Namespace.addCategoryObject('typeBinding', u'tHeader', tHeader)


headerfault = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'headerfault'), tHeaderFault)
Namespace.addCategoryObject('elementBinding', headerfault.name().localName(), headerfault)

fault = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'fault'), tFault)
Namespace.addCategoryObject('elementBinding', fault.name().localName(), fault)

address = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'address'), tAddress)
Namespace.addCategoryObject('elementBinding', address.name().localName(), address)

operation = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'operation'), tOperation)
Namespace.addCategoryObject('elementBinding', operation.name().localName(), operation)

binding = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'binding'), tBinding)
Namespace.addCategoryObject('elementBinding', binding.name().localName(), binding)

body = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'body'), tBody)
Namespace.addCategoryObject('elementBinding', body.name().localName(), body)

header = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'header'), tHeader)
Namespace.addCategoryObject('elementBinding', header.name().localName(), header)



tHeader._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'headerfault'), tHeaderFault, scope=tHeader))
tHeader._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tHeader._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'headerfault')), min_occurs=0L, max_occurs=None)
    )
tHeader._ContentModel = pyxb.binding.content.ParticleModel(tHeader._GroupModel, min_occurs=1, max_occurs=1)

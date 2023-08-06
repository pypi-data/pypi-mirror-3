# ./pyxb/bundles/wssplat/raw/wsrm.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:51117966240f7c6b98d95f1b3ed6125f819a832c
# Generated 2012-06-15 14:42:58.922926 by PyXB version 1.1.4
# Namespace http://docs.oasis-open.org/ws-rx/wsrm/200702

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:4f862412-b722-11e1-be26-c8600024e903')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes
import pyxb.bundles.wssplat.wsa

Namespace = pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/ws-rx/wsrm/200702', create_if_missing=True)
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
class IncompleteSequenceBehaviorType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'IncompleteSequenceBehaviorType')
    _Documentation = None
IncompleteSequenceBehaviorType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=IncompleteSequenceBehaviorType, enum_prefix=None)
IncompleteSequenceBehaviorType.DiscardEntireSequence = IncompleteSequenceBehaviorType._CF_enumeration.addEnumeration(unicode_value=u'DiscardEntireSequence', tag=u'DiscardEntireSequence')
IncompleteSequenceBehaviorType.DiscardFollowingFirstGap = IncompleteSequenceBehaviorType._CF_enumeration.addEnumeration(unicode_value=u'DiscardFollowingFirstGap', tag=u'DiscardFollowingFirstGap')
IncompleteSequenceBehaviorType.NoDiscard = IncompleteSequenceBehaviorType._CF_enumeration.addEnumeration(unicode_value=u'NoDiscard', tag=u'NoDiscard')
IncompleteSequenceBehaviorType._InitializeFacetMap(IncompleteSequenceBehaviorType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'IncompleteSequenceBehaviorType', IncompleteSequenceBehaviorType)

# Atomic SimpleTypeDefinition
class MessageNumberType (pyxb.binding.datatypes.unsignedLong):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'MessageNumberType')
    _Documentation = None
MessageNumberType._CF_maxInclusive = pyxb.binding.facets.CF_maxInclusive(value_datatype=MessageNumberType, value=pyxb.binding.datatypes.unsignedLong(9223372036854775807L))
MessageNumberType._CF_minInclusive = pyxb.binding.facets.CF_minInclusive(value_datatype=MessageNumberType, value=pyxb.binding.datatypes.unsignedLong(1L))
MessageNumberType._InitializeFacetMap(MessageNumberType._CF_maxInclusive,
   MessageNumberType._CF_minInclusive)
Namespace.addCategoryObject('typeBinding', u'MessageNumberType', MessageNumberType)

# Atomic SimpleTypeDefinition
class STD_ANON (pyxb.binding.datatypes.QName):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON._InitializeFacetMap()

# Atomic SimpleTypeDefinition
class FaultCodes (pyxb.binding.datatypes.QName, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'FaultCodes')
    _Documentation = None
FaultCodes._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=FaultCodes, enum_prefix=None)
FaultCodes.wsrmSequenceTerminated = FaultCodes._CF_enumeration.addEnumeration(unicode_value=u'wsrm:SequenceTerminated', tag=u'wsrmSequenceTerminated')
FaultCodes.wsrmUnknownSequence = FaultCodes._CF_enumeration.addEnumeration(unicode_value=u'wsrm:UnknownSequence', tag=u'wsrmUnknownSequence')
FaultCodes.wsrmInvalidAcknowledgement = FaultCodes._CF_enumeration.addEnumeration(unicode_value=u'wsrm:InvalidAcknowledgement', tag=u'wsrmInvalidAcknowledgement')
FaultCodes.wsrmMessageNumberRollover = FaultCodes._CF_enumeration.addEnumeration(unicode_value=u'wsrm:MessageNumberRollover', tag=u'wsrmMessageNumberRollover')
FaultCodes.wsrmCreateSequenceRefused = FaultCodes._CF_enumeration.addEnumeration(unicode_value=u'wsrm:CreateSequenceRefused', tag=u'wsrmCreateSequenceRefused')
FaultCodes.wsrmSequenceClosed = FaultCodes._CF_enumeration.addEnumeration(unicode_value=u'wsrm:SequenceClosed', tag=u'wsrmSequenceClosed')
FaultCodes.wsrmWSRMRequired = FaultCodes._CF_enumeration.addEnumeration(unicode_value=u'wsrm:WSRMRequired', tag=u'wsrmWSRMRequired')
FaultCodes._InitializeFacetMap(FaultCodes._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'FaultCodes', FaultCodes)

# Complex type CTD_ANON with content type SIMPLE
class CTD_ANON (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.anyURI
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyURI
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



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



# Complex type SequenceFaultType with content type ELEMENT_ONLY
class SequenceFaultType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SequenceFaultType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}FaultCode uses Python identifier FaultCode
    __FaultCode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'FaultCode'), 'FaultCode', '__httpdocs_oasis_open_orgws_rxwsrm200702_SequenceFaultType_httpdocs_oasis_open_orgws_rxwsrm200702FaultCode', False)

    
    FaultCode = property(__FaultCode.value, __FaultCode.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}Detail uses Python identifier Detail
    __Detail = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Detail'), 'Detail', '__httpdocs_oasis_open_orgws_rxwsrm200702_SequenceFaultType_httpdocs_oasis_open_orgws_rxwsrm200702Detail', False)

    
    Detail = property(__Detail.value, __Detail.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))
    _HasWildcardElement = True

    _ElementMap = {
        __FaultCode.name() : __FaultCode,
        __Detail.name() : __Detail
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'SequenceFaultType', SequenceFaultType)


# Complex type CreateSequenceType with content type ELEMENT_ONLY
class CreateSequenceType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'CreateSequenceType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}Expires uses Python identifier Expires
    __Expires = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Expires'), 'Expires', '__httpdocs_oasis_open_orgws_rxwsrm200702_CreateSequenceType_httpdocs_oasis_open_orgws_rxwsrm200702Expires', False)

    
    Expires = property(__Expires.value, __Expires.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}AcksTo uses Python identifier AcksTo
    __AcksTo = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AcksTo'), 'AcksTo', '__httpdocs_oasis_open_orgws_rxwsrm200702_CreateSequenceType_httpdocs_oasis_open_orgws_rxwsrm200702AcksTo', False)

    
    AcksTo = property(__AcksTo.value, __AcksTo.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}Offer uses Python identifier Offer
    __Offer = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Offer'), 'Offer', '__httpdocs_oasis_open_orgws_rxwsrm200702_CreateSequenceType_httpdocs_oasis_open_orgws_rxwsrm200702Offer', False)

    
    Offer = property(__Offer.value, __Offer.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))
    _HasWildcardElement = True

    _ElementMap = {
        __Expires.name() : __Expires,
        __AcksTo.name() : __AcksTo,
        __Offer.name() : __Offer
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'CreateSequenceType', CreateSequenceType)


# Complex type OfferType with content type ELEMENT_ONLY
class OfferType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'OfferType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}Identifier uses Python identifier Identifier
    __Identifier = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), 'Identifier', '__httpdocs_oasis_open_orgws_rxwsrm200702_OfferType_httpdocs_oasis_open_orgws_rxwsrm200702Identifier', False)

    
    Identifier = property(__Identifier.value, __Identifier.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}IncompleteSequenceBehavior uses Python identifier IncompleteSequenceBehavior
    __IncompleteSequenceBehavior = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'IncompleteSequenceBehavior'), 'IncompleteSequenceBehavior', '__httpdocs_oasis_open_orgws_rxwsrm200702_OfferType_httpdocs_oasis_open_orgws_rxwsrm200702IncompleteSequenceBehavior', False)

    
    IncompleteSequenceBehavior = property(__IncompleteSequenceBehavior.value, __IncompleteSequenceBehavior.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}Endpoint uses Python identifier Endpoint
    __Endpoint = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Endpoint'), 'Endpoint', '__httpdocs_oasis_open_orgws_rxwsrm200702_OfferType_httpdocs_oasis_open_orgws_rxwsrm200702Endpoint', False)

    
    Endpoint = property(__Endpoint.value, __Endpoint.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}Expires uses Python identifier Expires
    __Expires = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Expires'), 'Expires', '__httpdocs_oasis_open_orgws_rxwsrm200702_OfferType_httpdocs_oasis_open_orgws_rxwsrm200702Expires', False)

    
    Expires = property(__Expires.value, __Expires.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))
    _HasWildcardElement = True

    _ElementMap = {
        __Identifier.name() : __Identifier,
        __IncompleteSequenceBehavior.name() : __IncompleteSequenceBehavior,
        __Endpoint.name() : __Endpoint,
        __Expires.name() : __Expires
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'OfferType', OfferType)


# Complex type CreateSequenceResponseType with content type ELEMENT_ONLY
class CreateSequenceResponseType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'CreateSequenceResponseType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}Identifier uses Python identifier Identifier
    __Identifier = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), 'Identifier', '__httpdocs_oasis_open_orgws_rxwsrm200702_CreateSequenceResponseType_httpdocs_oasis_open_orgws_rxwsrm200702Identifier', False)

    
    Identifier = property(__Identifier.value, __Identifier.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}Expires uses Python identifier Expires
    __Expires = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Expires'), 'Expires', '__httpdocs_oasis_open_orgws_rxwsrm200702_CreateSequenceResponseType_httpdocs_oasis_open_orgws_rxwsrm200702Expires', False)

    
    Expires = property(__Expires.value, __Expires.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}IncompleteSequenceBehavior uses Python identifier IncompleteSequenceBehavior
    __IncompleteSequenceBehavior = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'IncompleteSequenceBehavior'), 'IncompleteSequenceBehavior', '__httpdocs_oasis_open_orgws_rxwsrm200702_CreateSequenceResponseType_httpdocs_oasis_open_orgws_rxwsrm200702IncompleteSequenceBehavior', False)

    
    IncompleteSequenceBehavior = property(__IncompleteSequenceBehavior.value, __IncompleteSequenceBehavior.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}Accept uses Python identifier Accept
    __Accept = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Accept'), 'Accept', '__httpdocs_oasis_open_orgws_rxwsrm200702_CreateSequenceResponseType_httpdocs_oasis_open_orgws_rxwsrm200702Accept', False)

    
    Accept = property(__Accept.value, __Accept.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))
    _HasWildcardElement = True

    _ElementMap = {
        __Identifier.name() : __Identifier,
        __Expires.name() : __Expires,
        __IncompleteSequenceBehavior.name() : __IncompleteSequenceBehavior,
        __Accept.name() : __Accept
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'CreateSequenceResponseType', CreateSequenceResponseType)


# Complex type SequenceType with content type ELEMENT_ONLY
class SequenceType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SequenceType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}Identifier uses Python identifier Identifier
    __Identifier = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), 'Identifier', '__httpdocs_oasis_open_orgws_rxwsrm200702_SequenceType_httpdocs_oasis_open_orgws_rxwsrm200702Identifier', False)

    
    Identifier = property(__Identifier.value, __Identifier.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}MessageNumber uses Python identifier MessageNumber
    __MessageNumber = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'MessageNumber'), 'MessageNumber', '__httpdocs_oasis_open_orgws_rxwsrm200702_SequenceType_httpdocs_oasis_open_orgws_rxwsrm200702MessageNumber', False)

    
    MessageNumber = property(__MessageNumber.value, __MessageNumber.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))
    _HasWildcardElement = True

    _ElementMap = {
        __Identifier.name() : __Identifier,
        __MessageNumber.name() : __MessageNumber
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'SequenceType', SequenceType)


# Complex type CTD_ANON_2 with content type SIMPLE
class CTD_ANON_2 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.anyURI
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyURI
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type CTD_ANON_3 with content type ELEMENT_ONLY
class CTD_ANON_3 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}Nack uses Python identifier Nack
    __Nack = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Nack'), 'Nack', '__httpdocs_oasis_open_orgws_rxwsrm200702_CTD_ANON_3_httpdocs_oasis_open_orgws_rxwsrm200702Nack', True)

    
    Nack = property(__Nack.value, __Nack.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}Identifier uses Python identifier Identifier
    __Identifier = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), 'Identifier', '__httpdocs_oasis_open_orgws_rxwsrm200702_CTD_ANON_3_httpdocs_oasis_open_orgws_rxwsrm200702Identifier', False)

    
    Identifier = property(__Identifier.value, __Identifier.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}None uses Python identifier None_
    __None = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'None'), 'None_', '__httpdocs_oasis_open_orgws_rxwsrm200702_CTD_ANON_3_httpdocs_oasis_open_orgws_rxwsrm200702None', False)

    
    None_ = property(__None.value, __None.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}Final uses Python identifier Final
    __Final = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Final'), 'Final', '__httpdocs_oasis_open_orgws_rxwsrm200702_CTD_ANON_3_httpdocs_oasis_open_orgws_rxwsrm200702Final', False)

    
    Final = property(__Final.value, __Final.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}AcknowledgementRange uses Python identifier AcknowledgementRange
    __AcknowledgementRange = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AcknowledgementRange'), 'AcknowledgementRange', '__httpdocs_oasis_open_orgws_rxwsrm200702_CTD_ANON_3_httpdocs_oasis_open_orgws_rxwsrm200702AcknowledgementRange', True)

    
    AcknowledgementRange = property(__AcknowledgementRange.value, __AcknowledgementRange.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))
    _HasWildcardElement = True

    _ElementMap = {
        __Nack.name() : __Nack,
        __Identifier.name() : __Identifier,
        __None.name() : __None,
        __Final.name() : __Final,
        __AcknowledgementRange.name() : __AcknowledgementRange
    }
    _AttributeMap = {
        
    }



# Complex type TerminateSequenceType with content type ELEMENT_ONLY
class TerminateSequenceType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TerminateSequenceType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}Identifier uses Python identifier Identifier
    __Identifier = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), 'Identifier', '__httpdocs_oasis_open_orgws_rxwsrm200702_TerminateSequenceType_httpdocs_oasis_open_orgws_rxwsrm200702Identifier', False)

    
    Identifier = property(__Identifier.value, __Identifier.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}LastMsgNumber uses Python identifier LastMsgNumber
    __LastMsgNumber = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LastMsgNumber'), 'LastMsgNumber', '__httpdocs_oasis_open_orgws_rxwsrm200702_TerminateSequenceType_httpdocs_oasis_open_orgws_rxwsrm200702LastMsgNumber', False)

    
    LastMsgNumber = property(__LastMsgNumber.value, __LastMsgNumber.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))
    _HasWildcardElement = True

    _ElementMap = {
        __Identifier.name() : __Identifier,
        __LastMsgNumber.name() : __LastMsgNumber
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'TerminateSequenceType', TerminateSequenceType)


# Complex type TerminateSequenceResponseType with content type ELEMENT_ONLY
class TerminateSequenceResponseType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TerminateSequenceResponseType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}Identifier uses Python identifier Identifier
    __Identifier = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), 'Identifier', '__httpdocs_oasis_open_orgws_rxwsrm200702_TerminateSequenceResponseType_httpdocs_oasis_open_orgws_rxwsrm200702Identifier', False)

    
    Identifier = property(__Identifier.value, __Identifier.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))
    _HasWildcardElement = True

    _ElementMap = {
        __Identifier.name() : __Identifier
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'TerminateSequenceResponseType', TerminateSequenceResponseType)


# Complex type CTD_ANON_4 with content type EMPTY
class CTD_ANON_4 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type CloseSequenceType with content type ELEMENT_ONLY
class CloseSequenceType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'CloseSequenceType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}Identifier uses Python identifier Identifier
    __Identifier = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), 'Identifier', '__httpdocs_oasis_open_orgws_rxwsrm200702_CloseSequenceType_httpdocs_oasis_open_orgws_rxwsrm200702Identifier', False)

    
    Identifier = property(__Identifier.value, __Identifier.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}LastMsgNumber uses Python identifier LastMsgNumber
    __LastMsgNumber = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LastMsgNumber'), 'LastMsgNumber', '__httpdocs_oasis_open_orgws_rxwsrm200702_CloseSequenceType_httpdocs_oasis_open_orgws_rxwsrm200702LastMsgNumber', False)

    
    LastMsgNumber = property(__LastMsgNumber.value, __LastMsgNumber.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))
    _HasWildcardElement = True

    _ElementMap = {
        __Identifier.name() : __Identifier,
        __LastMsgNumber.name() : __LastMsgNumber
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'CloseSequenceType', CloseSequenceType)


# Complex type CTD_ANON_5 with content type EMPTY
class CTD_ANON_5 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type AckRequestedType with content type ELEMENT_ONLY
class AckRequestedType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AckRequestedType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}Identifier uses Python identifier Identifier
    __Identifier = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), 'Identifier', '__httpdocs_oasis_open_orgws_rxwsrm200702_AckRequestedType_httpdocs_oasis_open_orgws_rxwsrm200702Identifier', False)

    
    Identifier = property(__Identifier.value, __Identifier.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))
    _HasWildcardElement = True

    _ElementMap = {
        __Identifier.name() : __Identifier
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'AckRequestedType', AckRequestedType)


# Complex type CTD_ANON_6 with content type SIMPLE
class CTD_ANON_6 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.duration
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.duration
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type CloseSequenceResponseType with content type ELEMENT_ONLY
class CloseSequenceResponseType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'CloseSequenceResponseType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}Identifier uses Python identifier Identifier
    __Identifier = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), 'Identifier', '__httpdocs_oasis_open_orgws_rxwsrm200702_CloseSequenceResponseType_httpdocs_oasis_open_orgws_rxwsrm200702Identifier', False)

    
    Identifier = property(__Identifier.value, __Identifier.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))
    _HasWildcardElement = True

    _ElementMap = {
        __Identifier.name() : __Identifier
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'CloseSequenceResponseType', CloseSequenceResponseType)


# Complex type CTD_ANON_7 with content type EMPTY
class CTD_ANON_7 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type CTD_ANON_8 with content type EMPTY
class CTD_ANON_8 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Upper uses Python identifier Upper
    __Upper = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Upper'), 'Upper', '__httpdocs_oasis_open_orgws_rxwsrm200702_CTD_ANON_8_Upper', pyxb.binding.datatypes.unsignedLong, required=True)
    
    Upper = property(__Upper.value, __Upper.set, None, None)

    
    # Attribute Lower uses Python identifier Lower
    __Lower = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Lower'), 'Lower', '__httpdocs_oasis_open_orgws_rxwsrm200702_CTD_ANON_8_Lower', pyxb.binding.datatypes.unsignedLong, required=True)
    
    Lower = property(__Lower.value, __Lower.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Upper.name() : __Upper,
        __Lower.name() : __Lower
    }



# Complex type DetailType with content type ELEMENT_ONLY
class DetailType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'DetailType')
    # Base type is pyxb.binding.datatypes.anyType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'DetailType', DetailType)


# Complex type AcceptType with content type ELEMENT_ONLY
class AcceptType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AcceptType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}AcksTo uses Python identifier AcksTo
    __AcksTo = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AcksTo'), 'AcksTo', '__httpdocs_oasis_open_orgws_rxwsrm200702_AcceptType_httpdocs_oasis_open_orgws_rxwsrm200702AcksTo', False)

    
    AcksTo = property(__AcksTo.value, __AcksTo.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))
    _HasWildcardElement = True

    _ElementMap = {
        __AcksTo.name() : __AcksTo
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'AcceptType', AcceptType)


SequenceFault = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SequenceFault'), SequenceFaultType)
Namespace.addCategoryObject('elementBinding', SequenceFault.name().localName(), SequenceFault)

CreateSequence = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CreateSequence'), CreateSequenceType)
Namespace.addCategoryObject('elementBinding', CreateSequence.name().localName(), CreateSequence)

CreateSequenceResponse = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CreateSequenceResponse'), CreateSequenceResponseType)
Namespace.addCategoryObject('elementBinding', CreateSequenceResponse.name().localName(), CreateSequenceResponse)

Sequence = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Sequence'), SequenceType)
Namespace.addCategoryObject('elementBinding', Sequence.name().localName(), Sequence)

Address = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Address'), CTD_ANON_2)
Namespace.addCategoryObject('elementBinding', Address.name().localName(), Address)

SequenceAcknowledgement = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SequenceAcknowledgement'), CTD_ANON_3)
Namespace.addCategoryObject('elementBinding', SequenceAcknowledgement.name().localName(), SequenceAcknowledgement)

TerminateSequence = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TerminateSequence'), TerminateSequenceType)
Namespace.addCategoryObject('elementBinding', TerminateSequence.name().localName(), TerminateSequence)

TerminateSequenceResponse = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TerminateSequenceResponse'), TerminateSequenceResponseType)
Namespace.addCategoryObject('elementBinding', TerminateSequenceResponse.name().localName(), TerminateSequenceResponse)

UsesSequenceSSL = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'UsesSequenceSSL'), CTD_ANON_4)
Namespace.addCategoryObject('elementBinding', UsesSequenceSSL.name().localName(), UsesSequenceSSL)

CloseSequence = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CloseSequence'), CloseSequenceType)
Namespace.addCategoryObject('elementBinding', CloseSequence.name().localName(), CloseSequence)

AckRequested = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AckRequested'), AckRequestedType)
Namespace.addCategoryObject('elementBinding', AckRequested.name().localName(), AckRequested)

Identifier = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), CTD_ANON)
Namespace.addCategoryObject('elementBinding', Identifier.name().localName(), Identifier)

Expires = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Expires'), CTD_ANON_6)
Namespace.addCategoryObject('elementBinding', Expires.name().localName(), Expires)

CloseSequenceResponse = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CloseSequenceResponse'), CloseSequenceResponseType)
Namespace.addCategoryObject('elementBinding', CloseSequenceResponse.name().localName(), CloseSequenceResponse)

UsesSequenceSTR = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'UsesSequenceSTR'), CTD_ANON_7)
Namespace.addCategoryObject('elementBinding', UsesSequenceSTR.name().localName(), UsesSequenceSTR)

UnsupportedElement = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'UnsupportedElement'), STD_ANON)
Namespace.addCategoryObject('elementBinding', UnsupportedElement.name().localName(), UnsupportedElement)

AcksTo = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AcksTo'), pyxb.bundles.wssplat.wsa.EndpointReferenceType)
Namespace.addCategoryObject('elementBinding', AcksTo.name().localName(), AcksTo)



SequenceFaultType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'FaultCode'), FaultCodes, scope=SequenceFaultType))

SequenceFaultType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Detail'), DetailType, scope=SequenceFaultType))
SequenceFaultType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SequenceFaultType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'FaultCode')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(SequenceFaultType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Detail')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702')), min_occurs=0L, max_occurs=None)
    )
SequenceFaultType._ContentModel = pyxb.binding.content.ParticleModel(SequenceFaultType._GroupModel, min_occurs=1, max_occurs=1)



CreateSequenceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Expires'), CTD_ANON_6, scope=CreateSequenceType))

CreateSequenceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AcksTo'), pyxb.bundles.wssplat.wsa.EndpointReferenceType, scope=CreateSequenceType))

CreateSequenceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Offer'), OfferType, scope=CreateSequenceType))
CreateSequenceType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CreateSequenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AcksTo')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CreateSequenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Expires')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CreateSequenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Offer')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702')), min_occurs=0L, max_occurs=None)
    )
CreateSequenceType._ContentModel = pyxb.binding.content.ParticleModel(CreateSequenceType._GroupModel, min_occurs=1, max_occurs=1)



OfferType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), CTD_ANON, scope=OfferType))

OfferType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'IncompleteSequenceBehavior'), IncompleteSequenceBehaviorType, scope=OfferType))

OfferType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Endpoint'), pyxb.bundles.wssplat.wsa.EndpointReferenceType, scope=OfferType))

OfferType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Expires'), CTD_ANON_6, scope=OfferType))
OfferType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(OfferType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Identifier')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(OfferType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Endpoint')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(OfferType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Expires')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(OfferType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'IncompleteSequenceBehavior')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702')), min_occurs=0L, max_occurs=None)
    )
OfferType._ContentModel = pyxb.binding.content.ParticleModel(OfferType._GroupModel, min_occurs=1, max_occurs=1)



CreateSequenceResponseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), CTD_ANON, scope=CreateSequenceResponseType))

CreateSequenceResponseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Expires'), CTD_ANON_6, scope=CreateSequenceResponseType))

CreateSequenceResponseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'IncompleteSequenceBehavior'), IncompleteSequenceBehaviorType, scope=CreateSequenceResponseType))

CreateSequenceResponseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Accept'), AcceptType, scope=CreateSequenceResponseType))
CreateSequenceResponseType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CreateSequenceResponseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Identifier')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CreateSequenceResponseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Expires')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CreateSequenceResponseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'IncompleteSequenceBehavior')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CreateSequenceResponseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Accept')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702')), min_occurs=0L, max_occurs=None)
    )
CreateSequenceResponseType._ContentModel = pyxb.binding.content.ParticleModel(CreateSequenceResponseType._GroupModel, min_occurs=1, max_occurs=1)



SequenceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), CTD_ANON, scope=SequenceType))

SequenceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MessageNumber'), MessageNumberType, scope=SequenceType))
SequenceType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SequenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Identifier')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(SequenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'MessageNumber')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702')), min_occurs=0L, max_occurs=None)
    )
SequenceType._ContentModel = pyxb.binding.content.ParticleModel(SequenceType._GroupModel, min_occurs=1, max_occurs=1)



CTD_ANON_3._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Nack'), pyxb.binding.datatypes.unsignedLong, scope=CTD_ANON_3))

CTD_ANON_3._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), CTD_ANON, scope=CTD_ANON_3))

CTD_ANON_3._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'None'), CTD_ANON_5, scope=CTD_ANON_3))

CTD_ANON_3._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Final'), CTD_ANON_, scope=CTD_ANON_3))

CTD_ANON_3._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AcknowledgementRange'), CTD_ANON_8, scope=CTD_ANON_3))
CTD_ANON_3._GroupModel_3 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(CTD_ANON_3._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AcknowledgementRange')), min_occurs=1, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_3._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'None')), min_occurs=1, max_occurs=1)
    )
CTD_ANON_3._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_3._GroupModel_3, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_3._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Final')), min_occurs=0L, max_occurs=1)
    )
CTD_ANON_3._GroupModel_ = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(CTD_ANON_3._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_3._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Nack')), min_occurs=1, max_occurs=None)
    )
CTD_ANON_3._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_3._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Identifier')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_3._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_3._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_3._GroupModel, min_occurs=1, max_occurs=1)



TerminateSequenceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), CTD_ANON, scope=TerminateSequenceType))

TerminateSequenceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LastMsgNumber'), MessageNumberType, scope=TerminateSequenceType))
TerminateSequenceType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TerminateSequenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Identifier')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(TerminateSequenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LastMsgNumber')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702')), min_occurs=0L, max_occurs=None)
    )
TerminateSequenceType._ContentModel = pyxb.binding.content.ParticleModel(TerminateSequenceType._GroupModel, min_occurs=1, max_occurs=1)



TerminateSequenceResponseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), CTD_ANON, scope=TerminateSequenceResponseType))
TerminateSequenceResponseType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TerminateSequenceResponseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Identifier')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702')), min_occurs=0L, max_occurs=None)
    )
TerminateSequenceResponseType._ContentModel = pyxb.binding.content.ParticleModel(TerminateSequenceResponseType._GroupModel, min_occurs=1, max_occurs=1)



CloseSequenceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), CTD_ANON, scope=CloseSequenceType))

CloseSequenceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LastMsgNumber'), MessageNumberType, scope=CloseSequenceType))
CloseSequenceType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CloseSequenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Identifier')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CloseSequenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LastMsgNumber')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702')), min_occurs=0L, max_occurs=None)
    )
CloseSequenceType._ContentModel = pyxb.binding.content.ParticleModel(CloseSequenceType._GroupModel, min_occurs=1, max_occurs=1)



AckRequestedType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), CTD_ANON, scope=AckRequestedType))
AckRequestedType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AckRequestedType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Identifier')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702')), min_occurs=0L, max_occurs=None)
    )
AckRequestedType._ContentModel = pyxb.binding.content.ParticleModel(AckRequestedType._GroupModel, min_occurs=1, max_occurs=1)



CloseSequenceResponseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), CTD_ANON, scope=CloseSequenceResponseType))
CloseSequenceResponseType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CloseSequenceResponseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Identifier')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702')), min_occurs=0L, max_occurs=None)
    )
CloseSequenceResponseType._ContentModel = pyxb.binding.content.ParticleModel(CloseSequenceResponseType._GroupModel, min_occurs=1, max_occurs=1)


DetailType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702')), min_occurs=0L, max_occurs=None)
    )
DetailType._ContentModel = pyxb.binding.content.ParticleModel(DetailType._GroupModel, min_occurs=1, max_occurs=1)



AcceptType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AcksTo'), pyxb.bundles.wssplat.wsa.EndpointReferenceType, scope=AcceptType))
AcceptType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AcceptType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AcksTo')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702')), min_occurs=0L, max_occurs=None)
    )
AcceptType._ContentModel = pyxb.binding.content.ParticleModel(AcceptType._GroupModel, min_occurs=1, max_occurs=1)

# ./pyxb/bundles/wssplat/raw/wsa.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:0ecbd27a42302a2dbf33a51269e14ce6419c0738
# Generated 2012-06-15 14:42:57.838239 by PyXB version 1.1.4
# Namespace http://www.w3.org/2005/08/addressing

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:4ee3d8ce-b722-11e1-96c7-c8600024e903')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes

Namespace = pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2005/08/addressing', create_if_missing=True)
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
class FaultCodesType (pyxb.binding.datatypes.QName, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'FaultCodesType')
    _Documentation = None
FaultCodesType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=FaultCodesType, enum_prefix=None)
FaultCodesType.tnsInvalidAddressingHeader = FaultCodesType._CF_enumeration.addEnumeration(unicode_value=u'tns:InvalidAddressingHeader', tag=u'tnsInvalidAddressingHeader')
FaultCodesType.tnsInvalidAddress = FaultCodesType._CF_enumeration.addEnumeration(unicode_value=u'tns:InvalidAddress', tag=u'tnsInvalidAddress')
FaultCodesType.tnsInvalidEPR = FaultCodesType._CF_enumeration.addEnumeration(unicode_value=u'tns:InvalidEPR', tag=u'tnsInvalidEPR')
FaultCodesType.tnsInvalidCardinality = FaultCodesType._CF_enumeration.addEnumeration(unicode_value=u'tns:InvalidCardinality', tag=u'tnsInvalidCardinality')
FaultCodesType.tnsMissingAddressInEPR = FaultCodesType._CF_enumeration.addEnumeration(unicode_value=u'tns:MissingAddressInEPR', tag=u'tnsMissingAddressInEPR')
FaultCodesType.tnsDuplicateMessageID = FaultCodesType._CF_enumeration.addEnumeration(unicode_value=u'tns:DuplicateMessageID', tag=u'tnsDuplicateMessageID')
FaultCodesType.tnsActionMismatch = FaultCodesType._CF_enumeration.addEnumeration(unicode_value=u'tns:ActionMismatch', tag=u'tnsActionMismatch')
FaultCodesType.tnsMessageAddressingHeaderRequired = FaultCodesType._CF_enumeration.addEnumeration(unicode_value=u'tns:MessageAddressingHeaderRequired', tag=u'tnsMessageAddressingHeaderRequired')
FaultCodesType.tnsDestinationUnreachable = FaultCodesType._CF_enumeration.addEnumeration(unicode_value=u'tns:DestinationUnreachable', tag=u'tnsDestinationUnreachable')
FaultCodesType.tnsActionNotSupported = FaultCodesType._CF_enumeration.addEnumeration(unicode_value=u'tns:ActionNotSupported', tag=u'tnsActionNotSupported')
FaultCodesType.tnsEndpointUnavailable = FaultCodesType._CF_enumeration.addEnumeration(unicode_value=u'tns:EndpointUnavailable', tag=u'tnsEndpointUnavailable')
FaultCodesType._InitializeFacetMap(FaultCodesType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'FaultCodesType', FaultCodesType)

# Union SimpleTypeDefinition
# superclasses pyxb.binding.datatypes.anySimpleType
class FaultCodesOpenEnumType (pyxb.binding.basis.STD_union):

    """Simple type that is a union of FaultCodesType, pyxb.binding.datatypes.QName."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'FaultCodesOpenEnumType')
    _Documentation = None

    _MemberTypes = ( FaultCodesType, pyxb.binding.datatypes.QName, )
FaultCodesOpenEnumType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=FaultCodesOpenEnumType)
FaultCodesOpenEnumType._CF_pattern = pyxb.binding.facets.CF_pattern()
FaultCodesOpenEnumType.tnsInvalidAddressingHeader = u'tns:InvalidAddressingHeader'# originally FaultCodesType.tnsInvalidAddressingHeader
FaultCodesOpenEnumType.tnsInvalidAddress = u'tns:InvalidAddress'# originally FaultCodesType.tnsInvalidAddress
FaultCodesOpenEnumType.tnsInvalidEPR = u'tns:InvalidEPR'# originally FaultCodesType.tnsInvalidEPR
FaultCodesOpenEnumType.tnsInvalidCardinality = u'tns:InvalidCardinality'# originally FaultCodesType.tnsInvalidCardinality
FaultCodesOpenEnumType.tnsMissingAddressInEPR = u'tns:MissingAddressInEPR'# originally FaultCodesType.tnsMissingAddressInEPR
FaultCodesOpenEnumType.tnsDuplicateMessageID = u'tns:DuplicateMessageID'# originally FaultCodesType.tnsDuplicateMessageID
FaultCodesOpenEnumType.tnsActionMismatch = u'tns:ActionMismatch'# originally FaultCodesType.tnsActionMismatch
FaultCodesOpenEnumType.tnsMessageAddressingHeaderRequired = u'tns:MessageAddressingHeaderRequired'# originally FaultCodesType.tnsMessageAddressingHeaderRequired
FaultCodesOpenEnumType.tnsDestinationUnreachable = u'tns:DestinationUnreachable'# originally FaultCodesType.tnsDestinationUnreachable
FaultCodesOpenEnumType.tnsActionNotSupported = u'tns:ActionNotSupported'# originally FaultCodesType.tnsActionNotSupported
FaultCodesOpenEnumType.tnsEndpointUnavailable = u'tns:EndpointUnavailable'# originally FaultCodesType.tnsEndpointUnavailable
FaultCodesOpenEnumType._InitializeFacetMap(FaultCodesOpenEnumType._CF_enumeration,
   FaultCodesOpenEnumType._CF_pattern)
Namespace.addCategoryObject('typeBinding', u'FaultCodesOpenEnumType', FaultCodesOpenEnumType)

# Atomic SimpleTypeDefinition
class RelationshipType (pyxb.binding.datatypes.anyURI, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'RelationshipType')
    _Documentation = None
RelationshipType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=RelationshipType, enum_prefix=None)
RelationshipType.httpwww_w3_org200508addressingreply = RelationshipType._CF_enumeration.addEnumeration(unicode_value=u'http://www.w3.org/2005/08/addressing/reply', tag=u'httpwww_w3_org200508addressingreply')
RelationshipType._InitializeFacetMap(RelationshipType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'RelationshipType', RelationshipType)

# Union SimpleTypeDefinition
# superclasses pyxb.binding.datatypes.anySimpleType
class RelationshipTypeOpenEnum (pyxb.binding.basis.STD_union):

    """Simple type that is a union of RelationshipType, pyxb.binding.datatypes.anyURI."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'RelationshipTypeOpenEnum')
    _Documentation = None

    _MemberTypes = ( RelationshipType, pyxb.binding.datatypes.anyURI, )
RelationshipTypeOpenEnum._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=RelationshipTypeOpenEnum)
RelationshipTypeOpenEnum._CF_pattern = pyxb.binding.facets.CF_pattern()
RelationshipTypeOpenEnum.httpwww_w3_org200508addressingreply = u'http://www.w3.org/2005/08/addressing/reply'# originally RelationshipType.httpwww_w3_org200508addressingreply
RelationshipTypeOpenEnum._InitializeFacetMap(RelationshipTypeOpenEnum._CF_enumeration,
   RelationshipTypeOpenEnum._CF_pattern)
Namespace.addCategoryObject('typeBinding', u'RelationshipTypeOpenEnum', RelationshipTypeOpenEnum)

# Complex type AttributedURIType with content type SIMPLE
class AttributedURIType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.anyURI
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AttributedURIType')
    # Base type is pyxb.binding.datatypes.anyURI
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2005/08/addressing'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'AttributedURIType', AttributedURIType)


# Complex type EndpointReferenceType with content type ELEMENT_ONLY
class EndpointReferenceType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'EndpointReferenceType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2005/08/addressing}Address uses Python identifier Address
    __Address = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Address'), 'Address', '__httpwww_w3_org200508addressing_EndpointReferenceType_httpwww_w3_org200508addressingAddress', False)

    
    Address = property(__Address.value, __Address.set, None, None)

    
    # Element {http://www.w3.org/2005/08/addressing}ReferenceParameters uses Python identifier ReferenceParameters
    __ReferenceParameters = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ReferenceParameters'), 'ReferenceParameters', '__httpwww_w3_org200508addressing_EndpointReferenceType_httpwww_w3_org200508addressingReferenceParameters', False)

    
    ReferenceParameters = property(__ReferenceParameters.value, __ReferenceParameters.set, None, None)

    
    # Element {http://www.w3.org/2005/08/addressing}Metadata uses Python identifier Metadata
    __Metadata = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Metadata'), 'Metadata', '__httpwww_w3_org200508addressing_EndpointReferenceType_httpwww_w3_org200508addressingMetadata', False)

    
    Metadata = property(__Metadata.value, __Metadata.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2005/08/addressing'))
    _HasWildcardElement = True

    _ElementMap = {
        __Address.name() : __Address,
        __ReferenceParameters.name() : __ReferenceParameters,
        __Metadata.name() : __Metadata
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'EndpointReferenceType', EndpointReferenceType)


# Complex type ProblemActionType with content type ELEMENT_ONLY
class ProblemActionType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ProblemActionType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2005/08/addressing}SoapAction uses Python identifier SoapAction
    __SoapAction = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SoapAction'), 'SoapAction', '__httpwww_w3_org200508addressing_ProblemActionType_httpwww_w3_org200508addressingSoapAction', False)

    
    SoapAction = property(__SoapAction.value, __SoapAction.set, None, None)

    
    # Element {http://www.w3.org/2005/08/addressing}Action uses Python identifier Action
    __Action = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Action'), 'Action', '__httpwww_w3_org200508addressing_ProblemActionType_httpwww_w3_org200508addressingAction', False)

    
    Action = property(__Action.value, __Action.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2005/08/addressing'))

    _ElementMap = {
        __SoapAction.name() : __SoapAction,
        __Action.name() : __Action
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'ProblemActionType', ProblemActionType)


# Complex type ReferenceParametersType with content type ELEMENT_ONLY
class ReferenceParametersType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ReferenceParametersType')
    # Base type is pyxb.binding.datatypes.anyType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2005/08/addressing'))
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'ReferenceParametersType', ReferenceParametersType)


# Complex type MetadataType with content type ELEMENT_ONLY
class MetadataType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'MetadataType')
    # Base type is pyxb.binding.datatypes.anyType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2005/08/addressing'))
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'MetadataType', MetadataType)


# Complex type RelatesToType with content type SIMPLE
class RelatesToType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.anyURI
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'RelatesToType')
    # Base type is pyxb.binding.datatypes.anyURI
    
    # Attribute RelationshipType uses Python identifier RelationshipType
    __RelationshipType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'RelationshipType'), 'RelationshipType', '__httpwww_w3_org200508addressing_RelatesToType_RelationshipType', RelationshipTypeOpenEnum, unicode_default=u'http://www.w3.org/2005/08/addressing/reply')
    
    RelationshipType = property(__RelationshipType.value, __RelationshipType.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2005/08/addressing'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __RelationshipType.name() : __RelationshipType
    }
Namespace.addCategoryObject('typeBinding', u'RelatesToType', RelatesToType)


# Complex type AttributedUnsignedLongType with content type SIMPLE
class AttributedUnsignedLongType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.unsignedLong
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AttributedUnsignedLongType')
    # Base type is pyxb.binding.datatypes.unsignedLong
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2005/08/addressing'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'AttributedUnsignedLongType', AttributedUnsignedLongType)


# Complex type AttributedQNameType with content type SIMPLE
class AttributedQNameType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.QName
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AttributedQNameType')
    # Base type is pyxb.binding.datatypes.QName
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2005/08/addressing'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'AttributedQNameType', AttributedQNameType)


FaultTo = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'FaultTo'), EndpointReferenceType)
Namespace.addCategoryObject('elementBinding', FaultTo.name().localName(), FaultTo)

EndpointReference = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'EndpointReference'), EndpointReferenceType)
Namespace.addCategoryObject('elementBinding', EndpointReference.name().localName(), EndpointReference)

From = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'From'), EndpointReferenceType)
Namespace.addCategoryObject('elementBinding', From.name().localName(), From)

To = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'To'), AttributedURIType)
Namespace.addCategoryObject('elementBinding', To.name().localName(), To)

ProblemAction = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ProblemAction'), ProblemActionType)
Namespace.addCategoryObject('elementBinding', ProblemAction.name().localName(), ProblemAction)

Action = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Action'), AttributedURIType)
Namespace.addCategoryObject('elementBinding', Action.name().localName(), Action)

ReplyTo = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ReplyTo'), EndpointReferenceType)
Namespace.addCategoryObject('elementBinding', ReplyTo.name().localName(), ReplyTo)

ReferenceParameters = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ReferenceParameters'), ReferenceParametersType)
Namespace.addCategoryObject('elementBinding', ReferenceParameters.name().localName(), ReferenceParameters)

Metadata = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Metadata'), MetadataType)
Namespace.addCategoryObject('elementBinding', Metadata.name().localName(), Metadata)

ProblemIRI = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ProblemIRI'), AttributedURIType)
Namespace.addCategoryObject('elementBinding', ProblemIRI.name().localName(), ProblemIRI)

RelatesTo = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RelatesTo'), RelatesToType)
Namespace.addCategoryObject('elementBinding', RelatesTo.name().localName(), RelatesTo)

RetryAfter = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RetryAfter'), AttributedUnsignedLongType)
Namespace.addCategoryObject('elementBinding', RetryAfter.name().localName(), RetryAfter)

MessageID = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MessageID'), AttributedURIType)
Namespace.addCategoryObject('elementBinding', MessageID.name().localName(), MessageID)

ProblemHeaderQName = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ProblemHeaderQName'), AttributedQNameType)
Namespace.addCategoryObject('elementBinding', ProblemHeaderQName.name().localName(), ProblemHeaderQName)



EndpointReferenceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Address'), AttributedURIType, scope=EndpointReferenceType))

EndpointReferenceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ReferenceParameters'), ReferenceParametersType, scope=EndpointReferenceType))

EndpointReferenceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Metadata'), MetadataType, scope=EndpointReferenceType))
EndpointReferenceType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(EndpointReferenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Address')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(EndpointReferenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ReferenceParameters')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(EndpointReferenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Metadata')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2005/08/addressing')), min_occurs=0L, max_occurs=None)
    )
EndpointReferenceType._ContentModel = pyxb.binding.content.ParticleModel(EndpointReferenceType._GroupModel, min_occurs=1, max_occurs=1)



ProblemActionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SoapAction'), pyxb.binding.datatypes.anyURI, scope=ProblemActionType))

ProblemActionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Action'), AttributedURIType, scope=ProblemActionType))
ProblemActionType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ProblemActionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Action')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ProblemActionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SoapAction')), min_occurs=0L, max_occurs=1)
    )
ProblemActionType._ContentModel = pyxb.binding.content.ParticleModel(ProblemActionType._GroupModel, min_occurs=1, max_occurs=1)


ReferenceParametersType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any), min_occurs=0L, max_occurs=None)
    )
ReferenceParametersType._ContentModel = pyxb.binding.content.ParticleModel(ReferenceParametersType._GroupModel, min_occurs=1, max_occurs=1)


MetadataType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any), min_occurs=0L, max_occurs=None)
    )
MetadataType._ContentModel = pyxb.binding.content.ParticleModel(MetadataType._GroupModel, min_occurs=1, max_occurs=1)

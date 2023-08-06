# ./pyxb/bundles/wssplat/raw/wsrf_br.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:dd5653a4ef6cf46e4740ac1eaece204a915200aa
# Generated 2012-06-15 14:42:59.890025 by PyXB version 1.1.4
# Namespace http://docs.oasis-open.org/wsn/br-2

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:501a0fa6-b722-11e1-a349-c8600024e903')

# Import bindings for namespaces imported into schema
import pyxb.bundles.wssplat.wsrf_bf
import pyxb.binding.datatypes
import pyxb.bundles.wssplat.wsnt
import pyxb.bundles.wssplat.wstop
import pyxb.bundles.wssplat.wsa

Namespace = pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsn/br-2', create_if_missing=True)
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


# Complex type PublisherRegistrationFailedFaultType with content type ELEMENT_ONLY
class PublisherRegistrationFailedFaultType (pyxb.bundles.wssplat.wsrf_bf.BaseFaultType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'PublisherRegistrationFailedFaultType')
    # Base type is pyxb.bundles.wssplat.wsrf_bf.BaseFaultType
    
    # Element Originator ({http://docs.oasis-open.org/wsrf/bf-2}Originator) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element ErrorCode ({http://docs.oasis-open.org/wsrf/bf-2}ErrorCode) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element FaultCause ({http://docs.oasis-open.org/wsrf/bf-2}FaultCause) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Description ({http://docs.oasis-open.org/wsrf/bf-2}Description) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Timestamp ({http://docs.oasis-open.org/wsrf/bf-2}Timestamp) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2'))
    _HasWildcardElement = True

    _ElementMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'PublisherRegistrationFailedFaultType', PublisherRegistrationFailedFaultType)


# Complex type CTD_ANON with content type ELEMENT_ONLY
class CTD_ANON (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type CTD_ANON_ with content type ELEMENT_ONLY
class CTD_ANON_ (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/wsn/b-2}TopicExpression uses Python identifier TopicExpression
    __TopicExpression = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsn/b-2'), u'TopicExpression'), 'TopicExpression', '__httpdocs_oasis_open_orgwsnbr_2_CTD_ANON__httpdocs_oasis_open_orgwsnb_2TopicExpression', True)

    
    TopicExpression = property(__TopicExpression.value, __TopicExpression.set, None, None)

    
    # Element {http://docs.oasis-open.org/wsn/br-2}RequiresRegistration uses Python identifier RequiresRegistration
    __RequiresRegistration = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'RequiresRegistration'), 'RequiresRegistration', '__httpdocs_oasis_open_orgwsnbr_2_CTD_ANON__httpdocs_oasis_open_orgwsnbr_2RequiresRegistration', False)

    
    RequiresRegistration = property(__RequiresRegistration.value, __RequiresRegistration.set, None, None)

    
    # Element {http://docs.oasis-open.org/wsn/t-1}TopicSet uses Python identifier TopicSet
    __TopicSet = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsn/t-1'), u'TopicSet'), 'TopicSet', '__httpdocs_oasis_open_orgwsnbr_2_CTD_ANON__httpdocs_oasis_open_orgwsnt_1TopicSet', False)

    
    TopicSet = property(__TopicSet.value, __TopicSet.set, None, None)

    
    # Element {http://docs.oasis-open.org/wsn/b-2}FixedTopicSet uses Python identifier FixedTopicSet
    __FixedTopicSet = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsn/b-2'), u'FixedTopicSet'), 'FixedTopicSet', '__httpdocs_oasis_open_orgwsnbr_2_CTD_ANON__httpdocs_oasis_open_orgwsnb_2FixedTopicSet', False)

    
    FixedTopicSet = property(__FixedTopicSet.value, __FixedTopicSet.set, None, None)

    
    # Element {http://docs.oasis-open.org/wsn/b-2}TopicExpressionDialect uses Python identifier TopicExpressionDialect
    __TopicExpressionDialect = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsn/b-2'), u'TopicExpressionDialect'), 'TopicExpressionDialect', '__httpdocs_oasis_open_orgwsnbr_2_CTD_ANON__httpdocs_oasis_open_orgwsnb_2TopicExpressionDialect', True)

    
    TopicExpressionDialect = property(__TopicExpressionDialect.value, __TopicExpressionDialect.set, None, None)


    _ElementMap = {
        __TopicExpression.name() : __TopicExpression,
        __RequiresRegistration.name() : __RequiresRegistration,
        __TopicSet.name() : __TopicSet,
        __FixedTopicSet.name() : __FixedTopicSet,
        __TopicExpressionDialect.name() : __TopicExpressionDialect
    }
    _AttributeMap = {
        
    }



# Complex type CTD_ANON_2 with content type ELEMENT_ONLY
class CTD_ANON_2 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/wsn/br-2}PublisherReference uses Python identifier PublisherReference
    __PublisherReference = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PublisherReference'), 'PublisherReference', '__httpdocs_oasis_open_orgwsnbr_2_CTD_ANON_2_httpdocs_oasis_open_orgwsnbr_2PublisherReference', False)

    
    PublisherReference = property(__PublisherReference.value, __PublisherReference.set, None, None)

    
    # Element {http://docs.oasis-open.org/wsn/br-2}Demand uses Python identifier Demand
    __Demand = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Demand'), 'Demand', '__httpdocs_oasis_open_orgwsnbr_2_CTD_ANON_2_httpdocs_oasis_open_orgwsnbr_2Demand', False)

    
    Demand = property(__Demand.value, __Demand.set, None, None)

    
    # Element {http://docs.oasis-open.org/wsn/br-2}Topic uses Python identifier Topic
    __Topic = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Topic'), 'Topic', '__httpdocs_oasis_open_orgwsnbr_2_CTD_ANON_2_httpdocs_oasis_open_orgwsnbr_2Topic', True)

    
    Topic = property(__Topic.value, __Topic.set, None, None)

    
    # Element {http://docs.oasis-open.org/wsn/br-2}InitialTerminationTime uses Python identifier InitialTerminationTime
    __InitialTerminationTime = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'InitialTerminationTime'), 'InitialTerminationTime', '__httpdocs_oasis_open_orgwsnbr_2_CTD_ANON_2_httpdocs_oasis_open_orgwsnbr_2InitialTerminationTime', False)

    
    InitialTerminationTime = property(__InitialTerminationTime.value, __InitialTerminationTime.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        __PublisherReference.name() : __PublisherReference,
        __Demand.name() : __Demand,
        __Topic.name() : __Topic,
        __InitialTerminationTime.name() : __InitialTerminationTime
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
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type ResourceNotDestroyedFaultType with content type ELEMENT_ONLY
class ResourceNotDestroyedFaultType (pyxb.bundles.wssplat.wsrf_bf.BaseFaultType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ResourceNotDestroyedFaultType')
    # Base type is pyxb.bundles.wssplat.wsrf_bf.BaseFaultType
    
    # Element Originator ({http://docs.oasis-open.org/wsrf/bf-2}Originator) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element ErrorCode ({http://docs.oasis-open.org/wsrf/bf-2}ErrorCode) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element FaultCause ({http://docs.oasis-open.org/wsrf/bf-2}FaultCause) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Description ({http://docs.oasis-open.org/wsrf/bf-2}Description) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Timestamp ({http://docs.oasis-open.org/wsrf/bf-2}Timestamp) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2'))
    _HasWildcardElement = True

    _ElementMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'ResourceNotDestroyedFaultType', ResourceNotDestroyedFaultType)


# Complex type CTD_ANON_4 with content type ELEMENT_ONLY
class CTD_ANON_4 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/wsn/br-2}ConsumerReference uses Python identifier ConsumerReference
    __ConsumerReference = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ConsumerReference'), 'ConsumerReference', '__httpdocs_oasis_open_orgwsnbr_2_CTD_ANON_4_httpdocs_oasis_open_orgwsnbr_2ConsumerReference', False)

    
    ConsumerReference = property(__ConsumerReference.value, __ConsumerReference.set, None, None)

    
    # Element {http://docs.oasis-open.org/wsn/br-2}PublisherRegistrationReference uses Python identifier PublisherRegistrationReference
    __PublisherRegistrationReference = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PublisherRegistrationReference'), 'PublisherRegistrationReference', '__httpdocs_oasis_open_orgwsnbr_2_CTD_ANON_4_httpdocs_oasis_open_orgwsnbr_2PublisherRegistrationReference', False)

    
    PublisherRegistrationReference = property(__PublisherRegistrationReference.value, __PublisherRegistrationReference.set, None, None)


    _ElementMap = {
        __ConsumerReference.name() : __ConsumerReference,
        __PublisherRegistrationReference.name() : __PublisherRegistrationReference
    }
    _AttributeMap = {
        
    }



# Complex type PublisherRegistrationRejectedFaultType with content type ELEMENT_ONLY
class PublisherRegistrationRejectedFaultType (pyxb.bundles.wssplat.wsrf_bf.BaseFaultType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'PublisherRegistrationRejectedFaultType')
    # Base type is pyxb.bundles.wssplat.wsrf_bf.BaseFaultType
    
    # Element Originator ({http://docs.oasis-open.org/wsrf/bf-2}Originator) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element ErrorCode ({http://docs.oasis-open.org/wsrf/bf-2}ErrorCode) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element FaultCause ({http://docs.oasis-open.org/wsrf/bf-2}FaultCause) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Description ({http://docs.oasis-open.org/wsrf/bf-2}Description) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Timestamp ({http://docs.oasis-open.org/wsrf/bf-2}Timestamp) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2'))
    _HasWildcardElement = True

    _ElementMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'PublisherRegistrationRejectedFaultType', PublisherRegistrationRejectedFaultType)


# Complex type CTD_ANON_5 with content type ELEMENT_ONLY
class CTD_ANON_5 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/wsn/br-2}Topic uses Python identifier Topic
    __Topic = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Topic'), 'Topic', '__httpdocs_oasis_open_orgwsnbr_2_CTD_ANON_5_httpdocs_oasis_open_orgwsnbr_2Topic', True)

    
    Topic = property(__Topic.value, __Topic.set, None, None)

    
    # Element {http://docs.oasis-open.org/wsn/br-2}PublisherReference uses Python identifier PublisherReference
    __PublisherReference = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PublisherReference'), 'PublisherReference', '__httpdocs_oasis_open_orgwsnbr_2_CTD_ANON_5_httpdocs_oasis_open_orgwsnbr_2PublisherReference', False)

    
    PublisherReference = property(__PublisherReference.value, __PublisherReference.set, None, None)

    
    # Element {http://docs.oasis-open.org/wsn/br-2}CreationTime uses Python identifier CreationTime
    __CreationTime = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'CreationTime'), 'CreationTime', '__httpdocs_oasis_open_orgwsnbr_2_CTD_ANON_5_httpdocs_oasis_open_orgwsnbr_2CreationTime', False)

    
    CreationTime = property(__CreationTime.value, __CreationTime.set, None, None)

    
    # Element {http://docs.oasis-open.org/wsn/br-2}Demand uses Python identifier Demand
    __Demand = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Demand'), 'Demand', '__httpdocs_oasis_open_orgwsnbr_2_CTD_ANON_5_httpdocs_oasis_open_orgwsnbr_2Demand', False)

    
    Demand = property(__Demand.value, __Demand.set, None, None)


    _ElementMap = {
        __Topic.name() : __Topic,
        __PublisherReference.name() : __PublisherReference,
        __CreationTime.name() : __CreationTime,
        __Demand.name() : __Demand
    }
    _AttributeMap = {
        
    }



PublisherRegistrationFailedFault = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PublisherRegistrationFailedFault'), PublisherRegistrationFailedFaultType)
Namespace.addCategoryObject('elementBinding', PublisherRegistrationFailedFault.name().localName(), PublisherRegistrationFailedFault)

DestroyRegistration = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DestroyRegistration'), CTD_ANON)
Namespace.addCategoryObject('elementBinding', DestroyRegistration.name().localName(), DestroyRegistration)

NotificationBrokerRP = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'NotificationBrokerRP'), CTD_ANON_)
Namespace.addCategoryObject('elementBinding', NotificationBrokerRP.name().localName(), NotificationBrokerRP)

RegisterPublisher = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RegisterPublisher'), CTD_ANON_2)
Namespace.addCategoryObject('elementBinding', RegisterPublisher.name().localName(), RegisterPublisher)

DestroyRegistrationResponse = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DestroyRegistrationResponse'), CTD_ANON_3)
Namespace.addCategoryObject('elementBinding', DestroyRegistrationResponse.name().localName(), DestroyRegistrationResponse)

RequiresRegistration = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RequiresRegistration'), pyxb.binding.datatypes.boolean)
Namespace.addCategoryObject('elementBinding', RequiresRegistration.name().localName(), RequiresRegistration)

ResourceNotDestroyedFault = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ResourceNotDestroyedFault'), ResourceNotDestroyedFaultType)
Namespace.addCategoryObject('elementBinding', ResourceNotDestroyedFault.name().localName(), ResourceNotDestroyedFault)

PublisherReference = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PublisherReference'), pyxb.bundles.wssplat.wsa.EndpointReferenceType)
Namespace.addCategoryObject('elementBinding', PublisherReference.name().localName(), PublisherReference)

ConsumerReference = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ConsumerReference'), pyxb.bundles.wssplat.wsa.EndpointReferenceType)
Namespace.addCategoryObject('elementBinding', ConsumerReference.name().localName(), ConsumerReference)

Topic = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Topic'), pyxb.bundles.wssplat.wsnt.TopicExpressionType)
Namespace.addCategoryObject('elementBinding', Topic.name().localName(), Topic)

Demand = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Demand'), pyxb.binding.datatypes.boolean)
Namespace.addCategoryObject('elementBinding', Demand.name().localName(), Demand)

CreationTime = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CreationTime'), pyxb.binding.datatypes.dateTime)
Namespace.addCategoryObject('elementBinding', CreationTime.name().localName(), CreationTime)

RegisterPublisherResponse = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RegisterPublisherResponse'), CTD_ANON_4)
Namespace.addCategoryObject('elementBinding', RegisterPublisherResponse.name().localName(), RegisterPublisherResponse)

PublisherRegistrationRejectedFault = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PublisherRegistrationRejectedFault'), PublisherRegistrationRejectedFaultType)
Namespace.addCategoryObject('elementBinding', PublisherRegistrationRejectedFault.name().localName(), PublisherRegistrationRejectedFault)

PublisherRegistrationRP = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PublisherRegistrationRP'), CTD_ANON_5)
Namespace.addCategoryObject('elementBinding', PublisherRegistrationRP.name().localName(), PublisherRegistrationRP)


PublisherRegistrationFailedFaultType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(PublisherRegistrationFailedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Timestamp')), min_occurs=1L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(PublisherRegistrationFailedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Originator')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(PublisherRegistrationFailedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'ErrorCode')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(PublisherRegistrationFailedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Description')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(PublisherRegistrationFailedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'FaultCause')), min_occurs=0L, max_occurs=1L)
    )
PublisherRegistrationFailedFaultType._ContentModel = pyxb.binding.content.ParticleModel(PublisherRegistrationFailedFaultType._GroupModel_, min_occurs=1, max_occurs=1)


CTD_ANON._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsn/br-2')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON._GroupModel, min_occurs=1, max_occurs=1)



CTD_ANON_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsn/b-2'), u'TopicExpression'), pyxb.bundles.wssplat.wsnt.TopicExpressionType, scope=CTD_ANON_))

CTD_ANON_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RequiresRegistration'), pyxb.binding.datatypes.boolean, scope=CTD_ANON_))

CTD_ANON_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsn/t-1'), u'TopicSet'), pyxb.bundles.wssplat.wstop.TopicSetType, scope=CTD_ANON_))

CTD_ANON_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsn/b-2'), u'FixedTopicSet'), pyxb.binding.datatypes.boolean, scope=CTD_ANON_))

CTD_ANON_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsn/b-2'), u'TopicExpressionDialect'), pyxb.binding.datatypes.anyURI, scope=CTD_ANON_))
CTD_ANON_._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsn/b-2'), u'TopicExpression')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsn/b-2'), u'FixedTopicSet')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(CTD_ANON_._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsn/b-2'), u'TopicExpressionDialect')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsn/t-1'), u'TopicSet')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(CTD_ANON_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'RequiresRegistration')), min_occurs=1L, max_occurs=1L)
    )
CTD_ANON_._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_._GroupModel, min_occurs=1, max_occurs=1)



CTD_ANON_2._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PublisherReference'), pyxb.bundles.wssplat.wsa.EndpointReferenceType, scope=CTD_ANON_2))

CTD_ANON_2._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Demand'), pyxb.binding.datatypes.boolean, scope=CTD_ANON_2))

CTD_ANON_2._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Topic'), pyxb.bundles.wssplat.wsnt.TopicExpressionType, scope=CTD_ANON_2))

CTD_ANON_2._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'InitialTerminationTime'), pyxb.binding.datatypes.dateTime, scope=CTD_ANON_2))
CTD_ANON_2._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_2._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PublisherReference')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(CTD_ANON_2._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Topic')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_2._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Demand')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(CTD_ANON_2._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'InitialTerminationTime')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsn/br-2')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_2._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_2._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_3._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsn/br-2')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_3._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_3._GroupModel, min_occurs=1, max_occurs=1)


ResourceNotDestroyedFaultType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(ResourceNotDestroyedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Timestamp')), min_occurs=1L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(ResourceNotDestroyedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Originator')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(ResourceNotDestroyedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'ErrorCode')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(ResourceNotDestroyedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Description')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(ResourceNotDestroyedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'FaultCause')), min_occurs=0L, max_occurs=1L)
    )
ResourceNotDestroyedFaultType._ContentModel = pyxb.binding.content.ParticleModel(ResourceNotDestroyedFaultType._GroupModel_, min_occurs=1, max_occurs=1)



CTD_ANON_4._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ConsumerReference'), pyxb.bundles.wssplat.wsa.EndpointReferenceType, scope=CTD_ANON_4))

CTD_ANON_4._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PublisherRegistrationReference'), pyxb.bundles.wssplat.wsa.EndpointReferenceType, scope=CTD_ANON_4))
CTD_ANON_4._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_4._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PublisherRegistrationReference')), min_occurs=1L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(CTD_ANON_4._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ConsumerReference')), min_occurs=0L, max_occurs=1L)
    )
CTD_ANON_4._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_4._GroupModel, min_occurs=1, max_occurs=1)


PublisherRegistrationRejectedFaultType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(PublisherRegistrationRejectedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Timestamp')), min_occurs=1L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(PublisherRegistrationRejectedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Originator')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(PublisherRegistrationRejectedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'ErrorCode')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(PublisherRegistrationRejectedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Description')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(PublisherRegistrationRejectedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'FaultCause')), min_occurs=0L, max_occurs=1L)
    )
PublisherRegistrationRejectedFaultType._ContentModel = pyxb.binding.content.ParticleModel(PublisherRegistrationRejectedFaultType._GroupModel_, min_occurs=1, max_occurs=1)



CTD_ANON_5._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Topic'), pyxb.bundles.wssplat.wsnt.TopicExpressionType, scope=CTD_ANON_5))

CTD_ANON_5._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PublisherReference'), pyxb.bundles.wssplat.wsa.EndpointReferenceType, scope=CTD_ANON_5))

CTD_ANON_5._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CreationTime'), pyxb.binding.datatypes.dateTime, scope=CTD_ANON_5))

CTD_ANON_5._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Demand'), pyxb.binding.datatypes.boolean, scope=CTD_ANON_5))
CTD_ANON_5._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_5._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PublisherReference')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(CTD_ANON_5._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Topic')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_5._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Demand')), min_occurs=1L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(CTD_ANON_5._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'CreationTime')), min_occurs=0L, max_occurs=1L)
    )
CTD_ANON_5._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_5._GroupModel, min_occurs=1, max_occurs=1)

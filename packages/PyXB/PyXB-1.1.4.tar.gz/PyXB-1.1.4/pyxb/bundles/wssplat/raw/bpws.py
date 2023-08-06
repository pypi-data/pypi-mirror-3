# ./pyxb/bundles/wssplat/raw/bpws.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:157fc4d84d91f9f337276fbd45fc8a0cd667f150
# Generated 2012-06-15 14:42:54.557998 by PyXB version 1.1.4
# Namespace http://schemas.xmlsoap.org/ws/2003/03/business-process/

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:4ce138fa-b722-11e1-ab10-c8600024e903')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes

Namespace = pyxb.namespace.NamespaceForURI(u'http://schemas.xmlsoap.org/ws/2003/03/business-process/', create_if_missing=True)
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
class tBoolean_expr (pyxb.binding.datatypes.string):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tBoolean-expr')
    _Documentation = None
tBoolean_expr._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'tBoolean-expr', tBoolean_expr)

# Atomic SimpleTypeDefinition
class tBoolean (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tBoolean')
    _Documentation = None
tBoolean._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=tBoolean, enum_prefix=None)
tBoolean.yes = tBoolean._CF_enumeration.addEnumeration(unicode_value=u'yes', tag=u'yes')
tBoolean.no = tBoolean._CF_enumeration.addEnumeration(unicode_value=u'no', tag=u'no')
tBoolean._InitializeFacetMap(tBoolean._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'tBoolean', tBoolean)

# Atomic SimpleTypeDefinition
class tDeadline_expr (pyxb.binding.datatypes.string):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tDeadline-expr')
    _Documentation = None
tDeadline_expr._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'tDeadline-expr', tDeadline_expr)

# Atomic SimpleTypeDefinition
class tDuration_expr (pyxb.binding.datatypes.string):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tDuration-expr')
    _Documentation = None
tDuration_expr._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'tDuration-expr', tDuration_expr)

# Atomic SimpleTypeDefinition
class tRoles (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tRoles')
    _Documentation = None
tRoles._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=tRoles, enum_prefix=None)
tRoles.myRole = tRoles._CF_enumeration.addEnumeration(unicode_value=u'myRole', tag=u'myRole')
tRoles.partnerRole = tRoles._CF_enumeration.addEnumeration(unicode_value=u'partnerRole', tag=u'partnerRole')
tRoles._InitializeFacetMap(tRoles._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'tRoles', tRoles)

# List SimpleTypeDefinition
# superclasses pyxb.binding.datatypes.anySimpleType
class STD_ANON (pyxb.binding.basis.STD_list):

    """Simple type that is a list of pyxb.binding.datatypes.QName."""

    _ExpandedName = None
    _Documentation = None

    _ItemType = pyxb.binding.datatypes.QName
STD_ANON._InitializeFacetMap()

# Atomic SimpleTypeDefinition
class STD_ANON_ (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_, enum_prefix=None)
STD_ANON_.in_ = STD_ANON_._CF_enumeration.addEnumeration(unicode_value=u'in', tag=u'in_')
STD_ANON_.out = STD_ANON_._CF_enumeration.addEnumeration(unicode_value=u'out', tag=u'out')
STD_ANON_.out_in = STD_ANON_._CF_enumeration.addEnumeration(unicode_value=u'out-in', tag=u'out_in')
STD_ANON_._InitializeFacetMap(STD_ANON_._CF_enumeration)

# Complex type tExtensibleElements with content type ELEMENT_ONLY
class tExtensibleElements (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tExtensibleElements')
    # Base type is pyxb.binding.datatypes.anyType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'tExtensibleElements', tExtensibleElements)


# Complex type tActivity with content type ELEMENT_ONLY
class tActivity (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tActivity')
    # Base type is tExtensibleElements
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}source uses Python identifier source
    __source = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'source'), 'source', '__httpschemas_xmlsoap_orgws200303business_process_tActivity_httpschemas_xmlsoap_orgws200303business_processsource', True)

    
    source = property(__source.value, __source.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}target uses Python identifier target
    __target = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'target'), 'target', '__httpschemas_xmlsoap_orgws200303business_process_tActivity_httpschemas_xmlsoap_orgws200303business_processtarget', True)

    
    target = property(__target.value, __target.set, None, None)

    
    # Attribute suppressJoinFailure uses Python identifier suppressJoinFailure
    __suppressJoinFailure = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'suppressJoinFailure'), 'suppressJoinFailure', '__httpschemas_xmlsoap_orgws200303business_process_tActivity_suppressJoinFailure', tBoolean, unicode_default=u'no')
    
    suppressJoinFailure = property(__suppressJoinFailure.value, __suppressJoinFailure.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgws200303business_process_tActivity_name', pyxb.binding.datatypes.NCName)
    
    name = property(__name.value, __name.set, None, None)

    
    # Attribute joinCondition uses Python identifier joinCondition
    __joinCondition = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'joinCondition'), 'joinCondition', '__httpschemas_xmlsoap_orgws200303business_process_tActivity_joinCondition', tBoolean_expr)
    
    joinCondition = property(__joinCondition.value, __joinCondition.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        __source.name() : __source,
        __target.name() : __target
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        __suppressJoinFailure.name() : __suppressJoinFailure,
        __name.name() : __name,
        __joinCondition.name() : __joinCondition
    })
Namespace.addCategoryObject('typeBinding', u'tActivity', tActivity)


# Complex type tTerminate with content type ELEMENT_ONLY
class tTerminate (tActivity):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tTerminate')
    # Base type is tActivity
    
    # Element source ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}source) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Element target ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}target) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute joinCondition inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute name inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute suppressJoinFailure inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tActivity._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tActivity._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tTerminate', tTerminate)


# Complex type tEmpty with content type ELEMENT_ONLY
class tEmpty (tActivity):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tEmpty')
    # Base type is tActivity
    
    # Element source ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}source) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Element target ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}target) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute joinCondition inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute name inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute suppressJoinFailure inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tActivity._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tActivity._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tEmpty', tEmpty)


# Complex type tCorrelationsWithPattern with content type ELEMENT_ONLY
class tCorrelationsWithPattern (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tCorrelationsWithPattern')
    # Base type is tExtensibleElements
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}correlation uses Python identifier correlation
    __correlation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'correlation'), 'correlation', '__httpschemas_xmlsoap_orgws200303business_process_tCorrelationsWithPattern_httpschemas_xmlsoap_orgws200303business_processcorrelation', True)

    
    correlation = property(__correlation.value, __correlation.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        __correlation.name() : __correlation
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tCorrelationsWithPattern', tCorrelationsWithPattern)


# Complex type tReply with content type ELEMENT_ONLY
class tReply (tActivity):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tReply')
    # Base type is tActivity
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}correlations uses Python identifier correlations
    __correlations = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'correlations'), 'correlations', '__httpschemas_xmlsoap_orgws200303business_process_tReply_httpschemas_xmlsoap_orgws200303business_processcorrelations', False)

    
    correlations = property(__correlations.value, __correlations.set, None, None)

    
    # Element target ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}target) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Element source ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}source) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute variable uses Python identifier variable
    __variable = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'variable'), 'variable', '__httpschemas_xmlsoap_orgws200303business_process_tReply_variable', pyxb.binding.datatypes.NCName)
    
    variable = property(__variable.value, __variable.set, None, None)

    
    # Attribute portType uses Python identifier portType
    __portType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'portType'), 'portType', '__httpschemas_xmlsoap_orgws200303business_process_tReply_portType', pyxb.binding.datatypes.QName, required=True)
    
    portType = property(__portType.value, __portType.set, None, None)

    
    # Attribute partnerLink uses Python identifier partnerLink
    __partnerLink = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'partnerLink'), 'partnerLink', '__httpschemas_xmlsoap_orgws200303business_process_tReply_partnerLink', pyxb.binding.datatypes.NCName, required=True)
    
    partnerLink = property(__partnerLink.value, __partnerLink.set, None, None)

    
    # Attribute name inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute operation uses Python identifier operation
    __operation = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'operation'), 'operation', '__httpschemas_xmlsoap_orgws200303business_process_tReply_operation', pyxb.binding.datatypes.NCName, required=True)
    
    operation = property(__operation.value, __operation.set, None, None)

    
    # Attribute faultName uses Python identifier faultName
    __faultName = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'faultName'), 'faultName', '__httpschemas_xmlsoap_orgws200303business_process_tReply_faultName', pyxb.binding.datatypes.QName)
    
    faultName = property(__faultName.value, __faultName.set, None, None)

    
    # Attribute joinCondition inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute suppressJoinFailure inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tActivity._ElementMap.copy()
    _ElementMap.update({
        __correlations.name() : __correlations
    })
    _AttributeMap = tActivity._AttributeMap.copy()
    _AttributeMap.update({
        __variable.name() : __variable,
        __portType.name() : __portType,
        __partnerLink.name() : __partnerLink,
        __operation.name() : __operation,
        __faultName.name() : __faultName
    })
Namespace.addCategoryObject('typeBinding', u'tReply', tReply)


# Complex type tCopy with content type ELEMENT_ONLY
class tCopy (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tCopy')
    # Base type is tExtensibleElements
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}to uses Python identifier to
    __to = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'to'), 'to', '__httpschemas_xmlsoap_orgws200303business_process_tCopy_httpschemas_xmlsoap_orgws200303business_processto', False)

    
    to = property(__to.value, __to.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}from uses Python identifier from_
    __from = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'from'), 'from_', '__httpschemas_xmlsoap_orgws200303business_process_tCopy_httpschemas_xmlsoap_orgws200303business_processfrom', False)

    
    from_ = property(__from.value, __from.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        __to.name() : __to,
        __from.name() : __from
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tCopy', tCopy)


# Complex type tFlow with content type ELEMENT_ONLY
class tFlow (tActivity):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tFlow')
    # Base type is tActivity
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}terminate uses Python identifier terminate
    __terminate = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'terminate'), 'terminate', '__httpschemas_xmlsoap_orgws200303business_process_tFlow_httpschemas_xmlsoap_orgws200303business_processterminate', True)

    
    terminate = property(__terminate.value, __terminate.set, None, None)

    
    # Element source ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}source) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}while uses Python identifier while_
    __while = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'while'), 'while_', '__httpschemas_xmlsoap_orgws200303business_process_tFlow_httpschemas_xmlsoap_orgws200303business_processwhile', True)

    
    while_ = property(__while.value, __while.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}sequence uses Python identifier sequence
    __sequence = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'sequence'), 'sequence', '__httpschemas_xmlsoap_orgws200303business_process_tFlow_httpschemas_xmlsoap_orgws200303business_processsequence', True)

    
    sequence = property(__sequence.value, __sequence.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}scope uses Python identifier scope
    __scope = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'scope'), 'scope', '__httpschemas_xmlsoap_orgws200303business_process_tFlow_httpschemas_xmlsoap_orgws200303business_processscope', True)

    
    scope = property(__scope.value, __scope.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}pick uses Python identifier pick
    __pick = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'pick'), 'pick', '__httpschemas_xmlsoap_orgws200303business_process_tFlow_httpschemas_xmlsoap_orgws200303business_processpick', True)

    
    pick = property(__pick.value, __pick.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}flow uses Python identifier flow
    __flow = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'flow'), 'flow', '__httpschemas_xmlsoap_orgws200303business_process_tFlow_httpschemas_xmlsoap_orgws200303business_processflow', True)

    
    flow = property(__flow.value, __flow.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}invoke uses Python identifier invoke
    __invoke = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'invoke'), 'invoke', '__httpschemas_xmlsoap_orgws200303business_process_tFlow_httpschemas_xmlsoap_orgws200303business_processinvoke', True)

    
    invoke = property(__invoke.value, __invoke.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}empty uses Python identifier empty
    __empty = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'empty'), 'empty', '__httpschemas_xmlsoap_orgws200303business_process_tFlow_httpschemas_xmlsoap_orgws200303business_processempty', True)

    
    empty = property(__empty.value, __empty.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}reply uses Python identifier reply
    __reply = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'reply'), 'reply', '__httpschemas_xmlsoap_orgws200303business_process_tFlow_httpschemas_xmlsoap_orgws200303business_processreply', True)

    
    reply = property(__reply.value, __reply.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}throw uses Python identifier throw
    __throw = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'throw'), 'throw', '__httpschemas_xmlsoap_orgws200303business_process_tFlow_httpschemas_xmlsoap_orgws200303business_processthrow', True)

    
    throw = property(__throw.value, __throw.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}wait uses Python identifier wait
    __wait = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'wait'), 'wait', '__httpschemas_xmlsoap_orgws200303business_process_tFlow_httpschemas_xmlsoap_orgws200303business_processwait', True)

    
    wait = property(__wait.value, __wait.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}links uses Python identifier links
    __links = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'links'), 'links', '__httpschemas_xmlsoap_orgws200303business_process_tFlow_httpschemas_xmlsoap_orgws200303business_processlinks', False)

    
    links = property(__links.value, __links.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}assign uses Python identifier assign
    __assign = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'assign'), 'assign', '__httpschemas_xmlsoap_orgws200303business_process_tFlow_httpschemas_xmlsoap_orgws200303business_processassign', True)

    
    assign = property(__assign.value, __assign.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}switch uses Python identifier switch
    __switch = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'switch'), 'switch', '__httpschemas_xmlsoap_orgws200303business_process_tFlow_httpschemas_xmlsoap_orgws200303business_processswitch', True)

    
    switch = property(__switch.value, __switch.set, None, None)

    
    # Element target ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}target) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}receive uses Python identifier receive
    __receive = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'receive'), 'receive', '__httpschemas_xmlsoap_orgws200303business_process_tFlow_httpschemas_xmlsoap_orgws200303business_processreceive', True)

    
    receive = property(__receive.value, __receive.set, None, None)

    
    # Attribute joinCondition inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute name inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute suppressJoinFailure inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tActivity._ElementMap.copy()
    _ElementMap.update({
        __terminate.name() : __terminate,
        __while.name() : __while,
        __sequence.name() : __sequence,
        __scope.name() : __scope,
        __pick.name() : __pick,
        __flow.name() : __flow,
        __invoke.name() : __invoke,
        __empty.name() : __empty,
        __reply.name() : __reply,
        __throw.name() : __throw,
        __wait.name() : __wait,
        __links.name() : __links,
        __assign.name() : __assign,
        __switch.name() : __switch,
        __receive.name() : __receive
    })
    _AttributeMap = tActivity._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tFlow', tFlow)


# Complex type tActivityContainer with content type ELEMENT_ONLY
class tActivityContainer (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tActivityContainer')
    # Base type is tExtensibleElements
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}empty uses Python identifier empty
    __empty = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'empty'), 'empty', '__httpschemas_xmlsoap_orgws200303business_process_tActivityContainer_httpschemas_xmlsoap_orgws200303business_processempty', False)

    
    empty = property(__empty.value, __empty.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}invoke uses Python identifier invoke
    __invoke = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'invoke'), 'invoke', '__httpschemas_xmlsoap_orgws200303business_process_tActivityContainer_httpschemas_xmlsoap_orgws200303business_processinvoke', False)

    
    invoke = property(__invoke.value, __invoke.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}terminate uses Python identifier terminate
    __terminate = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'terminate'), 'terminate', '__httpschemas_xmlsoap_orgws200303business_process_tActivityContainer_httpschemas_xmlsoap_orgws200303business_processterminate', False)

    
    terminate = property(__terminate.value, __terminate.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}assign uses Python identifier assign
    __assign = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'assign'), 'assign', '__httpschemas_xmlsoap_orgws200303business_process_tActivityContainer_httpschemas_xmlsoap_orgws200303business_processassign', False)

    
    assign = property(__assign.value, __assign.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}pick uses Python identifier pick
    __pick = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'pick'), 'pick', '__httpschemas_xmlsoap_orgws200303business_process_tActivityContainer_httpschemas_xmlsoap_orgws200303business_processpick', False)

    
    pick = property(__pick.value, __pick.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}while uses Python identifier while_
    __while = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'while'), 'while_', '__httpschemas_xmlsoap_orgws200303business_process_tActivityContainer_httpschemas_xmlsoap_orgws200303business_processwhile', False)

    
    while_ = property(__while.value, __while.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}flow uses Python identifier flow
    __flow = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'flow'), 'flow', '__httpschemas_xmlsoap_orgws200303business_process_tActivityContainer_httpschemas_xmlsoap_orgws200303business_processflow', False)

    
    flow = property(__flow.value, __flow.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}receive uses Python identifier receive
    __receive = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'receive'), 'receive', '__httpschemas_xmlsoap_orgws200303business_process_tActivityContainer_httpschemas_xmlsoap_orgws200303business_processreceive', False)

    
    receive = property(__receive.value, __receive.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}wait uses Python identifier wait
    __wait = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'wait'), 'wait', '__httpschemas_xmlsoap_orgws200303business_process_tActivityContainer_httpschemas_xmlsoap_orgws200303business_processwait', False)

    
    wait = property(__wait.value, __wait.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}switch uses Python identifier switch
    __switch = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'switch'), 'switch', '__httpschemas_xmlsoap_orgws200303business_process_tActivityContainer_httpschemas_xmlsoap_orgws200303business_processswitch', False)

    
    switch = property(__switch.value, __switch.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}scope uses Python identifier scope
    __scope = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'scope'), 'scope', '__httpschemas_xmlsoap_orgws200303business_process_tActivityContainer_httpschemas_xmlsoap_orgws200303business_processscope', False)

    
    scope = property(__scope.value, __scope.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}reply uses Python identifier reply
    __reply = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'reply'), 'reply', '__httpschemas_xmlsoap_orgws200303business_process_tActivityContainer_httpschemas_xmlsoap_orgws200303business_processreply', False)

    
    reply = property(__reply.value, __reply.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}sequence uses Python identifier sequence
    __sequence = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'sequence'), 'sequence', '__httpschemas_xmlsoap_orgws200303business_process_tActivityContainer_httpschemas_xmlsoap_orgws200303business_processsequence', False)

    
    sequence = property(__sequence.value, __sequence.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}throw uses Python identifier throw
    __throw = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'throw'), 'throw', '__httpschemas_xmlsoap_orgws200303business_process_tActivityContainer_httpschemas_xmlsoap_orgws200303business_processthrow', False)

    
    throw = property(__throw.value, __throw.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        __empty.name() : __empty,
        __invoke.name() : __invoke,
        __terminate.name() : __terminate,
        __assign.name() : __assign,
        __pick.name() : __pick,
        __while.name() : __while,
        __flow.name() : __flow,
        __receive.name() : __receive,
        __wait.name() : __wait,
        __switch.name() : __switch,
        __scope.name() : __scope,
        __reply.name() : __reply,
        __sequence.name() : __sequence,
        __throw.name() : __throw
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tActivityContainer', tActivityContainer)


# Complex type tOnAlarm with content type ELEMENT_ONLY
class tOnAlarm (tActivityContainer):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tOnAlarm')
    # Base type is tActivityContainer
    
    # Element empty ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}empty) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element invoke ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}invoke) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element terminate ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}terminate) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element assign ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}assign) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element pick ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}pick) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element while_ ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}while) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element flow ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}flow) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element receive ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}receive) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element wait ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}wait) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element switch ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}switch) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element scope ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}scope) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element reply ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}reply) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element sequence ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}sequence) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element throw ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}throw) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Attribute until uses Python identifier until
    __until = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'until'), 'until', '__httpschemas_xmlsoap_orgws200303business_process_tOnAlarm_until', tDeadline_expr)
    
    until = property(__until.value, __until.set, None, None)

    
    # Attribute for uses Python identifier for_
    __for = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'for'), 'for_', '__httpschemas_xmlsoap_orgws200303business_process_tOnAlarm_for', tDuration_expr)
    
    for_ = property(__for.value, __for.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tActivityContainer._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tActivityContainer._AttributeMap.copy()
    _AttributeMap.update({
        __until.name() : __until,
        __for.name() : __for
    })
Namespace.addCategoryObject('typeBinding', u'tOnAlarm', tOnAlarm)


# Complex type tScope with content type ELEMENT_ONLY
class tScope (tActivity):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tScope')
    # Base type is tActivity
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}scope uses Python identifier scope
    __scope = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'scope'), 'scope', '__httpschemas_xmlsoap_orgws200303business_process_tScope_httpschemas_xmlsoap_orgws200303business_processscope', False)

    
    scope = property(__scope.value, __scope.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}faultHandlers uses Python identifier faultHandlers
    __faultHandlers = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'faultHandlers'), 'faultHandlers', '__httpschemas_xmlsoap_orgws200303business_process_tScope_httpschemas_xmlsoap_orgws200303business_processfaultHandlers', False)

    
    faultHandlers = property(__faultHandlers.value, __faultHandlers.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}sequence uses Python identifier sequence
    __sequence = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'sequence'), 'sequence', '__httpschemas_xmlsoap_orgws200303business_process_tScope_httpschemas_xmlsoap_orgws200303business_processsequence', False)

    
    sequence = property(__sequence.value, __sequence.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}empty uses Python identifier empty
    __empty = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'empty'), 'empty', '__httpschemas_xmlsoap_orgws200303business_process_tScope_httpschemas_xmlsoap_orgws200303business_processempty', False)

    
    empty = property(__empty.value, __empty.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}eventHandlers uses Python identifier eventHandlers
    __eventHandlers = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'eventHandlers'), 'eventHandlers', '__httpschemas_xmlsoap_orgws200303business_process_tScope_httpschemas_xmlsoap_orgws200303business_processeventHandlers', False)

    
    eventHandlers = property(__eventHandlers.value, __eventHandlers.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}compensationHandler uses Python identifier compensationHandler
    __compensationHandler = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'compensationHandler'), 'compensationHandler', '__httpschemas_xmlsoap_orgws200303business_process_tScope_httpschemas_xmlsoap_orgws200303business_processcompensationHandler', False)

    
    compensationHandler = property(__compensationHandler.value, __compensationHandler.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}pick uses Python identifier pick
    __pick = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'pick'), 'pick', '__httpschemas_xmlsoap_orgws200303business_process_tScope_httpschemas_xmlsoap_orgws200303business_processpick', False)

    
    pick = property(__pick.value, __pick.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}reply uses Python identifier reply
    __reply = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'reply'), 'reply', '__httpschemas_xmlsoap_orgws200303business_process_tScope_httpschemas_xmlsoap_orgws200303business_processreply', False)

    
    reply = property(__reply.value, __reply.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}terminate uses Python identifier terminate
    __terminate = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'terminate'), 'terminate', '__httpschemas_xmlsoap_orgws200303business_process_tScope_httpschemas_xmlsoap_orgws200303business_processterminate', False)

    
    terminate = property(__terminate.value, __terminate.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}throw uses Python identifier throw
    __throw = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'throw'), 'throw', '__httpschemas_xmlsoap_orgws200303business_process_tScope_httpschemas_xmlsoap_orgws200303business_processthrow', False)

    
    throw = property(__throw.value, __throw.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}variables uses Python identifier variables
    __variables = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'variables'), 'variables', '__httpschemas_xmlsoap_orgws200303business_process_tScope_httpschemas_xmlsoap_orgws200303business_processvariables', False)

    
    variables = property(__variables.value, __variables.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}assign uses Python identifier assign
    __assign = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'assign'), 'assign', '__httpschemas_xmlsoap_orgws200303business_process_tScope_httpschemas_xmlsoap_orgws200303business_processassign', False)

    
    assign = property(__assign.value, __assign.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}switch uses Python identifier switch
    __switch = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'switch'), 'switch', '__httpschemas_xmlsoap_orgws200303business_process_tScope_httpschemas_xmlsoap_orgws200303business_processswitch', False)

    
    switch = property(__switch.value, __switch.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}flow uses Python identifier flow
    __flow = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'flow'), 'flow', '__httpschemas_xmlsoap_orgws200303business_process_tScope_httpschemas_xmlsoap_orgws200303business_processflow', False)

    
    flow = property(__flow.value, __flow.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}correlationSets uses Python identifier correlationSets
    __correlationSets = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'correlationSets'), 'correlationSets', '__httpschemas_xmlsoap_orgws200303business_process_tScope_httpschemas_xmlsoap_orgws200303business_processcorrelationSets', False)

    
    correlationSets = property(__correlationSets.value, __correlationSets.set, None, None)

    
    # Element source ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}source) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}while uses Python identifier while_
    __while = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'while'), 'while_', '__httpschemas_xmlsoap_orgws200303business_process_tScope_httpschemas_xmlsoap_orgws200303business_processwhile', False)

    
    while_ = property(__while.value, __while.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}invoke uses Python identifier invoke
    __invoke = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'invoke'), 'invoke', '__httpschemas_xmlsoap_orgws200303business_process_tScope_httpschemas_xmlsoap_orgws200303business_processinvoke', False)

    
    invoke = property(__invoke.value, __invoke.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}receive uses Python identifier receive
    __receive = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'receive'), 'receive', '__httpschemas_xmlsoap_orgws200303business_process_tScope_httpschemas_xmlsoap_orgws200303business_processreceive', False)

    
    receive = property(__receive.value, __receive.set, None, None)

    
    # Element target ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}target) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}wait uses Python identifier wait
    __wait = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'wait'), 'wait', '__httpschemas_xmlsoap_orgws200303business_process_tScope_httpschemas_xmlsoap_orgws200303business_processwait', False)

    
    wait = property(__wait.value, __wait.set, None, None)

    
    # Attribute suppressJoinFailure inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute name inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute variableAccessSerializable uses Python identifier variableAccessSerializable
    __variableAccessSerializable = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'variableAccessSerializable'), 'variableAccessSerializable', '__httpschemas_xmlsoap_orgws200303business_process_tScope_variableAccessSerializable', tBoolean, unicode_default=u'no')
    
    variableAccessSerializable = property(__variableAccessSerializable.value, __variableAccessSerializable.set, None, None)

    
    # Attribute joinCondition inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tActivity._ElementMap.copy()
    _ElementMap.update({
        __scope.name() : __scope,
        __faultHandlers.name() : __faultHandlers,
        __sequence.name() : __sequence,
        __empty.name() : __empty,
        __eventHandlers.name() : __eventHandlers,
        __compensationHandler.name() : __compensationHandler,
        __pick.name() : __pick,
        __reply.name() : __reply,
        __terminate.name() : __terminate,
        __throw.name() : __throw,
        __variables.name() : __variables,
        __assign.name() : __assign,
        __switch.name() : __switch,
        __flow.name() : __flow,
        __correlationSets.name() : __correlationSets,
        __while.name() : __while,
        __invoke.name() : __invoke,
        __receive.name() : __receive,
        __wait.name() : __wait
    })
    _AttributeMap = tActivity._AttributeMap.copy()
    _AttributeMap.update({
        __variableAccessSerializable.name() : __variableAccessSerializable
    })
Namespace.addCategoryObject('typeBinding', u'tScope', tScope)


# Complex type tAssign with content type ELEMENT_ONLY
class tAssign (tActivity):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tAssign')
    # Base type is tActivity
    
    # Element source ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}source) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}copy uses Python identifier copy
    __copy = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'copy'), 'copy', '__httpschemas_xmlsoap_orgws200303business_process_tAssign_httpschemas_xmlsoap_orgws200303business_processcopy', True)

    
    copy = property(__copy.value, __copy.set, None, None)

    
    # Element target ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}target) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute joinCondition inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute name inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute suppressJoinFailure inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tActivity._ElementMap.copy()
    _ElementMap.update({
        __copy.name() : __copy
    })
    _AttributeMap = tActivity._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tAssign', tAssign)


# Complex type tWhile with content type ELEMENT_ONLY
class tWhile (tActivity):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tWhile')
    # Base type is tActivity
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}assign uses Python identifier assign
    __assign = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'assign'), 'assign', '__httpschemas_xmlsoap_orgws200303business_process_tWhile_httpschemas_xmlsoap_orgws200303business_processassign', False)

    
    assign = property(__assign.value, __assign.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}pick uses Python identifier pick
    __pick = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'pick'), 'pick', '__httpschemas_xmlsoap_orgws200303business_process_tWhile_httpschemas_xmlsoap_orgws200303business_processpick', False)

    
    pick = property(__pick.value, __pick.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}terminate uses Python identifier terminate
    __terminate = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'terminate'), 'terminate', '__httpschemas_xmlsoap_orgws200303business_process_tWhile_httpschemas_xmlsoap_orgws200303business_processterminate', False)

    
    terminate = property(__terminate.value, __terminate.set, None, None)

    
    # Element target ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}target) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}receive uses Python identifier receive
    __receive = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'receive'), 'receive', '__httpschemas_xmlsoap_orgws200303business_process_tWhile_httpschemas_xmlsoap_orgws200303business_processreceive', False)

    
    receive = property(__receive.value, __receive.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}flow uses Python identifier flow
    __flow = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'flow'), 'flow', '__httpschemas_xmlsoap_orgws200303business_process_tWhile_httpschemas_xmlsoap_orgws200303business_processflow', False)

    
    flow = property(__flow.value, __flow.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}scope uses Python identifier scope
    __scope = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'scope'), 'scope', '__httpschemas_xmlsoap_orgws200303business_process_tWhile_httpschemas_xmlsoap_orgws200303business_processscope', False)

    
    scope = property(__scope.value, __scope.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}wait uses Python identifier wait
    __wait = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'wait'), 'wait', '__httpschemas_xmlsoap_orgws200303business_process_tWhile_httpschemas_xmlsoap_orgws200303business_processwait', False)

    
    wait = property(__wait.value, __wait.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}switch uses Python identifier switch
    __switch = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'switch'), 'switch', '__httpschemas_xmlsoap_orgws200303business_process_tWhile_httpschemas_xmlsoap_orgws200303business_processswitch', False)

    
    switch = property(__switch.value, __switch.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}empty uses Python identifier empty
    __empty = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'empty'), 'empty', '__httpschemas_xmlsoap_orgws200303business_process_tWhile_httpschemas_xmlsoap_orgws200303business_processempty', False)

    
    empty = property(__empty.value, __empty.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}reply uses Python identifier reply
    __reply = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'reply'), 'reply', '__httpschemas_xmlsoap_orgws200303business_process_tWhile_httpschemas_xmlsoap_orgws200303business_processreply', False)

    
    reply = property(__reply.value, __reply.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}throw uses Python identifier throw
    __throw = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'throw'), 'throw', '__httpschemas_xmlsoap_orgws200303business_process_tWhile_httpschemas_xmlsoap_orgws200303business_processthrow', False)

    
    throw = property(__throw.value, __throw.set, None, None)

    
    # Element source ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}source) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}while uses Python identifier while_
    __while = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'while'), 'while_', '__httpschemas_xmlsoap_orgws200303business_process_tWhile_httpschemas_xmlsoap_orgws200303business_processwhile', False)

    
    while_ = property(__while.value, __while.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}invoke uses Python identifier invoke
    __invoke = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'invoke'), 'invoke', '__httpschemas_xmlsoap_orgws200303business_process_tWhile_httpschemas_xmlsoap_orgws200303business_processinvoke', False)

    
    invoke = property(__invoke.value, __invoke.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}sequence uses Python identifier sequence
    __sequence = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'sequence'), 'sequence', '__httpschemas_xmlsoap_orgws200303business_process_tWhile_httpschemas_xmlsoap_orgws200303business_processsequence', False)

    
    sequence = property(__sequence.value, __sequence.set, None, None)

    
    # Attribute suppressJoinFailure inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute condition uses Python identifier condition
    __condition = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'condition'), 'condition', '__httpschemas_xmlsoap_orgws200303business_process_tWhile_condition', tBoolean_expr, required=True)
    
    condition = property(__condition.value, __condition.set, None, None)

    
    # Attribute name inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute joinCondition inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tActivity._ElementMap.copy()
    _ElementMap.update({
        __assign.name() : __assign,
        __pick.name() : __pick,
        __terminate.name() : __terminate,
        __receive.name() : __receive,
        __flow.name() : __flow,
        __scope.name() : __scope,
        __wait.name() : __wait,
        __switch.name() : __switch,
        __empty.name() : __empty,
        __reply.name() : __reply,
        __throw.name() : __throw,
        __while.name() : __while,
        __invoke.name() : __invoke,
        __sequence.name() : __sequence
    })
    _AttributeMap = tActivity._AttributeMap.copy()
    _AttributeMap.update({
        __condition.name() : __condition
    })
Namespace.addCategoryObject('typeBinding', u'tWhile', tWhile)


# Complex type tSwitch with content type ELEMENT_ONLY
class tSwitch (tActivity):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tSwitch')
    # Base type is tActivity
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}case uses Python identifier case
    __case = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'case'), 'case', '__httpschemas_xmlsoap_orgws200303business_process_tSwitch_httpschemas_xmlsoap_orgws200303business_processcase', True)

    
    case = property(__case.value, __case.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}otherwise uses Python identifier otherwise
    __otherwise = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'otherwise'), 'otherwise', '__httpschemas_xmlsoap_orgws200303business_process_tSwitch_httpschemas_xmlsoap_orgws200303business_processotherwise', False)

    
    otherwise = property(__otherwise.value, __otherwise.set, None, None)

    
    # Element target ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}target) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Element source ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}source) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute joinCondition inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute name inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute suppressJoinFailure inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tActivity._ElementMap.copy()
    _ElementMap.update({
        __case.name() : __case,
        __otherwise.name() : __otherwise
    })
    _AttributeMap = tActivity._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tSwitch', tSwitch)


# Complex type tThrow with content type ELEMENT_ONLY
class tThrow (tActivity):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tThrow')
    # Base type is tActivity
    
    # Element source ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}source) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Element target ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}target) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute suppressJoinFailure inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute joinCondition inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute name inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute faultVariable uses Python identifier faultVariable
    __faultVariable = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'faultVariable'), 'faultVariable', '__httpschemas_xmlsoap_orgws200303business_process_tThrow_faultVariable', pyxb.binding.datatypes.NCName)
    
    faultVariable = property(__faultVariable.value, __faultVariable.set, None, None)

    
    # Attribute faultName uses Python identifier faultName
    __faultName = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'faultName'), 'faultName', '__httpschemas_xmlsoap_orgws200303business_process_tThrow_faultName', pyxb.binding.datatypes.QName, required=True)
    
    faultName = property(__faultName.value, __faultName.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tActivity._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tActivity._AttributeMap.copy()
    _AttributeMap.update({
        __faultVariable.name() : __faultVariable,
        __faultName.name() : __faultName
    })
Namespace.addCategoryObject('typeBinding', u'tThrow', tThrow)


# Complex type tActivityOrCompensateContainer with content type ELEMENT_ONLY
class tActivityOrCompensateContainer (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tActivityOrCompensateContainer')
    # Base type is tExtensibleElements
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}assign uses Python identifier assign
    __assign = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'assign'), 'assign', '__httpschemas_xmlsoap_orgws200303business_process_tActivityOrCompensateContainer_httpschemas_xmlsoap_orgws200303business_processassign', False)

    
    assign = property(__assign.value, __assign.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}terminate uses Python identifier terminate
    __terminate = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'terminate'), 'terminate', '__httpschemas_xmlsoap_orgws200303business_process_tActivityOrCompensateContainer_httpschemas_xmlsoap_orgws200303business_processterminate', False)

    
    terminate = property(__terminate.value, __terminate.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}flow uses Python identifier flow
    __flow = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'flow'), 'flow', '__httpschemas_xmlsoap_orgws200303business_process_tActivityOrCompensateContainer_httpschemas_xmlsoap_orgws200303business_processflow', False)

    
    flow = property(__flow.value, __flow.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}receive uses Python identifier receive
    __receive = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'receive'), 'receive', '__httpschemas_xmlsoap_orgws200303business_process_tActivityOrCompensateContainer_httpschemas_xmlsoap_orgws200303business_processreceive', False)

    
    receive = property(__receive.value, __receive.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}while uses Python identifier while_
    __while = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'while'), 'while_', '__httpschemas_xmlsoap_orgws200303business_process_tActivityOrCompensateContainer_httpschemas_xmlsoap_orgws200303business_processwhile', False)

    
    while_ = property(__while.value, __while.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}wait uses Python identifier wait
    __wait = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'wait'), 'wait', '__httpschemas_xmlsoap_orgws200303business_process_tActivityOrCompensateContainer_httpschemas_xmlsoap_orgws200303business_processwait', False)

    
    wait = property(__wait.value, __wait.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}switch uses Python identifier switch
    __switch = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'switch'), 'switch', '__httpschemas_xmlsoap_orgws200303business_process_tActivityOrCompensateContainer_httpschemas_xmlsoap_orgws200303business_processswitch', False)

    
    switch = property(__switch.value, __switch.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}scope uses Python identifier scope
    __scope = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'scope'), 'scope', '__httpschemas_xmlsoap_orgws200303business_process_tActivityOrCompensateContainer_httpschemas_xmlsoap_orgws200303business_processscope', False)

    
    scope = property(__scope.value, __scope.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}empty uses Python identifier empty
    __empty = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'empty'), 'empty', '__httpschemas_xmlsoap_orgws200303business_process_tActivityOrCompensateContainer_httpschemas_xmlsoap_orgws200303business_processempty', False)

    
    empty = property(__empty.value, __empty.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}reply uses Python identifier reply
    __reply = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'reply'), 'reply', '__httpschemas_xmlsoap_orgws200303business_process_tActivityOrCompensateContainer_httpschemas_xmlsoap_orgws200303business_processreply', False)

    
    reply = property(__reply.value, __reply.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}compensate uses Python identifier compensate
    __compensate = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'compensate'), 'compensate', '__httpschemas_xmlsoap_orgws200303business_process_tActivityOrCompensateContainer_httpschemas_xmlsoap_orgws200303business_processcompensate', False)

    
    compensate = property(__compensate.value, __compensate.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}sequence uses Python identifier sequence
    __sequence = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'sequence'), 'sequence', '__httpschemas_xmlsoap_orgws200303business_process_tActivityOrCompensateContainer_httpschemas_xmlsoap_orgws200303business_processsequence', False)

    
    sequence = property(__sequence.value, __sequence.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}throw uses Python identifier throw
    __throw = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'throw'), 'throw', '__httpschemas_xmlsoap_orgws200303business_process_tActivityOrCompensateContainer_httpschemas_xmlsoap_orgws200303business_processthrow', False)

    
    throw = property(__throw.value, __throw.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}invoke uses Python identifier invoke
    __invoke = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'invoke'), 'invoke', '__httpschemas_xmlsoap_orgws200303business_process_tActivityOrCompensateContainer_httpschemas_xmlsoap_orgws200303business_processinvoke', False)

    
    invoke = property(__invoke.value, __invoke.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}pick uses Python identifier pick
    __pick = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'pick'), 'pick', '__httpschemas_xmlsoap_orgws200303business_process_tActivityOrCompensateContainer_httpschemas_xmlsoap_orgws200303business_processpick', False)

    
    pick = property(__pick.value, __pick.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        __assign.name() : __assign,
        __terminate.name() : __terminate,
        __flow.name() : __flow,
        __receive.name() : __receive,
        __while.name() : __while,
        __wait.name() : __wait,
        __switch.name() : __switch,
        __scope.name() : __scope,
        __empty.name() : __empty,
        __reply.name() : __reply,
        __compensate.name() : __compensate,
        __sequence.name() : __sequence,
        __throw.name() : __throw,
        __invoke.name() : __invoke,
        __pick.name() : __pick
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tActivityOrCompensateContainer', tActivityOrCompensateContainer)


# Complex type tCompensationHandler with content type ELEMENT_ONLY
class tCompensationHandler (tActivityOrCompensateContainer):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tCompensationHandler')
    # Base type is tActivityOrCompensateContainer
    
    # Element assign ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}assign) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element terminate ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}terminate) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element flow ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}flow) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element receive ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}receive) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element while_ ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}while) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element wait ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}wait) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element switch ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}switch) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element scope ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}scope) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element empty ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}empty) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element reply ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}reply) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element compensate ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}compensate) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element sequence ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}sequence) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element throw ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}throw) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element invoke ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}invoke) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element pick ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}pick) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tActivityOrCompensateContainer._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tActivityOrCompensateContainer._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tCompensationHandler', tCompensationHandler)


# Complex type tPick with content type ELEMENT_ONLY
class tPick (tActivity):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tPick')
    # Base type is tActivity
    
    # Element source ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}source) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}onMessage uses Python identifier onMessage
    __onMessage = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'onMessage'), 'onMessage', '__httpschemas_xmlsoap_orgws200303business_process_tPick_httpschemas_xmlsoap_orgws200303business_processonMessage', True)

    
    onMessage = property(__onMessage.value, __onMessage.set, None, None)

    
    # Element target ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}target) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}onAlarm uses Python identifier onAlarm
    __onAlarm = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'onAlarm'), 'onAlarm', '__httpschemas_xmlsoap_orgws200303business_process_tPick_httpschemas_xmlsoap_orgws200303business_processonAlarm', True)

    
    onAlarm = property(__onAlarm.value, __onAlarm.set, None, None)

    
    # Attribute suppressJoinFailure inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute createInstance uses Python identifier createInstance
    __createInstance = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'createInstance'), 'createInstance', '__httpschemas_xmlsoap_orgws200303business_process_tPick_createInstance', tBoolean, unicode_default=u'no')
    
    createInstance = property(__createInstance.value, __createInstance.set, None, None)

    
    # Attribute name inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute joinCondition inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tActivity._ElementMap.copy()
    _ElementMap.update({
        __onMessage.name() : __onMessage,
        __onAlarm.name() : __onAlarm
    })
    _AttributeMap = tActivity._AttributeMap.copy()
    _AttributeMap.update({
        __createInstance.name() : __createInstance
    })
Namespace.addCategoryObject('typeBinding', u'tPick', tPick)


# Complex type tSequence with content type ELEMENT_ONLY
class tSequence (tActivity):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tSequence')
    # Base type is tActivity
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}terminate uses Python identifier terminate
    __terminate = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'terminate'), 'terminate', '__httpschemas_xmlsoap_orgws200303business_process_tSequence_httpschemas_xmlsoap_orgws200303business_processterminate', True)

    
    terminate = property(__terminate.value, __terminate.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}while uses Python identifier while_
    __while = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'while'), 'while_', '__httpschemas_xmlsoap_orgws200303business_process_tSequence_httpschemas_xmlsoap_orgws200303business_processwhile', True)

    
    while_ = property(__while.value, __while.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}reply uses Python identifier reply
    __reply = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'reply'), 'reply', '__httpschemas_xmlsoap_orgws200303business_process_tSequence_httpschemas_xmlsoap_orgws200303business_processreply', True)

    
    reply = property(__reply.value, __reply.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}wait uses Python identifier wait
    __wait = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'wait'), 'wait', '__httpschemas_xmlsoap_orgws200303business_process_tSequence_httpschemas_xmlsoap_orgws200303business_processwait', True)

    
    wait = property(__wait.value, __wait.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}empty uses Python identifier empty
    __empty = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'empty'), 'empty', '__httpschemas_xmlsoap_orgws200303business_process_tSequence_httpschemas_xmlsoap_orgws200303business_processempty', True)

    
    empty = property(__empty.value, __empty.set, None, None)

    
    # Element source ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}source) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}scope uses Python identifier scope
    __scope = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'scope'), 'scope', '__httpschemas_xmlsoap_orgws200303business_process_tSequence_httpschemas_xmlsoap_orgws200303business_processscope', True)

    
    scope = property(__scope.value, __scope.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}sequence uses Python identifier sequence
    __sequence = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'sequence'), 'sequence', '__httpschemas_xmlsoap_orgws200303business_process_tSequence_httpschemas_xmlsoap_orgws200303business_processsequence', True)

    
    sequence = property(__sequence.value, __sequence.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}throw uses Python identifier throw
    __throw = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'throw'), 'throw', '__httpschemas_xmlsoap_orgws200303business_process_tSequence_httpschemas_xmlsoap_orgws200303business_processthrow', True)

    
    throw = property(__throw.value, __throw.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}invoke uses Python identifier invoke
    __invoke = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'invoke'), 'invoke', '__httpschemas_xmlsoap_orgws200303business_process_tSequence_httpschemas_xmlsoap_orgws200303business_processinvoke', True)

    
    invoke = property(__invoke.value, __invoke.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}assign uses Python identifier assign
    __assign = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'assign'), 'assign', '__httpschemas_xmlsoap_orgws200303business_process_tSequence_httpschemas_xmlsoap_orgws200303business_processassign', True)

    
    assign = property(__assign.value, __assign.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}switch uses Python identifier switch
    __switch = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'switch'), 'switch', '__httpschemas_xmlsoap_orgws200303business_process_tSequence_httpschemas_xmlsoap_orgws200303business_processswitch', True)

    
    switch = property(__switch.value, __switch.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}flow uses Python identifier flow
    __flow = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'flow'), 'flow', '__httpschemas_xmlsoap_orgws200303business_process_tSequence_httpschemas_xmlsoap_orgws200303business_processflow', True)

    
    flow = property(__flow.value, __flow.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}pick uses Python identifier pick
    __pick = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'pick'), 'pick', '__httpschemas_xmlsoap_orgws200303business_process_tSequence_httpschemas_xmlsoap_orgws200303business_processpick', True)

    
    pick = property(__pick.value, __pick.set, None, None)

    
    # Element target ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}target) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}receive uses Python identifier receive
    __receive = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'receive'), 'receive', '__httpschemas_xmlsoap_orgws200303business_process_tSequence_httpschemas_xmlsoap_orgws200303business_processreceive', True)

    
    receive = property(__receive.value, __receive.set, None, None)

    
    # Attribute joinCondition inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute name inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute suppressJoinFailure inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tActivity._ElementMap.copy()
    _ElementMap.update({
        __terminate.name() : __terminate,
        __while.name() : __while,
        __reply.name() : __reply,
        __wait.name() : __wait,
        __empty.name() : __empty,
        __scope.name() : __scope,
        __sequence.name() : __sequence,
        __throw.name() : __throw,
        __invoke.name() : __invoke,
        __assign.name() : __assign,
        __switch.name() : __switch,
        __flow.name() : __flow,
        __pick.name() : __pick,
        __receive.name() : __receive
    })
    _AttributeMap = tActivity._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tSequence', tSequence)


# Complex type tCorrelationSets with content type ELEMENT_ONLY
class tCorrelationSets (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tCorrelationSets')
    # Base type is tExtensibleElements
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}correlationSet uses Python identifier correlationSet
    __correlationSet = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'correlationSet'), 'correlationSet', '__httpschemas_xmlsoap_orgws200303business_process_tCorrelationSets_httpschemas_xmlsoap_orgws200303business_processcorrelationSet', True)

    
    correlationSet = property(__correlationSet.value, __correlationSet.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        __correlationSet.name() : __correlationSet
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tCorrelationSets', tCorrelationSets)


# Complex type tFaultHandlers with content type ELEMENT_ONLY
class tFaultHandlers (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tFaultHandlers')
    # Base type is tExtensibleElements
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}catchAll uses Python identifier catchAll
    __catchAll = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'catchAll'), 'catchAll', '__httpschemas_xmlsoap_orgws200303business_process_tFaultHandlers_httpschemas_xmlsoap_orgws200303business_processcatchAll', False)

    
    catchAll = property(__catchAll.value, __catchAll.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}catch uses Python identifier catch
    __catch = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'catch'), 'catch', '__httpschemas_xmlsoap_orgws200303business_process_tFaultHandlers_httpschemas_xmlsoap_orgws200303business_processcatch', True)

    
    catch = property(__catch.value, __catch.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        __catchAll.name() : __catchAll,
        __catch.name() : __catch
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tFaultHandlers', tFaultHandlers)


# Complex type tEventHandlers with content type ELEMENT_ONLY
class tEventHandlers (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tEventHandlers')
    # Base type is tExtensibleElements
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}onAlarm uses Python identifier onAlarm
    __onAlarm = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'onAlarm'), 'onAlarm', '__httpschemas_xmlsoap_orgws200303business_process_tEventHandlers_httpschemas_xmlsoap_orgws200303business_processonAlarm', True)

    
    onAlarm = property(__onAlarm.value, __onAlarm.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}onMessage uses Python identifier onMessage
    __onMessage = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'onMessage'), 'onMessage', '__httpschemas_xmlsoap_orgws200303business_process_tEventHandlers_httpschemas_xmlsoap_orgws200303business_processonMessage', True)

    
    onMessage = property(__onMessage.value, __onMessage.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        __onAlarm.name() : __onAlarm,
        __onMessage.name() : __onMessage
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tEventHandlers', tEventHandlers)


# Complex type tInvoke with content type ELEMENT_ONLY
class tInvoke (tActivity):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tInvoke')
    # Base type is tActivity
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}compensationHandler uses Python identifier compensationHandler
    __compensationHandler = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'compensationHandler'), 'compensationHandler', '__httpschemas_xmlsoap_orgws200303business_process_tInvoke_httpschemas_xmlsoap_orgws200303business_processcompensationHandler', False)

    
    compensationHandler = property(__compensationHandler.value, __compensationHandler.set, None, None)

    
    # Element target ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}target) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}correlations uses Python identifier correlations
    __correlations = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'correlations'), 'correlations', '__httpschemas_xmlsoap_orgws200303business_process_tInvoke_httpschemas_xmlsoap_orgws200303business_processcorrelations', False)

    
    correlations = property(__correlations.value, __correlations.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}catch uses Python identifier catch
    __catch = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'catch'), 'catch', '__httpschemas_xmlsoap_orgws200303business_process_tInvoke_httpschemas_xmlsoap_orgws200303business_processcatch', True)

    
    catch = property(__catch.value, __catch.set, None, None)

    
    # Element source ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}source) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}catchAll uses Python identifier catchAll
    __catchAll = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'catchAll'), 'catchAll', '__httpschemas_xmlsoap_orgws200303business_process_tInvoke_httpschemas_xmlsoap_orgws200303business_processcatchAll', False)

    
    catchAll = property(__catchAll.value, __catchAll.set, None, None)

    
    # Attribute suppressJoinFailure inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute operation uses Python identifier operation
    __operation = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'operation'), 'operation', '__httpschemas_xmlsoap_orgws200303business_process_tInvoke_operation', pyxb.binding.datatypes.NCName, required=True)
    
    operation = property(__operation.value, __operation.set, None, None)

    
    # Attribute inputVariable uses Python identifier inputVariable
    __inputVariable = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'inputVariable'), 'inputVariable', '__httpschemas_xmlsoap_orgws200303business_process_tInvoke_inputVariable', pyxb.binding.datatypes.NCName)
    
    inputVariable = property(__inputVariable.value, __inputVariable.set, None, None)

    
    # Attribute name inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute outputVariable uses Python identifier outputVariable
    __outputVariable = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'outputVariable'), 'outputVariable', '__httpschemas_xmlsoap_orgws200303business_process_tInvoke_outputVariable', pyxb.binding.datatypes.NCName)
    
    outputVariable = property(__outputVariable.value, __outputVariable.set, None, None)

    
    # Attribute joinCondition inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute portType uses Python identifier portType
    __portType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'portType'), 'portType', '__httpschemas_xmlsoap_orgws200303business_process_tInvoke_portType', pyxb.binding.datatypes.QName, required=True)
    
    portType = property(__portType.value, __portType.set, None, None)

    
    # Attribute partnerLink uses Python identifier partnerLink
    __partnerLink = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'partnerLink'), 'partnerLink', '__httpschemas_xmlsoap_orgws200303business_process_tInvoke_partnerLink', pyxb.binding.datatypes.NCName, required=True)
    
    partnerLink = property(__partnerLink.value, __partnerLink.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tActivity._ElementMap.copy()
    _ElementMap.update({
        __compensationHandler.name() : __compensationHandler,
        __correlations.name() : __correlations,
        __catch.name() : __catch,
        __catchAll.name() : __catchAll
    })
    _AttributeMap = tActivity._AttributeMap.copy()
    _AttributeMap.update({
        __operation.name() : __operation,
        __inputVariable.name() : __inputVariable,
        __outputVariable.name() : __outputVariable,
        __portType.name() : __portType,
        __partnerLink.name() : __partnerLink
    })
Namespace.addCategoryObject('typeBinding', u'tInvoke', tInvoke)


# Complex type tCorrelations with content type ELEMENT_ONLY
class tCorrelations (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tCorrelations')
    # Base type is tExtensibleElements
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}correlation uses Python identifier correlation
    __correlation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'correlation'), 'correlation', '__httpschemas_xmlsoap_orgws200303business_process_tCorrelations_httpschemas_xmlsoap_orgws200303business_processcorrelation', True)

    
    correlation = property(__correlation.value, __correlation.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        __correlation.name() : __correlation
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tCorrelations', tCorrelations)


# Complex type tReceive with content type ELEMENT_ONLY
class tReceive (tActivity):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tReceive')
    # Base type is tActivity
    
    # Element source ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}source) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}correlations uses Python identifier correlations
    __correlations = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'correlations'), 'correlations', '__httpschemas_xmlsoap_orgws200303business_process_tReceive_httpschemas_xmlsoap_orgws200303business_processcorrelations', False)

    
    correlations = property(__correlations.value, __correlations.set, None, None)

    
    # Element target ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}target) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute suppressJoinFailure inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute variable uses Python identifier variable
    __variable = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'variable'), 'variable', '__httpschemas_xmlsoap_orgws200303business_process_tReceive_variable', pyxb.binding.datatypes.NCName)
    
    variable = property(__variable.value, __variable.set, None, None)

    
    # Attribute createInstance uses Python identifier createInstance
    __createInstance = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'createInstance'), 'createInstance', '__httpschemas_xmlsoap_orgws200303business_process_tReceive_createInstance', tBoolean, unicode_default=u'no')
    
    createInstance = property(__createInstance.value, __createInstance.set, None, None)

    
    # Attribute partnerLink uses Python identifier partnerLink
    __partnerLink = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'partnerLink'), 'partnerLink', '__httpschemas_xmlsoap_orgws200303business_process_tReceive_partnerLink', pyxb.binding.datatypes.NCName, required=True)
    
    partnerLink = property(__partnerLink.value, __partnerLink.set, None, None)

    
    # Attribute name inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute portType uses Python identifier portType
    __portType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'portType'), 'portType', '__httpschemas_xmlsoap_orgws200303business_process_tReceive_portType', pyxb.binding.datatypes.QName, required=True)
    
    portType = property(__portType.value, __portType.set, None, None)

    
    # Attribute joinCondition inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute operation uses Python identifier operation
    __operation = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'operation'), 'operation', '__httpschemas_xmlsoap_orgws200303business_process_tReceive_operation', pyxb.binding.datatypes.NCName, required=True)
    
    operation = property(__operation.value, __operation.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tActivity._ElementMap.copy()
    _ElementMap.update({
        __correlations.name() : __correlations
    })
    _AttributeMap = tActivity._AttributeMap.copy()
    _AttributeMap.update({
        __variable.name() : __variable,
        __createInstance.name() : __createInstance,
        __partnerLink.name() : __partnerLink,
        __portType.name() : __portType,
        __operation.name() : __operation
    })
Namespace.addCategoryObject('typeBinding', u'tReceive', tReceive)


# Complex type tOnMessage with content type ELEMENT_ONLY
class tOnMessage (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tOnMessage')
    # Base type is tExtensibleElements
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}correlations uses Python identifier correlations
    __correlations = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'correlations'), 'correlations', '__httpschemas_xmlsoap_orgws200303business_process_tOnMessage_httpschemas_xmlsoap_orgws200303business_processcorrelations', False)

    
    correlations = property(__correlations.value, __correlations.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}sequence uses Python identifier sequence
    __sequence = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'sequence'), 'sequence', '__httpschemas_xmlsoap_orgws200303business_process_tOnMessage_httpschemas_xmlsoap_orgws200303business_processsequence', False)

    
    sequence = property(__sequence.value, __sequence.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}receive uses Python identifier receive
    __receive = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'receive'), 'receive', '__httpschemas_xmlsoap_orgws200303business_process_tOnMessage_httpschemas_xmlsoap_orgws200303business_processreceive', False)

    
    receive = property(__receive.value, __receive.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}pick uses Python identifier pick
    __pick = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'pick'), 'pick', '__httpschemas_xmlsoap_orgws200303business_process_tOnMessage_httpschemas_xmlsoap_orgws200303business_processpick', False)

    
    pick = property(__pick.value, __pick.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}flow uses Python identifier flow
    __flow = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'flow'), 'flow', '__httpschemas_xmlsoap_orgws200303business_process_tOnMessage_httpschemas_xmlsoap_orgws200303business_processflow', False)

    
    flow = property(__flow.value, __flow.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}wait uses Python identifier wait
    __wait = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'wait'), 'wait', '__httpschemas_xmlsoap_orgws200303business_process_tOnMessage_httpschemas_xmlsoap_orgws200303business_processwait', False)

    
    wait = property(__wait.value, __wait.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}empty uses Python identifier empty
    __empty = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'empty'), 'empty', '__httpschemas_xmlsoap_orgws200303business_process_tOnMessage_httpschemas_xmlsoap_orgws200303business_processempty', False)

    
    empty = property(__empty.value, __empty.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}scope uses Python identifier scope
    __scope = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'scope'), 'scope', '__httpschemas_xmlsoap_orgws200303business_process_tOnMessage_httpschemas_xmlsoap_orgws200303business_processscope', False)

    
    scope = property(__scope.value, __scope.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}switch uses Python identifier switch
    __switch = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'switch'), 'switch', '__httpschemas_xmlsoap_orgws200303business_process_tOnMessage_httpschemas_xmlsoap_orgws200303business_processswitch', False)

    
    switch = property(__switch.value, __switch.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}reply uses Python identifier reply
    __reply = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'reply'), 'reply', '__httpschemas_xmlsoap_orgws200303business_process_tOnMessage_httpschemas_xmlsoap_orgws200303business_processreply', False)

    
    reply = property(__reply.value, __reply.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}throw uses Python identifier throw
    __throw = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'throw'), 'throw', '__httpschemas_xmlsoap_orgws200303business_process_tOnMessage_httpschemas_xmlsoap_orgws200303business_processthrow', False)

    
    throw = property(__throw.value, __throw.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}while uses Python identifier while_
    __while = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'while'), 'while_', '__httpschemas_xmlsoap_orgws200303business_process_tOnMessage_httpschemas_xmlsoap_orgws200303business_processwhile', False)

    
    while_ = property(__while.value, __while.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}invoke uses Python identifier invoke
    __invoke = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'invoke'), 'invoke', '__httpschemas_xmlsoap_orgws200303business_process_tOnMessage_httpschemas_xmlsoap_orgws200303business_processinvoke', False)

    
    invoke = property(__invoke.value, __invoke.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}assign uses Python identifier assign
    __assign = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'assign'), 'assign', '__httpschemas_xmlsoap_orgws200303business_process_tOnMessage_httpschemas_xmlsoap_orgws200303business_processassign', False)

    
    assign = property(__assign.value, __assign.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}terminate uses Python identifier terminate
    __terminate = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'terminate'), 'terminate', '__httpschemas_xmlsoap_orgws200303business_process_tOnMessage_httpschemas_xmlsoap_orgws200303business_processterminate', False)

    
    terminate = property(__terminate.value, __terminate.set, None, None)

    
    # Attribute operation uses Python identifier operation
    __operation = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'operation'), 'operation', '__httpschemas_xmlsoap_orgws200303business_process_tOnMessage_operation', pyxb.binding.datatypes.NCName, required=True)
    
    operation = property(__operation.value, __operation.set, None, None)

    
    # Attribute variable uses Python identifier variable
    __variable = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'variable'), 'variable', '__httpschemas_xmlsoap_orgws200303business_process_tOnMessage_variable', pyxb.binding.datatypes.NCName)
    
    variable = property(__variable.value, __variable.set, None, None)

    
    # Attribute partnerLink uses Python identifier partnerLink
    __partnerLink = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'partnerLink'), 'partnerLink', '__httpschemas_xmlsoap_orgws200303business_process_tOnMessage_partnerLink', pyxb.binding.datatypes.NCName, required=True)
    
    partnerLink = property(__partnerLink.value, __partnerLink.set, None, None)

    
    # Attribute portType uses Python identifier portType
    __portType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'portType'), 'portType', '__httpschemas_xmlsoap_orgws200303business_process_tOnMessage_portType', pyxb.binding.datatypes.QName, required=True)
    
    portType = property(__portType.value, __portType.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        __correlations.name() : __correlations,
        __sequence.name() : __sequence,
        __receive.name() : __receive,
        __pick.name() : __pick,
        __flow.name() : __flow,
        __wait.name() : __wait,
        __empty.name() : __empty,
        __scope.name() : __scope,
        __switch.name() : __switch,
        __reply.name() : __reply,
        __throw.name() : __throw,
        __while.name() : __while,
        __invoke.name() : __invoke,
        __assign.name() : __assign,
        __terminate.name() : __terminate
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        __operation.name() : __operation,
        __variable.name() : __variable,
        __partnerLink.name() : __partnerLink,
        __portType.name() : __portType
    })
Namespace.addCategoryObject('typeBinding', u'tOnMessage', tOnMessage)


# Complex type tCatch with content type ELEMENT_ONLY
class tCatch (tActivityOrCompensateContainer):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tCatch')
    # Base type is tActivityOrCompensateContainer
    
    # Element assign ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}assign) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element terminate ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}terminate) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element flow ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}flow) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element receive ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}receive) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element while_ ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}while) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element wait ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}wait) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element switch ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}switch) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element scope ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}scope) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element empty ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}empty) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element reply ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}reply) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element compensate ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}compensate) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element sequence ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}sequence) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element throw ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}throw) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element invoke ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}invoke) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element pick ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}pick) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Attribute faultVariable uses Python identifier faultVariable
    __faultVariable = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'faultVariable'), 'faultVariable', '__httpschemas_xmlsoap_orgws200303business_process_tCatch_faultVariable', pyxb.binding.datatypes.NCName)
    
    faultVariable = property(__faultVariable.value, __faultVariable.set, None, None)

    
    # Attribute faultName uses Python identifier faultName
    __faultName = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'faultName'), 'faultName', '__httpschemas_xmlsoap_orgws200303business_process_tCatch_faultName', pyxb.binding.datatypes.QName)
    
    faultName = property(__faultName.value, __faultName.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tActivityOrCompensateContainer._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tActivityOrCompensateContainer._AttributeMap.copy()
    _AttributeMap.update({
        __faultVariable.name() : __faultVariable,
        __faultName.name() : __faultName
    })
Namespace.addCategoryObject('typeBinding', u'tCatch', tCatch)


# Complex type tCorrelation with content type ELEMENT_ONLY
class tCorrelation (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tCorrelation')
    # Base type is tExtensibleElements
    
    # Attribute initiate uses Python identifier initiate
    __initiate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'initiate'), 'initiate', '__httpschemas_xmlsoap_orgws200303business_process_tCorrelation_initiate', tBoolean, unicode_default=u'no')
    
    initiate = property(__initiate.value, __initiate.set, None, None)

    
    # Attribute set uses Python identifier set
    __set = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'set'), 'set', '__httpschemas_xmlsoap_orgws200303business_process_tCorrelation_set', pyxb.binding.datatypes.NCName, required=True)
    
    set = property(__set.value, __set.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        __initiate.name() : __initiate,
        __set.name() : __set
    })
Namespace.addCategoryObject('typeBinding', u'tCorrelation', tCorrelation)


# Complex type tWait with content type ELEMENT_ONLY
class tWait (tActivity):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tWait')
    # Base type is tActivity
    
    # Element source ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}source) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Element target ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}target) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute for uses Python identifier for_
    __for = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'for'), 'for_', '__httpschemas_xmlsoap_orgws200303business_process_tWait_for', tDuration_expr)
    
    for_ = property(__for.value, __for.set, None, None)

    
    # Attribute suppressJoinFailure inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute name inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute until uses Python identifier until
    __until = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'until'), 'until', '__httpschemas_xmlsoap_orgws200303business_process_tWait_until', tDeadline_expr)
    
    until = property(__until.value, __until.set, None, None)

    
    # Attribute joinCondition inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tActivity._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tActivity._AttributeMap.copy()
    _AttributeMap.update({
        __for.name() : __for,
        __until.name() : __until
    })
Namespace.addCategoryObject('typeBinding', u'tWait', tWait)


# Complex type tFrom with content type ELEMENT_ONLY
class tFrom (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tFrom')
    # Base type is tExtensibleElements
    
    # Attribute query uses Python identifier query
    __query = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'query'), 'query', '__httpschemas_xmlsoap_orgws200303business_process_tFrom_query', pyxb.binding.datatypes.string)
    
    query = property(__query.value, __query.set, None, None)

    
    # Attribute expression uses Python identifier expression
    __expression = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'expression'), 'expression', '__httpschemas_xmlsoap_orgws200303business_process_tFrom_expression', pyxb.binding.datatypes.string)
    
    expression = property(__expression.value, __expression.set, None, None)

    
    # Attribute partnerLink uses Python identifier partnerLink
    __partnerLink = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'partnerLink'), 'partnerLink', '__httpschemas_xmlsoap_orgws200303business_process_tFrom_partnerLink', pyxb.binding.datatypes.NCName)
    
    partnerLink = property(__partnerLink.value, __partnerLink.set, None, None)

    
    # Attribute property uses Python identifier property_
    __property = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'property'), 'property_', '__httpschemas_xmlsoap_orgws200303business_process_tFrom_property', pyxb.binding.datatypes.QName)
    
    property_ = property(__property.value, __property.set, None, None)

    
    # Attribute opaque uses Python identifier opaque
    __opaque = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'opaque'), 'opaque', '__httpschemas_xmlsoap_orgws200303business_process_tFrom_opaque', tBoolean)
    
    opaque = property(__opaque.value, __opaque.set, None, None)

    
    # Attribute variable uses Python identifier variable
    __variable = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'variable'), 'variable', '__httpschemas_xmlsoap_orgws200303business_process_tFrom_variable', pyxb.binding.datatypes.NCName)
    
    variable = property(__variable.value, __variable.set, None, None)

    
    # Attribute part uses Python identifier part
    __part = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'part'), 'part', '__httpschemas_xmlsoap_orgws200303business_process_tFrom_part', pyxb.binding.datatypes.NCName)
    
    part = property(__part.value, __part.set, None, None)

    
    # Attribute endpointReference uses Python identifier endpointReference
    __endpointReference = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'endpointReference'), 'endpointReference', '__httpschemas_xmlsoap_orgws200303business_process_tFrom_endpointReference', tRoles)
    
    endpointReference = property(__endpointReference.value, __endpointReference.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        __query.name() : __query,
        __expression.name() : __expression,
        __partnerLink.name() : __partnerLink,
        __property.name() : __property,
        __opaque.name() : __opaque,
        __variable.name() : __variable,
        __part.name() : __part,
        __endpointReference.name() : __endpointReference
    })
Namespace.addCategoryObject('typeBinding', u'tFrom', tFrom)


# Complex type CTD_ANON with content type EMPTY
class CTD_ANON (tFrom):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    # Base type is tFrom
    
    # Attribute query inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tFrom
    
    # Attribute opaque is restricted from parent
    
    # Attribute opaque uses Python identifier opaque
    __opaque = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'opaque'), 'opaque', '__httpschemas_xmlsoap_orgws200303business_process_tFrom_opaque', tBoolean, prohibited=True)
    
    opaque = property()

    
    # Attribute partnerLink inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tFrom
    
    # Attribute property_ inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tFrom
    
    # Attribute endpointReference is restricted from parent
    
    # Attribute endpointReference uses Python identifier endpointReference
    __endpointReference = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'endpointReference'), 'endpointReference', '__httpschemas_xmlsoap_orgws200303business_process_tFrom_endpointReference', tRoles, prohibited=True)
    
    endpointReference = property()

    
    # Attribute variable inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tFrom
    
    # Attribute part inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tFrom
    
    # Attribute expression is restricted from parent
    
    # Attribute expression uses Python identifier expression
    __expression = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'expression'), 'expression', '__httpschemas_xmlsoap_orgws200303business_process_tFrom_expression', pyxb.binding.datatypes.string, prohibited=True)
    
    expression = property()


    _ElementMap = tFrom._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tFrom._AttributeMap.copy()
    _AttributeMap.update({
        __opaque.name() : __opaque,
        __endpointReference.name() : __endpointReference,
        __expression.name() : __expression
    })



# Complex type tLinks with content type ELEMENT_ONLY
class tLinks (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tLinks')
    # Base type is tExtensibleElements
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}link uses Python identifier link
    __link = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'link'), 'link', '__httpschemas_xmlsoap_orgws200303business_process_tLinks_httpschemas_xmlsoap_orgws200303business_processlink', True)

    
    link = property(__link.value, __link.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        __link.name() : __link
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tLinks', tLinks)


# Complex type tLink with content type ELEMENT_ONLY
class tLink (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tLink')
    # Base type is tExtensibleElements
    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgws200303business_process_tLink_name', pyxb.binding.datatypes.NCName, required=True)
    
    name = property(__name.value, __name.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        __name.name() : __name
    })
Namespace.addCategoryObject('typeBinding', u'tLink', tLink)


# Complex type tProcess with content type ELEMENT_ONLY
class tProcess (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tProcess')
    # Base type is tExtensibleElements
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}pick uses Python identifier pick
    __pick = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'pick'), 'pick', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processpick', False)

    
    pick = property(__pick.value, __pick.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}variables uses Python identifier variables
    __variables = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'variables'), 'variables', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processvariables', False)

    
    variables = property(__variables.value, __variables.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}compensationHandler uses Python identifier compensationHandler
    __compensationHandler = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'compensationHandler'), 'compensationHandler', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processcompensationHandler', False)

    
    compensationHandler = property(__compensationHandler.value, __compensationHandler.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}eventHandlers uses Python identifier eventHandlers
    __eventHandlers = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'eventHandlers'), 'eventHandlers', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processeventHandlers', False)

    
    eventHandlers = property(__eventHandlers.value, __eventHandlers.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}receive uses Python identifier receive
    __receive = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'receive'), 'receive', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processreceive', False)

    
    receive = property(__receive.value, __receive.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}partnerLinks uses Python identifier partnerLinks
    __partnerLinks = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'partnerLinks'), 'partnerLinks', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processpartnerLinks', False)

    
    partnerLinks = property(__partnerLinks.value, __partnerLinks.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}reply uses Python identifier reply
    __reply = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'reply'), 'reply', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processreply', False)

    
    reply = property(__reply.value, __reply.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}throw uses Python identifier throw
    __throw = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'throw'), 'throw', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processthrow', False)

    
    throw = property(__throw.value, __throw.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}terminate uses Python identifier terminate
    __terminate = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'terminate'), 'terminate', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processterminate', False)

    
    terminate = property(__terminate.value, __terminate.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}while uses Python identifier while_
    __while = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'while'), 'while_', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processwhile', False)

    
    while_ = property(__while.value, __while.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}faultHandlers uses Python identifier faultHandlers
    __faultHandlers = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'faultHandlers'), 'faultHandlers', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processfaultHandlers', False)

    
    faultHandlers = property(__faultHandlers.value, __faultHandlers.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}flow uses Python identifier flow
    __flow = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'flow'), 'flow', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processflow', False)

    
    flow = property(__flow.value, __flow.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}invoke uses Python identifier invoke
    __invoke = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'invoke'), 'invoke', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processinvoke', False)

    
    invoke = property(__invoke.value, __invoke.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}scope uses Python identifier scope
    __scope = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'scope'), 'scope', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processscope', False)

    
    scope = property(__scope.value, __scope.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}correlationSets uses Python identifier correlationSets
    __correlationSets = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'correlationSets'), 'correlationSets', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processcorrelationSets', False)

    
    correlationSets = property(__correlationSets.value, __correlationSets.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}sequence uses Python identifier sequence
    __sequence = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'sequence'), 'sequence', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processsequence', False)

    
    sequence = property(__sequence.value, __sequence.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}partners uses Python identifier partners
    __partners = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'partners'), 'partners', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processpartners', False)

    
    partners = property(__partners.value, __partners.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}switch uses Python identifier switch
    __switch = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'switch'), 'switch', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processswitch', False)

    
    switch = property(__switch.value, __switch.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}empty uses Python identifier empty
    __empty = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'empty'), 'empty', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processempty', False)

    
    empty = property(__empty.value, __empty.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}assign uses Python identifier assign
    __assign = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'assign'), 'assign', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processassign', False)

    
    assign = property(__assign.value, __assign.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}wait uses Python identifier wait
    __wait = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'wait'), 'wait', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processwait', False)

    
    wait = property(__wait.value, __wait.set, None, None)

    
    # Attribute queryLanguage uses Python identifier queryLanguage
    __queryLanguage = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'queryLanguage'), 'queryLanguage', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_queryLanguage', pyxb.binding.datatypes.anyURI, unicode_default=u'http://www.w3.org/TR/1999/REC-xpath-19991116')
    
    queryLanguage = property(__queryLanguage.value, __queryLanguage.set, None, None)

    
    # Attribute expressionLanguage uses Python identifier expressionLanguage
    __expressionLanguage = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'expressionLanguage'), 'expressionLanguage', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_expressionLanguage', pyxb.binding.datatypes.anyURI, unicode_default=u'http://www.w3.org/TR/1999/REC-xpath-19991116')
    
    expressionLanguage = property(__expressionLanguage.value, __expressionLanguage.set, None, None)

    
    # Attribute targetNamespace uses Python identifier targetNamespace
    __targetNamespace = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'targetNamespace'), 'targetNamespace', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_targetNamespace', pyxb.binding.datatypes.anyURI, required=True)
    
    targetNamespace = property(__targetNamespace.value, __targetNamespace.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_name', pyxb.binding.datatypes.NCName, required=True)
    
    name = property(__name.value, __name.set, None, None)

    
    # Attribute enableInstanceCompensation uses Python identifier enableInstanceCompensation
    __enableInstanceCompensation = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'enableInstanceCompensation'), 'enableInstanceCompensation', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_enableInstanceCompensation', tBoolean, unicode_default=u'no')
    
    enableInstanceCompensation = property(__enableInstanceCompensation.value, __enableInstanceCompensation.set, None, None)

    
    # Attribute suppressJoinFailure uses Python identifier suppressJoinFailure
    __suppressJoinFailure = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'suppressJoinFailure'), 'suppressJoinFailure', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_suppressJoinFailure', tBoolean, unicode_default=u'no')
    
    suppressJoinFailure = property(__suppressJoinFailure.value, __suppressJoinFailure.set, None, None)

    
    # Attribute abstractProcess uses Python identifier abstractProcess
    __abstractProcess = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'abstractProcess'), 'abstractProcess', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_abstractProcess', tBoolean, unicode_default=u'no')
    
    abstractProcess = property(__abstractProcess.value, __abstractProcess.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        __pick.name() : __pick,
        __variables.name() : __variables,
        __compensationHandler.name() : __compensationHandler,
        __eventHandlers.name() : __eventHandlers,
        __receive.name() : __receive,
        __partnerLinks.name() : __partnerLinks,
        __reply.name() : __reply,
        __throw.name() : __throw,
        __terminate.name() : __terminate,
        __while.name() : __while,
        __faultHandlers.name() : __faultHandlers,
        __flow.name() : __flow,
        __invoke.name() : __invoke,
        __scope.name() : __scope,
        __correlationSets.name() : __correlationSets,
        __sequence.name() : __sequence,
        __partners.name() : __partners,
        __switch.name() : __switch,
        __empty.name() : __empty,
        __assign.name() : __assign,
        __wait.name() : __wait
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        __queryLanguage.name() : __queryLanguage,
        __expressionLanguage.name() : __expressionLanguage,
        __targetNamespace.name() : __targetNamespace,
        __name.name() : __name,
        __enableInstanceCompensation.name() : __enableInstanceCompensation,
        __suppressJoinFailure.name() : __suppressJoinFailure,
        __abstractProcess.name() : __abstractProcess
    })
Namespace.addCategoryObject('typeBinding', u'tProcess', tProcess)


# Complex type tTarget with content type ELEMENT_ONLY
class tTarget (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tTarget')
    # Base type is tExtensibleElements
    
    # Attribute linkName uses Python identifier linkName
    __linkName = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'linkName'), 'linkName', '__httpschemas_xmlsoap_orgws200303business_process_tTarget_linkName', pyxb.binding.datatypes.NCName, required=True)
    
    linkName = property(__linkName.value, __linkName.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        __linkName.name() : __linkName
    })
Namespace.addCategoryObject('typeBinding', u'tTarget', tTarget)


# Complex type tCorrelationSet with content type ELEMENT_ONLY
class tCorrelationSet (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tCorrelationSet')
    # Base type is tExtensibleElements
    
    # Attribute properties uses Python identifier properties
    __properties = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'properties'), 'properties', '__httpschemas_xmlsoap_orgws200303business_process_tCorrelationSet_properties', STD_ANON, required=True)
    
    properties = property(__properties.value, __properties.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgws200303business_process_tCorrelationSet_name', pyxb.binding.datatypes.NCName, required=True)
    
    name = property(__name.value, __name.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        __properties.name() : __properties,
        __name.name() : __name
    })
Namespace.addCategoryObject('typeBinding', u'tCorrelationSet', tCorrelationSet)


# Complex type tVariables with content type ELEMENT_ONLY
class tVariables (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tVariables')
    # Base type is tExtensibleElements
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}variable uses Python identifier variable
    __variable = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'variable'), 'variable', '__httpschemas_xmlsoap_orgws200303business_process_tVariables_httpschemas_xmlsoap_orgws200303business_processvariable', True)

    
    variable = property(__variable.value, __variable.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        __variable.name() : __variable
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tVariables', tVariables)


# Complex type tCorrelationWithPattern with content type ELEMENT_ONLY
class tCorrelationWithPattern (tCorrelation):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tCorrelationWithPattern')
    # Base type is tCorrelation
    
    # Attribute initiate inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tCorrelation
    
    # Attribute pattern uses Python identifier pattern
    __pattern = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'pattern'), 'pattern', '__httpschemas_xmlsoap_orgws200303business_process_tCorrelationWithPattern_pattern', STD_ANON_)
    
    pattern = property(__pattern.value, __pattern.set, None, None)

    
    # Attribute set inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tCorrelation
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tCorrelation._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tCorrelation._AttributeMap.copy()
    _AttributeMap.update({
        __pattern.name() : __pattern
    })
Namespace.addCategoryObject('typeBinding', u'tCorrelationWithPattern', tCorrelationWithPattern)


# Complex type CTD_ANON_ with content type ELEMENT_ONLY
class CTD_ANON_ (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is tExtensibleElements
    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgws200303business_process_CTD_ANON__name', pyxb.binding.datatypes.NCName, required=True)
    
    name = property(__name.value, __name.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        __name.name() : __name
    })



# Complex type tPartnerLink with content type ELEMENT_ONLY
class tPartnerLink (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tPartnerLink')
    # Base type is tExtensibleElements
    
    # Attribute myRole uses Python identifier myRole
    __myRole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'myRole'), 'myRole', '__httpschemas_xmlsoap_orgws200303business_process_tPartnerLink_myRole', pyxb.binding.datatypes.NCName)
    
    myRole = property(__myRole.value, __myRole.set, None, None)

    
    # Attribute partnerRole uses Python identifier partnerRole
    __partnerRole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'partnerRole'), 'partnerRole', '__httpschemas_xmlsoap_orgws200303business_process_tPartnerLink_partnerRole', pyxb.binding.datatypes.NCName)
    
    partnerRole = property(__partnerRole.value, __partnerRole.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgws200303business_process_tPartnerLink_name', pyxb.binding.datatypes.NCName, required=True)
    
    name = property(__name.value, __name.set, None, None)

    
    # Attribute partnerLinkType uses Python identifier partnerLinkType
    __partnerLinkType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'partnerLinkType'), 'partnerLinkType', '__httpschemas_xmlsoap_orgws200303business_process_tPartnerLink_partnerLinkType', pyxb.binding.datatypes.QName, required=True)
    
    partnerLinkType = property(__partnerLinkType.value, __partnerLinkType.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        __myRole.name() : __myRole,
        __partnerRole.name() : __partnerRole,
        __name.name() : __name,
        __partnerLinkType.name() : __partnerLinkType
    })
Namespace.addCategoryObject('typeBinding', u'tPartnerLink', tPartnerLink)


# Complex type CTD_ANON_2 with content type ELEMENT_ONLY
class CTD_ANON_2 (tActivityContainer):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is tActivityContainer
    
    # Element empty ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}empty) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element invoke ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}invoke) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element terminate ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}terminate) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element assign ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}assign) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element pick ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}pick) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element while_ ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}while) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element flow ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}flow) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element receive ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}receive) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element wait ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}wait) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element switch ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}switch) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element scope ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}scope) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element reply ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}reply) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element sequence ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}sequence) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element throw ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}throw) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Attribute condition uses Python identifier condition
    __condition = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'condition'), 'condition', '__httpschemas_xmlsoap_orgws200303business_process_CTD_ANON_2_condition', tBoolean_expr, required=True)
    
    condition = property(__condition.value, __condition.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tActivityContainer._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tActivityContainer._AttributeMap.copy()
    _AttributeMap.update({
        __condition.name() : __condition
    })



# Complex type tPartnerLinks with content type ELEMENT_ONLY
class tPartnerLinks (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tPartnerLinks')
    # Base type is tExtensibleElements
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}partnerLink uses Python identifier partnerLink
    __partnerLink = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'partnerLink'), 'partnerLink', '__httpschemas_xmlsoap_orgws200303business_process_tPartnerLinks_httpschemas_xmlsoap_orgws200303business_processpartnerLink', True)

    
    partnerLink = property(__partnerLink.value, __partnerLink.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        __partnerLink.name() : __partnerLink
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tPartnerLinks', tPartnerLinks)


# Complex type tPartner with content type ELEMENT_ONLY
class tPartner (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tPartner')
    # Base type is tExtensibleElements
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}partnerLink uses Python identifier partnerLink
    __partnerLink = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'partnerLink'), 'partnerLink', '__httpschemas_xmlsoap_orgws200303business_process_tPartner_httpschemas_xmlsoap_orgws200303business_processpartnerLink', True)

    
    partnerLink = property(__partnerLink.value, __partnerLink.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgws200303business_process_tPartner_name', pyxb.binding.datatypes.NCName, required=True)
    
    name = property(__name.value, __name.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        __partnerLink.name() : __partnerLink
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        __name.name() : __name
    })
Namespace.addCategoryObject('typeBinding', u'tPartner', tPartner)


# Complex type tPartners with content type ELEMENT_ONLY
class tPartners (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tPartners')
    # Base type is tExtensibleElements
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}partner uses Python identifier partner
    __partner = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'partner'), 'partner', '__httpschemas_xmlsoap_orgws200303business_process_tPartners_httpschemas_xmlsoap_orgws200303business_processpartner', True)

    
    partner = property(__partner.value, __partner.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        __partner.name() : __partner
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tPartners', tPartners)


# Complex type tVariable with content type EMPTY
class tVariable (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tVariable')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute element uses Python identifier element
    __element = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'element'), 'element', '__httpschemas_xmlsoap_orgws200303business_process_tVariable_element', pyxb.binding.datatypes.QName)
    
    element = property(__element.value, __element.set, None, None)

    
    # Attribute messageType uses Python identifier messageType
    __messageType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'messageType'), 'messageType', '__httpschemas_xmlsoap_orgws200303business_process_tVariable_messageType', pyxb.binding.datatypes.QName)
    
    messageType = property(__messageType.value, __messageType.set, None, None)

    
    # Attribute type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'type'), 'type', '__httpschemas_xmlsoap_orgws200303business_process_tVariable_type', pyxb.binding.datatypes.QName)
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgws200303business_process_tVariable_name', pyxb.binding.datatypes.NCName, required=True)
    
    name = property(__name.value, __name.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __element.name() : __element,
        __messageType.name() : __messageType,
        __type.name() : __type,
        __name.name() : __name
    }
Namespace.addCategoryObject('typeBinding', u'tVariable', tVariable)


# Complex type tCompensate with content type ELEMENT_ONLY
class tCompensate (tActivity):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tCompensate')
    # Base type is tActivity
    
    # Element source ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}source) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Element target ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}target) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute suppressJoinFailure inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute name inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute joinCondition inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute scope uses Python identifier scope
    __scope = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'scope'), 'scope', '__httpschemas_xmlsoap_orgws200303business_process_tCompensate_scope', pyxb.binding.datatypes.NCName)
    
    scope = property(__scope.value, __scope.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tActivity._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tActivity._AttributeMap.copy()
    _AttributeMap.update({
        __scope.name() : __scope
    })
Namespace.addCategoryObject('typeBinding', u'tCompensate', tCompensate)


# Complex type tSource with content type ELEMENT_ONLY
class tSource (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tSource')
    # Base type is tExtensibleElements
    
    # Attribute linkName uses Python identifier linkName
    __linkName = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'linkName'), 'linkName', '__httpschemas_xmlsoap_orgws200303business_process_tSource_linkName', pyxb.binding.datatypes.NCName, required=True)
    
    linkName = property(__linkName.value, __linkName.set, None, None)

    
    # Attribute transitionCondition uses Python identifier transitionCondition
    __transitionCondition = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'transitionCondition'), 'transitionCondition', '__httpschemas_xmlsoap_orgws200303business_process_tSource_transitionCondition', tBoolean_expr)
    
    transitionCondition = property(__transitionCondition.value, __transitionCondition.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        __linkName.name() : __linkName,
        __transitionCondition.name() : __transitionCondition
    })
Namespace.addCategoryObject('typeBinding', u'tSource', tSource)


to = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'to'), CTD_ANON)
Namespace.addCategoryObject('elementBinding', to.name().localName(), to)

from_ = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'from'), tFrom)
Namespace.addCategoryObject('elementBinding', from_.name().localName(), from_)

process = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'process'), tProcess)
Namespace.addCategoryObject('elementBinding', process.name().localName(), process)


tExtensibleElements._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tExtensibleElements._ContentModel = pyxb.binding.content.ParticleModel(tExtensibleElements._GroupModel, min_occurs=1, max_occurs=1)



tActivity._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'source'), tSource, scope=tActivity))

tActivity._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'target'), tTarget, scope=tActivity))
tActivity._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tActivity._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tActivity._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'target')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(tActivity._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'source')), min_occurs=0L, max_occurs=None)
    )
tActivity._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tActivity._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivity._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tActivity._ContentModel = pyxb.binding.content.ParticleModel(tActivity._GroupModel, min_occurs=1, max_occurs=1)


tTerminate._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tTerminate._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tTerminate._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'target')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(tTerminate._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'source')), min_occurs=0L, max_occurs=None)
    )
tTerminate._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tTerminate._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tTerminate._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tTerminate._ContentModel = pyxb.binding.content.ParticleModel(tTerminate._GroupModel, min_occurs=1, max_occurs=1)


tEmpty._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tEmpty._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tEmpty._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'target')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(tEmpty._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'source')), min_occurs=0L, max_occurs=None)
    )
tEmpty._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tEmpty._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tEmpty._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tEmpty._ContentModel = pyxb.binding.content.ParticleModel(tEmpty._GroupModel, min_occurs=1, max_occurs=1)



tCorrelationsWithPattern._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'correlation'), tCorrelationWithPattern, scope=tCorrelationsWithPattern))
tCorrelationsWithPattern._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tCorrelationsWithPattern._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tCorrelationsWithPattern._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'correlation')), min_occurs=1L, max_occurs=None)
    )
tCorrelationsWithPattern._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tCorrelationsWithPattern._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCorrelationsWithPattern._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tCorrelationsWithPattern._ContentModel = pyxb.binding.content.ParticleModel(tCorrelationsWithPattern._GroupModel, min_occurs=1, max_occurs=1)



tReply._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'correlations'), tCorrelations, scope=tReply))
tReply._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tReply._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tReply._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'target')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(tReply._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'source')), min_occurs=0L, max_occurs=None)
    )
tReply._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tReply._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tReply._GroupModel_3, min_occurs=1, max_occurs=1)
    )
tReply._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tReply._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'correlations')), min_occurs=0L, max_occurs=1)
    )
tReply._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tReply._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tReply._GroupModel_4, min_occurs=1, max_occurs=1)
    )
tReply._ContentModel = pyxb.binding.content.ParticleModel(tReply._GroupModel, min_occurs=1, max_occurs=1)



tCopy._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'to'), CTD_ANON, scope=tCopy))

tCopy._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'from'), tFrom, scope=tCopy))
tCopy._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tCopy._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tCopy._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'from')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCopy._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'to')), min_occurs=1, max_occurs=1)
    )
tCopy._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tCopy._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCopy._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tCopy._ContentModel = pyxb.binding.content.ParticleModel(tCopy._GroupModel, min_occurs=1, max_occurs=1)



tFlow._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'terminate'), tTerminate, scope=tFlow))

tFlow._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'while'), tWhile, scope=tFlow))

tFlow._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'sequence'), tSequence, scope=tFlow))

tFlow._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'scope'), tScope, scope=tFlow))

tFlow._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'pick'), tPick, scope=tFlow))

tFlow._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'flow'), tFlow, scope=tFlow))

tFlow._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'invoke'), tInvoke, scope=tFlow))

tFlow._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'empty'), tEmpty, scope=tFlow))

tFlow._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'reply'), tReply, scope=tFlow))

tFlow._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'throw'), tThrow, scope=tFlow))

tFlow._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'wait'), tWait, scope=tFlow))

tFlow._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'links'), tLinks, scope=tFlow))

tFlow._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'assign'), tAssign, scope=tFlow))

tFlow._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'switch'), tSwitch, scope=tFlow))

tFlow._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'receive'), tReceive, scope=tFlow))
tFlow._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tFlow._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tFlow._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'target')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(tFlow._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'source')), min_occurs=0L, max_occurs=None)
    )
tFlow._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tFlow._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tFlow._GroupModel_3, min_occurs=1, max_occurs=1)
    )
tFlow._GroupModel_5 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(tFlow._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'empty')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tFlow._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'invoke')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tFlow._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'receive')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tFlow._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'reply')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tFlow._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'assign')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tFlow._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'wait')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tFlow._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'throw')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tFlow._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'terminate')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tFlow._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'flow')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tFlow._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'switch')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tFlow._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'while')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tFlow._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sequence')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tFlow._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'pick')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tFlow._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'scope')), min_occurs=1, max_occurs=1)
    )
tFlow._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tFlow._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'links')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(tFlow._GroupModel_5, min_occurs=1, max_occurs=None)
    )
tFlow._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tFlow._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tFlow._GroupModel_4, min_occurs=1, max_occurs=1)
    )
tFlow._ContentModel = pyxb.binding.content.ParticleModel(tFlow._GroupModel, min_occurs=1, max_occurs=1)



tActivityContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'empty'), tEmpty, scope=tActivityContainer))

tActivityContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'invoke'), tInvoke, scope=tActivityContainer))

tActivityContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'terminate'), tTerminate, scope=tActivityContainer))

tActivityContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'assign'), tAssign, scope=tActivityContainer))

tActivityContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'pick'), tPick, scope=tActivityContainer))

tActivityContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'while'), tWhile, scope=tActivityContainer))

tActivityContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'flow'), tFlow, scope=tActivityContainer))

tActivityContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'receive'), tReceive, scope=tActivityContainer))

tActivityContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'wait'), tWait, scope=tActivityContainer))

tActivityContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'switch'), tSwitch, scope=tActivityContainer))

tActivityContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'scope'), tScope, scope=tActivityContainer))

tActivityContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'reply'), tReply, scope=tActivityContainer))

tActivityContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'sequence'), tSequence, scope=tActivityContainer))

tActivityContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'throw'), tThrow, scope=tActivityContainer))
tActivityContainer._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tActivityContainer._GroupModel_3 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(tActivityContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'empty')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'invoke')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'receive')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'reply')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'assign')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'wait')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'throw')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'terminate')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'flow')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'switch')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'while')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sequence')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'pick')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'scope')), min_occurs=1, max_occurs=1)
    )
tActivityContainer._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tActivityContainer._GroupModel_3, min_occurs=1, max_occurs=1)
    )
tActivityContainer._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tActivityContainer._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityContainer._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tActivityContainer._ContentModel = pyxb.binding.content.ParticleModel(tActivityContainer._GroupModel, min_occurs=1, max_occurs=1)


tOnAlarm._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tOnAlarm._GroupModel_3 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(tOnAlarm._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'empty')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnAlarm._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'invoke')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnAlarm._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'receive')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnAlarm._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'reply')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnAlarm._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'assign')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnAlarm._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'wait')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnAlarm._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'throw')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnAlarm._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'terminate')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnAlarm._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'flow')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnAlarm._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'switch')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnAlarm._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'while')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnAlarm._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sequence')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnAlarm._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'pick')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnAlarm._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'scope')), min_occurs=1, max_occurs=1)
    )
tOnAlarm._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tOnAlarm._GroupModel_3, min_occurs=1, max_occurs=1)
    )
tOnAlarm._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tOnAlarm._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnAlarm._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tOnAlarm._ContentModel = pyxb.binding.content.ParticleModel(tOnAlarm._GroupModel, min_occurs=1, max_occurs=1)



tScope._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'scope'), tScope, scope=tScope))

tScope._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'faultHandlers'), tFaultHandlers, scope=tScope))

tScope._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'sequence'), tSequence, scope=tScope))

tScope._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'empty'), tEmpty, scope=tScope))

tScope._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'eventHandlers'), tEventHandlers, scope=tScope))

tScope._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'compensationHandler'), tCompensationHandler, scope=tScope))

tScope._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'pick'), tPick, scope=tScope))

tScope._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'reply'), tReply, scope=tScope))

tScope._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'terminate'), tTerminate, scope=tScope))

tScope._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'throw'), tThrow, scope=tScope))

tScope._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'variables'), tVariables, scope=tScope))

tScope._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'assign'), tAssign, scope=tScope))

tScope._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'switch'), tSwitch, scope=tScope))

tScope._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'flow'), tFlow, scope=tScope))

tScope._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'correlationSets'), tCorrelationSets, scope=tScope))

tScope._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'while'), tWhile, scope=tScope))

tScope._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'invoke'), tInvoke, scope=tScope))

tScope._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'receive'), tReceive, scope=tScope))

tScope._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'wait'), tWait, scope=tScope))
tScope._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tScope._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'target')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'source')), min_occurs=0L, max_occurs=None)
    )
tScope._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tScope._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._GroupModel_3, min_occurs=1, max_occurs=1)
    )
tScope._GroupModel_5 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'empty')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'invoke')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'receive')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'reply')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'assign')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'wait')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'throw')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'terminate')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'flow')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'switch')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'while')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sequence')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'pick')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'scope')), min_occurs=1, max_occurs=1)
    )
tScope._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'variables')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'correlationSets')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'faultHandlers')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'compensationHandler')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'eventHandlers')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._GroupModel_5, min_occurs=1, max_occurs=1)
    )
tScope._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tScope._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._GroupModel_4, min_occurs=1, max_occurs=1)
    )
tScope._ContentModel = pyxb.binding.content.ParticleModel(tScope._GroupModel, min_occurs=1, max_occurs=1)



tAssign._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'copy'), tCopy, scope=tAssign))
tAssign._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tAssign._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tAssign._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'target')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(tAssign._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'source')), min_occurs=0L, max_occurs=None)
    )
tAssign._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tAssign._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tAssign._GroupModel_3, min_occurs=1, max_occurs=1)
    )
tAssign._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tAssign._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'copy')), min_occurs=1L, max_occurs=None)
    )
tAssign._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tAssign._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tAssign._GroupModel_4, min_occurs=1, max_occurs=1)
    )
tAssign._ContentModel = pyxb.binding.content.ParticleModel(tAssign._GroupModel, min_occurs=1, max_occurs=1)



tWhile._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'assign'), tAssign, scope=tWhile))

tWhile._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'pick'), tPick, scope=tWhile))

tWhile._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'terminate'), tTerminate, scope=tWhile))

tWhile._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'receive'), tReceive, scope=tWhile))

tWhile._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'flow'), tFlow, scope=tWhile))

tWhile._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'scope'), tScope, scope=tWhile))

tWhile._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'wait'), tWait, scope=tWhile))

tWhile._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'switch'), tSwitch, scope=tWhile))

tWhile._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'empty'), tEmpty, scope=tWhile))

tWhile._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'reply'), tReply, scope=tWhile))

tWhile._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'throw'), tThrow, scope=tWhile))

tWhile._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'while'), tWhile, scope=tWhile))

tWhile._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'invoke'), tInvoke, scope=tWhile))

tWhile._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'sequence'), tSequence, scope=tWhile))
tWhile._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tWhile._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tWhile._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'target')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(tWhile._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'source')), min_occurs=0L, max_occurs=None)
    )
tWhile._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tWhile._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tWhile._GroupModel_3, min_occurs=1, max_occurs=1)
    )
tWhile._GroupModel_5 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(tWhile._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'empty')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tWhile._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'invoke')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tWhile._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'receive')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tWhile._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'reply')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tWhile._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'assign')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tWhile._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'wait')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tWhile._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'throw')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tWhile._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'terminate')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tWhile._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'flow')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tWhile._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'switch')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tWhile._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'while')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tWhile._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sequence')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tWhile._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'pick')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tWhile._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'scope')), min_occurs=1, max_occurs=1)
    )
tWhile._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tWhile._GroupModel_5, min_occurs=1, max_occurs=1)
    )
tWhile._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tWhile._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tWhile._GroupModel_4, min_occurs=1, max_occurs=1)
    )
tWhile._ContentModel = pyxb.binding.content.ParticleModel(tWhile._GroupModel, min_occurs=1, max_occurs=1)



tSwitch._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'case'), CTD_ANON_2, scope=tSwitch))

tSwitch._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'otherwise'), tActivityContainer, scope=tSwitch))
tSwitch._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tSwitch._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tSwitch._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'target')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(tSwitch._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'source')), min_occurs=0L, max_occurs=None)
    )
tSwitch._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tSwitch._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tSwitch._GroupModel_3, min_occurs=1, max_occurs=1)
    )
tSwitch._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tSwitch._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'case')), min_occurs=1, max_occurs=None),
    pyxb.binding.content.ParticleModel(tSwitch._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'otherwise')), min_occurs=0L, max_occurs=1)
    )
tSwitch._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tSwitch._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tSwitch._GroupModel_4, min_occurs=1, max_occurs=1)
    )
tSwitch._ContentModel = pyxb.binding.content.ParticleModel(tSwitch._GroupModel, min_occurs=1, max_occurs=1)


tThrow._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tThrow._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tThrow._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'target')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(tThrow._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'source')), min_occurs=0L, max_occurs=None)
    )
tThrow._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tThrow._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tThrow._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tThrow._ContentModel = pyxb.binding.content.ParticleModel(tThrow._GroupModel, min_occurs=1, max_occurs=1)



tActivityOrCompensateContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'assign'), tAssign, scope=tActivityOrCompensateContainer))

tActivityOrCompensateContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'terminate'), tTerminate, scope=tActivityOrCompensateContainer))

tActivityOrCompensateContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'flow'), tFlow, scope=tActivityOrCompensateContainer))

tActivityOrCompensateContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'receive'), tReceive, scope=tActivityOrCompensateContainer))

tActivityOrCompensateContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'while'), tWhile, scope=tActivityOrCompensateContainer))

tActivityOrCompensateContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'wait'), tWait, scope=tActivityOrCompensateContainer))

tActivityOrCompensateContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'switch'), tSwitch, scope=tActivityOrCompensateContainer))

tActivityOrCompensateContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'scope'), tScope, scope=tActivityOrCompensateContainer))

tActivityOrCompensateContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'empty'), tEmpty, scope=tActivityOrCompensateContainer))

tActivityOrCompensateContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'reply'), tReply, scope=tActivityOrCompensateContainer))

tActivityOrCompensateContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'compensate'), tCompensate, scope=tActivityOrCompensateContainer))

tActivityOrCompensateContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'sequence'), tSequence, scope=tActivityOrCompensateContainer))

tActivityOrCompensateContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'throw'), tThrow, scope=tActivityOrCompensateContainer))

tActivityOrCompensateContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'invoke'), tInvoke, scope=tActivityOrCompensateContainer))

tActivityOrCompensateContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'pick'), tPick, scope=tActivityOrCompensateContainer))
tActivityOrCompensateContainer._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tActivityOrCompensateContainer._GroupModel_3 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(tActivityOrCompensateContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'empty')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityOrCompensateContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'invoke')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityOrCompensateContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'receive')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityOrCompensateContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'reply')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityOrCompensateContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'assign')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityOrCompensateContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'wait')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityOrCompensateContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'throw')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityOrCompensateContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'terminate')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityOrCompensateContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'flow')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityOrCompensateContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'switch')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityOrCompensateContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'while')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityOrCompensateContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sequence')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityOrCompensateContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'pick')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityOrCompensateContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'scope')), min_occurs=1, max_occurs=1)
    )
tActivityOrCompensateContainer._GroupModel_2 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(tActivityOrCompensateContainer._GroupModel_3, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityOrCompensateContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'compensate')), min_occurs=1, max_occurs=1)
    )
tActivityOrCompensateContainer._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tActivityOrCompensateContainer._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityOrCompensateContainer._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tActivityOrCompensateContainer._ContentModel = pyxb.binding.content.ParticleModel(tActivityOrCompensateContainer._GroupModel, min_occurs=1, max_occurs=1)


tCompensationHandler._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tCompensationHandler._GroupModel_3 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(tCompensationHandler._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'empty')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCompensationHandler._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'invoke')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCompensationHandler._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'receive')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCompensationHandler._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'reply')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCompensationHandler._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'assign')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCompensationHandler._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'wait')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCompensationHandler._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'throw')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCompensationHandler._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'terminate')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCompensationHandler._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'flow')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCompensationHandler._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'switch')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCompensationHandler._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'while')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCompensationHandler._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sequence')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCompensationHandler._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'pick')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCompensationHandler._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'scope')), min_occurs=1, max_occurs=1)
    )
tCompensationHandler._GroupModel_2 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(tCompensationHandler._GroupModel_3, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCompensationHandler._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'compensate')), min_occurs=1, max_occurs=1)
    )
tCompensationHandler._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tCompensationHandler._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCompensationHandler._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tCompensationHandler._ContentModel = pyxb.binding.content.ParticleModel(tCompensationHandler._GroupModel, min_occurs=1, max_occurs=1)



tPick._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'onMessage'), tOnMessage, scope=tPick))

tPick._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'onAlarm'), tOnAlarm, scope=tPick))
tPick._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tPick._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tPick._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'target')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(tPick._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'source')), min_occurs=0L, max_occurs=None)
    )
tPick._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tPick._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tPick._GroupModel_3, min_occurs=1, max_occurs=1)
    )
tPick._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tPick._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'onMessage')), min_occurs=1, max_occurs=None),
    pyxb.binding.content.ParticleModel(tPick._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'onAlarm')), min_occurs=0L, max_occurs=None)
    )
tPick._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tPick._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tPick._GroupModel_4, min_occurs=1, max_occurs=1)
    )
tPick._ContentModel = pyxb.binding.content.ParticleModel(tPick._GroupModel, min_occurs=1, max_occurs=1)



tSequence._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'terminate'), tTerminate, scope=tSequence))

tSequence._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'while'), tWhile, scope=tSequence))

tSequence._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'reply'), tReply, scope=tSequence))

tSequence._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'wait'), tWait, scope=tSequence))

tSequence._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'empty'), tEmpty, scope=tSequence))

tSequence._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'scope'), tScope, scope=tSequence))

tSequence._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'sequence'), tSequence, scope=tSequence))

tSequence._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'throw'), tThrow, scope=tSequence))

tSequence._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'invoke'), tInvoke, scope=tSequence))

tSequence._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'assign'), tAssign, scope=tSequence))

tSequence._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'switch'), tSwitch, scope=tSequence))

tSequence._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'flow'), tFlow, scope=tSequence))

tSequence._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'pick'), tPick, scope=tSequence))

tSequence._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'receive'), tReceive, scope=tSequence))
tSequence._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tSequence._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tSequence._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'target')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(tSequence._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'source')), min_occurs=0L, max_occurs=None)
    )
tSequence._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tSequence._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tSequence._GroupModel_3, min_occurs=1, max_occurs=1)
    )
tSequence._GroupModel_5 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(tSequence._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'empty')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tSequence._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'invoke')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tSequence._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'receive')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tSequence._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'reply')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tSequence._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'assign')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tSequence._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'wait')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tSequence._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'throw')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tSequence._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'terminate')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tSequence._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'flow')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tSequence._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'switch')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tSequence._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'while')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tSequence._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sequence')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tSequence._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'pick')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tSequence._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'scope')), min_occurs=1, max_occurs=1)
    )
tSequence._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tSequence._GroupModel_5, min_occurs=1, max_occurs=None)
    )
tSequence._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tSequence._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tSequence._GroupModel_4, min_occurs=1, max_occurs=1)
    )
tSequence._ContentModel = pyxb.binding.content.ParticleModel(tSequence._GroupModel, min_occurs=1, max_occurs=1)



tCorrelationSets._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'correlationSet'), tCorrelationSet, scope=tCorrelationSets))
tCorrelationSets._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tCorrelationSets._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tCorrelationSets._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'correlationSet')), min_occurs=1, max_occurs=None)
    )
tCorrelationSets._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tCorrelationSets._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCorrelationSets._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tCorrelationSets._ContentModel = pyxb.binding.content.ParticleModel(tCorrelationSets._GroupModel, min_occurs=1, max_occurs=1)



tFaultHandlers._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'catchAll'), tActivityOrCompensateContainer, scope=tFaultHandlers))

tFaultHandlers._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'catch'), tCatch, scope=tFaultHandlers))
tFaultHandlers._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tFaultHandlers._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tFaultHandlers._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'catch')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(tFaultHandlers._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'catchAll')), min_occurs=0L, max_occurs=1)
    )
tFaultHandlers._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tFaultHandlers._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tFaultHandlers._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tFaultHandlers._ContentModel = pyxb.binding.content.ParticleModel(tFaultHandlers._GroupModel, min_occurs=1, max_occurs=1)



tEventHandlers._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'onAlarm'), tOnAlarm, scope=tEventHandlers))

tEventHandlers._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'onMessage'), tOnMessage, scope=tEventHandlers))
tEventHandlers._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tEventHandlers._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tEventHandlers._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'onMessage')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(tEventHandlers._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'onAlarm')), min_occurs=0L, max_occurs=None)
    )
tEventHandlers._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tEventHandlers._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tEventHandlers._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tEventHandlers._ContentModel = pyxb.binding.content.ParticleModel(tEventHandlers._GroupModel, min_occurs=1, max_occurs=1)



tInvoke._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'compensationHandler'), tCompensationHandler, scope=tInvoke))

tInvoke._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'correlations'), tCorrelationsWithPattern, scope=tInvoke))

tInvoke._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'catch'), tCatch, scope=tInvoke))

tInvoke._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'catchAll'), tActivityOrCompensateContainer, scope=tInvoke))
tInvoke._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tInvoke._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tInvoke._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'target')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(tInvoke._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'source')), min_occurs=0L, max_occurs=None)
    )
tInvoke._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tInvoke._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tInvoke._GroupModel_3, min_occurs=1, max_occurs=1)
    )
tInvoke._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tInvoke._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'correlations')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(tInvoke._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'catch')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(tInvoke._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'catchAll')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(tInvoke._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'compensationHandler')), min_occurs=0L, max_occurs=1)
    )
tInvoke._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tInvoke._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tInvoke._GroupModel_4, min_occurs=1, max_occurs=1)
    )
tInvoke._ContentModel = pyxb.binding.content.ParticleModel(tInvoke._GroupModel, min_occurs=1, max_occurs=1)



tCorrelations._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'correlation'), tCorrelation, scope=tCorrelations))
tCorrelations._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tCorrelations._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tCorrelations._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'correlation')), min_occurs=1L, max_occurs=None)
    )
tCorrelations._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tCorrelations._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCorrelations._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tCorrelations._ContentModel = pyxb.binding.content.ParticleModel(tCorrelations._GroupModel, min_occurs=1, max_occurs=1)



tReceive._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'correlations'), tCorrelations, scope=tReceive))
tReceive._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tReceive._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tReceive._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'target')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(tReceive._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'source')), min_occurs=0L, max_occurs=None)
    )
tReceive._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tReceive._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tReceive._GroupModel_3, min_occurs=1, max_occurs=1)
    )
tReceive._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tReceive._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'correlations')), min_occurs=0L, max_occurs=1)
    )
tReceive._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tReceive._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tReceive._GroupModel_4, min_occurs=1, max_occurs=1)
    )
tReceive._ContentModel = pyxb.binding.content.ParticleModel(tReceive._GroupModel, min_occurs=1, max_occurs=1)



tOnMessage._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'correlations'), tCorrelations, scope=tOnMessage))

tOnMessage._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'sequence'), tSequence, scope=tOnMessage))

tOnMessage._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'receive'), tReceive, scope=tOnMessage))

tOnMessage._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'pick'), tPick, scope=tOnMessage))

tOnMessage._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'flow'), tFlow, scope=tOnMessage))

tOnMessage._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'wait'), tWait, scope=tOnMessage))

tOnMessage._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'empty'), tEmpty, scope=tOnMessage))

tOnMessage._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'scope'), tScope, scope=tOnMessage))

tOnMessage._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'switch'), tSwitch, scope=tOnMessage))

tOnMessage._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'reply'), tReply, scope=tOnMessage))

tOnMessage._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'throw'), tThrow, scope=tOnMessage))

tOnMessage._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'while'), tWhile, scope=tOnMessage))

tOnMessage._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'invoke'), tInvoke, scope=tOnMessage))

tOnMessage._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'assign'), tAssign, scope=tOnMessage))

tOnMessage._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'terminate'), tTerminate, scope=tOnMessage))
tOnMessage._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tOnMessage._GroupModel_3 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(tOnMessage._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'empty')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnMessage._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'invoke')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnMessage._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'receive')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnMessage._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'reply')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnMessage._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'assign')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnMessage._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'wait')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnMessage._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'throw')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnMessage._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'terminate')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnMessage._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'flow')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnMessage._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'switch')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnMessage._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'while')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnMessage._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sequence')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnMessage._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'pick')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnMessage._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'scope')), min_occurs=1, max_occurs=1)
    )
tOnMessage._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tOnMessage._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'correlations')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnMessage._GroupModel_3, min_occurs=1, max_occurs=1)
    )
tOnMessage._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tOnMessage._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnMessage._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tOnMessage._ContentModel = pyxb.binding.content.ParticleModel(tOnMessage._GroupModel, min_occurs=1, max_occurs=1)


tCatch._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tCatch._GroupModel_3 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(tCatch._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'empty')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCatch._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'invoke')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCatch._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'receive')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCatch._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'reply')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCatch._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'assign')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCatch._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'wait')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCatch._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'throw')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCatch._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'terminate')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCatch._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'flow')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCatch._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'switch')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCatch._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'while')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCatch._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sequence')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCatch._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'pick')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCatch._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'scope')), min_occurs=1, max_occurs=1)
    )
tCatch._GroupModel_2 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(tCatch._GroupModel_3, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCatch._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'compensate')), min_occurs=1, max_occurs=1)
    )
tCatch._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tCatch._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCatch._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tCatch._ContentModel = pyxb.binding.content.ParticleModel(tCatch._GroupModel, min_occurs=1, max_occurs=1)


tCorrelation._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tCorrelation._ContentModel = pyxb.binding.content.ParticleModel(tCorrelation._GroupModel, min_occurs=1, max_occurs=1)


tWait._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tWait._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tWait._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'target')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(tWait._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'source')), min_occurs=0L, max_occurs=None)
    )
tWait._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tWait._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tWait._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tWait._ContentModel = pyxb.binding.content.ParticleModel(tWait._GroupModel, min_occurs=1, max_occurs=1)


tFrom._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tFrom._ContentModel = pyxb.binding.content.ParticleModel(tFrom._GroupModel, min_occurs=1, max_occurs=1)



tLinks._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'link'), tLink, scope=tLinks))
tLinks._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tLinks._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tLinks._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'link')), min_occurs=1, max_occurs=None)
    )
tLinks._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tLinks._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tLinks._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tLinks._ContentModel = pyxb.binding.content.ParticleModel(tLinks._GroupModel, min_occurs=1, max_occurs=1)


tLink._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tLink._ContentModel = pyxb.binding.content.ParticleModel(tLink._GroupModel, min_occurs=1, max_occurs=1)



tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'pick'), tPick, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'variables'), tVariables, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'compensationHandler'), tCompensationHandler, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'eventHandlers'), tEventHandlers, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'receive'), tReceive, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'partnerLinks'), tPartnerLinks, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'reply'), tReply, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'throw'), tThrow, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'terminate'), tTerminate, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'while'), tWhile, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'faultHandlers'), tFaultHandlers, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'flow'), tFlow, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'invoke'), tInvoke, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'scope'), tScope, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'correlationSets'), tCorrelationSets, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'sequence'), tSequence, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'partners'), tPartners, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'switch'), tSwitch, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'empty'), tEmpty, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'assign'), tAssign, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'wait'), tWait, scope=tProcess))
tProcess._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tProcess._GroupModel_3 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'empty')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'invoke')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'receive')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'reply')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'assign')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'wait')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'throw')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'terminate')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'flow')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'switch')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'while')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sequence')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'pick')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'scope')), min_occurs=1, max_occurs=1)
    )
tProcess._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'partnerLinks')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'partners')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'variables')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'correlationSets')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'faultHandlers')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'compensationHandler')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'eventHandlers')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._GroupModel_3, min_occurs=1, max_occurs=1)
    )
tProcess._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tProcess._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tProcess._ContentModel = pyxb.binding.content.ParticleModel(tProcess._GroupModel, min_occurs=1, max_occurs=1)


tTarget._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tTarget._ContentModel = pyxb.binding.content.ParticleModel(tTarget._GroupModel, min_occurs=1, max_occurs=1)


tCorrelationSet._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tCorrelationSet._ContentModel = pyxb.binding.content.ParticleModel(tCorrelationSet._GroupModel, min_occurs=1, max_occurs=1)



tVariables._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'variable'), tVariable, scope=tVariables))
tVariables._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tVariables._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tVariables._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'variable')), min_occurs=1, max_occurs=None)
    )
tVariables._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tVariables._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tVariables._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tVariables._ContentModel = pyxb.binding.content.ParticleModel(tVariables._GroupModel, min_occurs=1, max_occurs=1)


tCorrelationWithPattern._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tCorrelationWithPattern._ContentModel = pyxb.binding.content.ParticleModel(tCorrelationWithPattern._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_._GroupModel, min_occurs=1, max_occurs=1)


tPartnerLink._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tPartnerLink._ContentModel = pyxb.binding.content.ParticleModel(tPartnerLink._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_2._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_2._GroupModel_3 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(CTD_ANON_2._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'empty')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_2._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'invoke')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_2._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'receive')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_2._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'reply')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_2._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'assign')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_2._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'wait')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_2._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'throw')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_2._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'terminate')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_2._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'flow')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_2._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'switch')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_2._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'while')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_2._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sequence')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_2._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'pick')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_2._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'scope')), min_occurs=1, max_occurs=1)
    )
CTD_ANON_2._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_2._GroupModel_3, min_occurs=1, max_occurs=1)
    )
CTD_ANON_2._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_2._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_2._GroupModel_2, min_occurs=1, max_occurs=1)
    )
CTD_ANON_2._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_2._GroupModel, min_occurs=1, max_occurs=1)



tPartnerLinks._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'partnerLink'), tPartnerLink, scope=tPartnerLinks))
tPartnerLinks._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tPartnerLinks._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tPartnerLinks._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'partnerLink')), min_occurs=1L, max_occurs=None)
    )
tPartnerLinks._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tPartnerLinks._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tPartnerLinks._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tPartnerLinks._ContentModel = pyxb.binding.content.ParticleModel(tPartnerLinks._GroupModel, min_occurs=1, max_occurs=1)



tPartner._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'partnerLink'), CTD_ANON_, scope=tPartner))
tPartner._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tPartner._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tPartner._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'partnerLink')), min_occurs=1L, max_occurs=None)
    )
tPartner._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tPartner._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tPartner._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tPartner._ContentModel = pyxb.binding.content.ParticleModel(tPartner._GroupModel, min_occurs=1, max_occurs=1)



tPartners._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'partner'), tPartner, scope=tPartners))
tPartners._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tPartners._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tPartners._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'partner')), min_occurs=1L, max_occurs=None)
    )
tPartners._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tPartners._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tPartners._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tPartners._ContentModel = pyxb.binding.content.ParticleModel(tPartners._GroupModel, min_occurs=1, max_occurs=1)


tCompensate._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tCompensate._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tCompensate._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'target')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(tCompensate._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'source')), min_occurs=0L, max_occurs=None)
    )
tCompensate._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tCompensate._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCompensate._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tCompensate._ContentModel = pyxb.binding.content.ParticleModel(tCompensate._GroupModel, min_occurs=1, max_occurs=1)


tSource._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tSource._ContentModel = pyxb.binding.content.ParticleModel(tSource._GroupModel, min_occurs=1, max_occurs=1)

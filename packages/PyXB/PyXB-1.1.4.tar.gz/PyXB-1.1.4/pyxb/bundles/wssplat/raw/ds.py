# ./pyxb/bundles/wssplat/raw/ds.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:f1c343a882e7a65fb879f4ee813309f8231f28c8
# Generated 2012-06-15 14:42:56.617332 by PyXB version 1.1.4
# Namespace http://www.w3.org/2000/09/xmldsig#

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:4e253f68-b722-11e1-be00-c8600024e903')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes

Namespace = pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#', create_if_missing=True)
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
class DigestValueType (pyxb.binding.datatypes.base64Binary):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'DigestValueType')
    _Documentation = None
DigestValueType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'DigestValueType', DigestValueType)

# Atomic SimpleTypeDefinition
class CryptoBinary (pyxb.binding.datatypes.base64Binary):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'CryptoBinary')
    _Documentation = None
CryptoBinary._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'CryptoBinary', CryptoBinary)

# Atomic SimpleTypeDefinition
class HMACOutputLengthType (pyxb.binding.datatypes.integer):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'HMACOutputLengthType')
    _Documentation = None
HMACOutputLengthType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'HMACOutputLengthType', HMACOutputLengthType)

# Complex type TransformsType with content type ELEMENT_ONLY
class TransformsType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TransformsType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2000/09/xmldsig#}Transform uses Python identifier Transform
    __Transform = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Transform'), 'Transform', '__httpwww_w3_org200009xmldsig_TransformsType_httpwww_w3_org200009xmldsigTransform', True)

    
    Transform = property(__Transform.value, __Transform.set, None, None)


    _ElementMap = {
        __Transform.name() : __Transform
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'TransformsType', TransformsType)


# Complex type SignaturePropertyType with content type MIXED
class SignaturePropertyType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SignaturePropertyType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Target uses Python identifier Target
    __Target = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Target'), 'Target', '__httpwww_w3_org200009xmldsig_SignaturePropertyType_Target', pyxb.binding.datatypes.anyURI, required=True)
    
    Target = property(__Target.value, __Target.set, None, None)

    
    # Attribute Id uses Python identifier Id
    __Id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Id'), 'Id', '__httpwww_w3_org200009xmldsig_SignaturePropertyType_Id', pyxb.binding.datatypes.ID)
    
    Id = property(__Id.value, __Id.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Target.name() : __Target,
        __Id.name() : __Id
    }
Namespace.addCategoryObject('typeBinding', u'SignaturePropertyType', SignaturePropertyType)


# Complex type SignaturePropertiesType with content type ELEMENT_ONLY
class SignaturePropertiesType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SignaturePropertiesType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2000/09/xmldsig#}SignatureProperty uses Python identifier SignatureProperty
    __SignatureProperty = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SignatureProperty'), 'SignatureProperty', '__httpwww_w3_org200009xmldsig_SignaturePropertiesType_httpwww_w3_org200009xmldsigSignatureProperty', True)

    
    SignatureProperty = property(__SignatureProperty.value, __SignatureProperty.set, None, None)

    
    # Attribute Id uses Python identifier Id
    __Id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Id'), 'Id', '__httpwww_w3_org200009xmldsig_SignaturePropertiesType_Id', pyxb.binding.datatypes.ID)
    
    Id = property(__Id.value, __Id.set, None, None)


    _ElementMap = {
        __SignatureProperty.name() : __SignatureProperty
    }
    _AttributeMap = {
        __Id.name() : __Id
    }
Namespace.addCategoryObject('typeBinding', u'SignaturePropertiesType', SignaturePropertiesType)


# Complex type KeyInfoType with content type MIXED
class KeyInfoType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'KeyInfoType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2000/09/xmldsig#}RetrievalMethod uses Python identifier RetrievalMethod
    __RetrievalMethod = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'RetrievalMethod'), 'RetrievalMethod', '__httpwww_w3_org200009xmldsig_KeyInfoType_httpwww_w3_org200009xmldsigRetrievalMethod', True)

    
    RetrievalMethod = property(__RetrievalMethod.value, __RetrievalMethod.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}SPKIData uses Python identifier SPKIData
    __SPKIData = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SPKIData'), 'SPKIData', '__httpwww_w3_org200009xmldsig_KeyInfoType_httpwww_w3_org200009xmldsigSPKIData', True)

    
    SPKIData = property(__SPKIData.value, __SPKIData.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}KeyName uses Python identifier KeyName
    __KeyName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'KeyName'), 'KeyName', '__httpwww_w3_org200009xmldsig_KeyInfoType_httpwww_w3_org200009xmldsigKeyName', True)

    
    KeyName = property(__KeyName.value, __KeyName.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}X509Data uses Python identifier X509Data
    __X509Data = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'X509Data'), 'X509Data', '__httpwww_w3_org200009xmldsig_KeyInfoType_httpwww_w3_org200009xmldsigX509Data', True)

    
    X509Data = property(__X509Data.value, __X509Data.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}MgmtData uses Python identifier MgmtData
    __MgmtData = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'MgmtData'), 'MgmtData', '__httpwww_w3_org200009xmldsig_KeyInfoType_httpwww_w3_org200009xmldsigMgmtData', True)

    
    MgmtData = property(__MgmtData.value, __MgmtData.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}KeyValue uses Python identifier KeyValue
    __KeyValue = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'KeyValue'), 'KeyValue', '__httpwww_w3_org200009xmldsig_KeyInfoType_httpwww_w3_org200009xmldsigKeyValue', True)

    
    KeyValue = property(__KeyValue.value, __KeyValue.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}PGPData uses Python identifier PGPData
    __PGPData = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PGPData'), 'PGPData', '__httpwww_w3_org200009xmldsig_KeyInfoType_httpwww_w3_org200009xmldsigPGPData', True)

    
    PGPData = property(__PGPData.value, __PGPData.set, None, None)

    
    # Attribute Id uses Python identifier Id
    __Id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Id'), 'Id', '__httpwww_w3_org200009xmldsig_KeyInfoType_Id', pyxb.binding.datatypes.ID)
    
    Id = property(__Id.value, __Id.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        __RetrievalMethod.name() : __RetrievalMethod,
        __SPKIData.name() : __SPKIData,
        __KeyName.name() : __KeyName,
        __X509Data.name() : __X509Data,
        __MgmtData.name() : __MgmtData,
        __KeyValue.name() : __KeyValue,
        __PGPData.name() : __PGPData
    }
    _AttributeMap = {
        __Id.name() : __Id
    }
Namespace.addCategoryObject('typeBinding', u'KeyInfoType', KeyInfoType)


# Complex type X509DataType with content type ELEMENT_ONLY
class X509DataType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'X509DataType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2000/09/xmldsig#}X509IssuerSerial uses Python identifier X509IssuerSerial
    __X509IssuerSerial = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'X509IssuerSerial'), 'X509IssuerSerial', '__httpwww_w3_org200009xmldsig_X509DataType_httpwww_w3_org200009xmldsigX509IssuerSerial', True)

    
    X509IssuerSerial = property(__X509IssuerSerial.value, __X509IssuerSerial.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}X509CRL uses Python identifier X509CRL
    __X509CRL = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'X509CRL'), 'X509CRL', '__httpwww_w3_org200009xmldsig_X509DataType_httpwww_w3_org200009xmldsigX509CRL', True)

    
    X509CRL = property(__X509CRL.value, __X509CRL.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}X509Certificate uses Python identifier X509Certificate
    __X509Certificate = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'X509Certificate'), 'X509Certificate', '__httpwww_w3_org200009xmldsig_X509DataType_httpwww_w3_org200009xmldsigX509Certificate', True)

    
    X509Certificate = property(__X509Certificate.value, __X509Certificate.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}X509SKI uses Python identifier X509SKI
    __X509SKI = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'X509SKI'), 'X509SKI', '__httpwww_w3_org200009xmldsig_X509DataType_httpwww_w3_org200009xmldsigX509SKI', True)

    
    X509SKI = property(__X509SKI.value, __X509SKI.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}X509SubjectName uses Python identifier X509SubjectName
    __X509SubjectName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'X509SubjectName'), 'X509SubjectName', '__httpwww_w3_org200009xmldsig_X509DataType_httpwww_w3_org200009xmldsigX509SubjectName', True)

    
    X509SubjectName = property(__X509SubjectName.value, __X509SubjectName.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        __X509IssuerSerial.name() : __X509IssuerSerial,
        __X509CRL.name() : __X509CRL,
        __X509Certificate.name() : __X509Certificate,
        __X509SKI.name() : __X509SKI,
        __X509SubjectName.name() : __X509SubjectName
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'X509DataType', X509DataType)


# Complex type KeyValueType with content type MIXED
class KeyValueType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'KeyValueType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2000/09/xmldsig#}DSAKeyValue uses Python identifier DSAKeyValue
    __DSAKeyValue = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'DSAKeyValue'), 'DSAKeyValue', '__httpwww_w3_org200009xmldsig_KeyValueType_httpwww_w3_org200009xmldsigDSAKeyValue', False)

    
    DSAKeyValue = property(__DSAKeyValue.value, __DSAKeyValue.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}RSAKeyValue uses Python identifier RSAKeyValue
    __RSAKeyValue = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'RSAKeyValue'), 'RSAKeyValue', '__httpwww_w3_org200009xmldsig_KeyValueType_httpwww_w3_org200009xmldsigRSAKeyValue', False)

    
    RSAKeyValue = property(__RSAKeyValue.value, __RSAKeyValue.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        __DSAKeyValue.name() : __DSAKeyValue,
        __RSAKeyValue.name() : __RSAKeyValue
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'KeyValueType', KeyValueType)


# Complex type SignatureMethodType with content type MIXED
class SignatureMethodType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SignatureMethodType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2000/09/xmldsig#}HMACOutputLength uses Python identifier HMACOutputLength
    __HMACOutputLength = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'HMACOutputLength'), 'HMACOutputLength', '__httpwww_w3_org200009xmldsig_SignatureMethodType_httpwww_w3_org200009xmldsigHMACOutputLength', False)

    
    HMACOutputLength = property(__HMACOutputLength.value, __HMACOutputLength.set, None, None)

    
    # Attribute Algorithm uses Python identifier Algorithm
    __Algorithm = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Algorithm'), 'Algorithm', '__httpwww_w3_org200009xmldsig_SignatureMethodType_Algorithm', pyxb.binding.datatypes.anyURI, required=True)
    
    Algorithm = property(__Algorithm.value, __Algorithm.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        __HMACOutputLength.name() : __HMACOutputLength
    }
    _AttributeMap = {
        __Algorithm.name() : __Algorithm
    }
Namespace.addCategoryObject('typeBinding', u'SignatureMethodType', SignatureMethodType)


# Complex type SPKIDataType with content type ELEMENT_ONLY
class SPKIDataType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SPKIDataType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2000/09/xmldsig#}SPKISexp uses Python identifier SPKISexp
    __SPKISexp = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SPKISexp'), 'SPKISexp', '__httpwww_w3_org200009xmldsig_SPKIDataType_httpwww_w3_org200009xmldsigSPKISexp', True)

    
    SPKISexp = property(__SPKISexp.value, __SPKISexp.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        __SPKISexp.name() : __SPKISexp
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'SPKIDataType', SPKIDataType)


# Complex type ObjectType with content type MIXED
class ObjectType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ObjectType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Encoding uses Python identifier Encoding
    __Encoding = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Encoding'), 'Encoding', '__httpwww_w3_org200009xmldsig_ObjectType_Encoding', pyxb.binding.datatypes.anyURI)
    
    Encoding = property(__Encoding.value, __Encoding.set, None, None)

    
    # Attribute MimeType uses Python identifier MimeType
    __MimeType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'MimeType'), 'MimeType', '__httpwww_w3_org200009xmldsig_ObjectType_MimeType', pyxb.binding.datatypes.string)
    
    MimeType = property(__MimeType.value, __MimeType.set, None, None)

    
    # Attribute Id uses Python identifier Id
    __Id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Id'), 'Id', '__httpwww_w3_org200009xmldsig_ObjectType_Id', pyxb.binding.datatypes.ID)
    
    Id = property(__Id.value, __Id.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Encoding.name() : __Encoding,
        __MimeType.name() : __MimeType,
        __Id.name() : __Id
    }
Namespace.addCategoryObject('typeBinding', u'ObjectType', ObjectType)


# Complex type CanonicalizationMethodType with content type MIXED
class CanonicalizationMethodType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'CanonicalizationMethodType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Algorithm uses Python identifier Algorithm
    __Algorithm = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Algorithm'), 'Algorithm', '__httpwww_w3_org200009xmldsig_CanonicalizationMethodType_Algorithm', pyxb.binding.datatypes.anyURI, required=True)
    
    Algorithm = property(__Algorithm.value, __Algorithm.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Algorithm.name() : __Algorithm
    }
Namespace.addCategoryObject('typeBinding', u'CanonicalizationMethodType', CanonicalizationMethodType)


# Complex type TransformType with content type MIXED
class TransformType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TransformType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2000/09/xmldsig#}XPath uses Python identifier XPath
    __XPath = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'XPath'), 'XPath', '__httpwww_w3_org200009xmldsig_TransformType_httpwww_w3_org200009xmldsigXPath', True)

    
    XPath = property(__XPath.value, __XPath.set, None, None)

    
    # Attribute Algorithm uses Python identifier Algorithm
    __Algorithm = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Algorithm'), 'Algorithm', '__httpwww_w3_org200009xmldsig_TransformType_Algorithm', pyxb.binding.datatypes.anyURI, required=True)
    
    Algorithm = property(__Algorithm.value, __Algorithm.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        __XPath.name() : __XPath
    }
    _AttributeMap = {
        __Algorithm.name() : __Algorithm
    }
Namespace.addCategoryObject('typeBinding', u'TransformType', TransformType)


# Complex type ReferenceType with content type ELEMENT_ONLY
class ReferenceType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ReferenceType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2000/09/xmldsig#}DigestMethod uses Python identifier DigestMethod
    __DigestMethod = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'DigestMethod'), 'DigestMethod', '__httpwww_w3_org200009xmldsig_ReferenceType_httpwww_w3_org200009xmldsigDigestMethod', False)

    
    DigestMethod = property(__DigestMethod.value, __DigestMethod.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}DigestValue uses Python identifier DigestValue
    __DigestValue = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'DigestValue'), 'DigestValue', '__httpwww_w3_org200009xmldsig_ReferenceType_httpwww_w3_org200009xmldsigDigestValue', False)

    
    DigestValue = property(__DigestValue.value, __DigestValue.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}Transforms uses Python identifier Transforms
    __Transforms = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Transforms'), 'Transforms', '__httpwww_w3_org200009xmldsig_ReferenceType_httpwww_w3_org200009xmldsigTransforms', False)

    
    Transforms = property(__Transforms.value, __Transforms.set, None, None)

    
    # Attribute URI uses Python identifier URI
    __URI = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'URI'), 'URI', '__httpwww_w3_org200009xmldsig_ReferenceType_URI', pyxb.binding.datatypes.anyURI)
    
    URI = property(__URI.value, __URI.set, None, None)

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__httpwww_w3_org200009xmldsig_ReferenceType_Type', pyxb.binding.datatypes.anyURI)
    
    Type = property(__Type.value, __Type.set, None, None)

    
    # Attribute Id uses Python identifier Id
    __Id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Id'), 'Id', '__httpwww_w3_org200009xmldsig_ReferenceType_Id', pyxb.binding.datatypes.ID)
    
    Id = property(__Id.value, __Id.set, None, None)


    _ElementMap = {
        __DigestMethod.name() : __DigestMethod,
        __DigestValue.name() : __DigestValue,
        __Transforms.name() : __Transforms
    }
    _AttributeMap = {
        __URI.name() : __URI,
        __Type.name() : __Type,
        __Id.name() : __Id
    }
Namespace.addCategoryObject('typeBinding', u'ReferenceType', ReferenceType)


# Complex type SignedInfoType with content type ELEMENT_ONLY
class SignedInfoType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SignedInfoType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2000/09/xmldsig#}SignatureMethod uses Python identifier SignatureMethod
    __SignatureMethod = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SignatureMethod'), 'SignatureMethod', '__httpwww_w3_org200009xmldsig_SignedInfoType_httpwww_w3_org200009xmldsigSignatureMethod', False)

    
    SignatureMethod = property(__SignatureMethod.value, __SignatureMethod.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}Reference uses Python identifier Reference
    __Reference = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Reference'), 'Reference', '__httpwww_w3_org200009xmldsig_SignedInfoType_httpwww_w3_org200009xmldsigReference', True)

    
    Reference = property(__Reference.value, __Reference.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}CanonicalizationMethod uses Python identifier CanonicalizationMethod
    __CanonicalizationMethod = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'CanonicalizationMethod'), 'CanonicalizationMethod', '__httpwww_w3_org200009xmldsig_SignedInfoType_httpwww_w3_org200009xmldsigCanonicalizationMethod', False)

    
    CanonicalizationMethod = property(__CanonicalizationMethod.value, __CanonicalizationMethod.set, None, None)

    
    # Attribute Id uses Python identifier Id
    __Id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Id'), 'Id', '__httpwww_w3_org200009xmldsig_SignedInfoType_Id', pyxb.binding.datatypes.ID)
    
    Id = property(__Id.value, __Id.set, None, None)


    _ElementMap = {
        __SignatureMethod.name() : __SignatureMethod,
        __Reference.name() : __Reference,
        __CanonicalizationMethod.name() : __CanonicalizationMethod
    }
    _AttributeMap = {
        __Id.name() : __Id
    }
Namespace.addCategoryObject('typeBinding', u'SignedInfoType', SignedInfoType)


# Complex type RetrievalMethodType with content type ELEMENT_ONLY
class RetrievalMethodType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'RetrievalMethodType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2000/09/xmldsig#}Transforms uses Python identifier Transforms
    __Transforms = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Transforms'), 'Transforms', '__httpwww_w3_org200009xmldsig_RetrievalMethodType_httpwww_w3_org200009xmldsigTransforms', False)

    
    Transforms = property(__Transforms.value, __Transforms.set, None, None)

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__httpwww_w3_org200009xmldsig_RetrievalMethodType_Type', pyxb.binding.datatypes.anyURI)
    
    Type = property(__Type.value, __Type.set, None, None)

    
    # Attribute URI uses Python identifier URI
    __URI = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'URI'), 'URI', '__httpwww_w3_org200009xmldsig_RetrievalMethodType_URI', pyxb.binding.datatypes.anyURI)
    
    URI = property(__URI.value, __URI.set, None, None)


    _ElementMap = {
        __Transforms.name() : __Transforms
    }
    _AttributeMap = {
        __Type.name() : __Type,
        __URI.name() : __URI
    }
Namespace.addCategoryObject('typeBinding', u'RetrievalMethodType', RetrievalMethodType)


# Complex type ManifestType with content type ELEMENT_ONLY
class ManifestType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ManifestType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2000/09/xmldsig#}Reference uses Python identifier Reference
    __Reference = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Reference'), 'Reference', '__httpwww_w3_org200009xmldsig_ManifestType_httpwww_w3_org200009xmldsigReference', True)

    
    Reference = property(__Reference.value, __Reference.set, None, None)

    
    # Attribute Id uses Python identifier Id
    __Id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Id'), 'Id', '__httpwww_w3_org200009xmldsig_ManifestType_Id', pyxb.binding.datatypes.ID)
    
    Id = property(__Id.value, __Id.set, None, None)


    _ElementMap = {
        __Reference.name() : __Reference
    }
    _AttributeMap = {
        __Id.name() : __Id
    }
Namespace.addCategoryObject('typeBinding', u'ManifestType', ManifestType)


# Complex type SignatureType with content type ELEMENT_ONLY
class SignatureType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SignatureType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2000/09/xmldsig#}SignedInfo uses Python identifier SignedInfo
    __SignedInfo = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SignedInfo'), 'SignedInfo', '__httpwww_w3_org200009xmldsig_SignatureType_httpwww_w3_org200009xmldsigSignedInfo', False)

    
    SignedInfo = property(__SignedInfo.value, __SignedInfo.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}KeyInfo uses Python identifier KeyInfo
    __KeyInfo = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'KeyInfo'), 'KeyInfo', '__httpwww_w3_org200009xmldsig_SignatureType_httpwww_w3_org200009xmldsigKeyInfo', False)

    
    KeyInfo = property(__KeyInfo.value, __KeyInfo.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}Object uses Python identifier Object
    __Object = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Object'), 'Object', '__httpwww_w3_org200009xmldsig_SignatureType_httpwww_w3_org200009xmldsigObject', True)

    
    Object = property(__Object.value, __Object.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}SignatureValue uses Python identifier SignatureValue
    __SignatureValue = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SignatureValue'), 'SignatureValue', '__httpwww_w3_org200009xmldsig_SignatureType_httpwww_w3_org200009xmldsigSignatureValue', False)

    
    SignatureValue = property(__SignatureValue.value, __SignatureValue.set, None, None)

    
    # Attribute Id uses Python identifier Id
    __Id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Id'), 'Id', '__httpwww_w3_org200009xmldsig_SignatureType_Id', pyxb.binding.datatypes.ID)
    
    Id = property(__Id.value, __Id.set, None, None)


    _ElementMap = {
        __SignedInfo.name() : __SignedInfo,
        __KeyInfo.name() : __KeyInfo,
        __Object.name() : __Object,
        __SignatureValue.name() : __SignatureValue
    }
    _AttributeMap = {
        __Id.name() : __Id
    }
Namespace.addCategoryObject('typeBinding', u'SignatureType', SignatureType)


# Complex type DigestMethodType with content type MIXED
class DigestMethodType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'DigestMethodType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Algorithm uses Python identifier Algorithm
    __Algorithm = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Algorithm'), 'Algorithm', '__httpwww_w3_org200009xmldsig_DigestMethodType_Algorithm', pyxb.binding.datatypes.anyURI, required=True)
    
    Algorithm = property(__Algorithm.value, __Algorithm.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Algorithm.name() : __Algorithm
    }
Namespace.addCategoryObject('typeBinding', u'DigestMethodType', DigestMethodType)


# Complex type PGPDataType with content type ELEMENT_ONLY
class PGPDataType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'PGPDataType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2000/09/xmldsig#}PGPKeyID uses Python identifier PGPKeyID
    __PGPKeyID = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PGPKeyID'), 'PGPKeyID', '__httpwww_w3_org200009xmldsig_PGPDataType_httpwww_w3_org200009xmldsigPGPKeyID', False)

    
    PGPKeyID = property(__PGPKeyID.value, __PGPKeyID.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}PGPKeyPacket uses Python identifier PGPKeyPacket
    __PGPKeyPacket = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PGPKeyPacket'), 'PGPKeyPacket', '__httpwww_w3_org200009xmldsig_PGPDataType_httpwww_w3_org200009xmldsigPGPKeyPacket', False)

    
    PGPKeyPacket = property(__PGPKeyPacket.value, __PGPKeyPacket.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        __PGPKeyID.name() : __PGPKeyID,
        __PGPKeyPacket.name() : __PGPKeyPacket
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'PGPDataType', PGPDataType)


# Complex type X509IssuerSerialType with content type ELEMENT_ONLY
class X509IssuerSerialType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'X509IssuerSerialType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2000/09/xmldsig#}X509SerialNumber uses Python identifier X509SerialNumber
    __X509SerialNumber = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'X509SerialNumber'), 'X509SerialNumber', '__httpwww_w3_org200009xmldsig_X509IssuerSerialType_httpwww_w3_org200009xmldsigX509SerialNumber', False)

    
    X509SerialNumber = property(__X509SerialNumber.value, __X509SerialNumber.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}X509IssuerName uses Python identifier X509IssuerName
    __X509IssuerName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'X509IssuerName'), 'X509IssuerName', '__httpwww_w3_org200009xmldsig_X509IssuerSerialType_httpwww_w3_org200009xmldsigX509IssuerName', False)

    
    X509IssuerName = property(__X509IssuerName.value, __X509IssuerName.set, None, None)


    _ElementMap = {
        __X509SerialNumber.name() : __X509SerialNumber,
        __X509IssuerName.name() : __X509IssuerName
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'X509IssuerSerialType', X509IssuerSerialType)


# Complex type RSAKeyValueType with content type ELEMENT_ONLY
class RSAKeyValueType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'RSAKeyValueType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2000/09/xmldsig#}Exponent uses Python identifier Exponent
    __Exponent = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Exponent'), 'Exponent', '__httpwww_w3_org200009xmldsig_RSAKeyValueType_httpwww_w3_org200009xmldsigExponent', False)

    
    Exponent = property(__Exponent.value, __Exponent.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}Modulus uses Python identifier Modulus
    __Modulus = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Modulus'), 'Modulus', '__httpwww_w3_org200009xmldsig_RSAKeyValueType_httpwww_w3_org200009xmldsigModulus', False)

    
    Modulus = property(__Modulus.value, __Modulus.set, None, None)


    _ElementMap = {
        __Exponent.name() : __Exponent,
        __Modulus.name() : __Modulus
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'RSAKeyValueType', RSAKeyValueType)


# Complex type SignatureValueType with content type SIMPLE
class SignatureValueType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.base64Binary
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SignatureValueType')
    # Base type is pyxb.binding.datatypes.base64Binary
    
    # Attribute Id uses Python identifier Id
    __Id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Id'), 'Id', '__httpwww_w3_org200009xmldsig_SignatureValueType_Id', pyxb.binding.datatypes.ID)
    
    Id = property(__Id.value, __Id.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __Id.name() : __Id
    }
Namespace.addCategoryObject('typeBinding', u'SignatureValueType', SignatureValueType)


# Complex type DSAKeyValueType with content type ELEMENT_ONLY
class DSAKeyValueType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'DSAKeyValueType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2000/09/xmldsig#}Q uses Python identifier Q
    __Q = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Q'), 'Q', '__httpwww_w3_org200009xmldsig_DSAKeyValueType_httpwww_w3_org200009xmldsigQ', False)

    
    Q = property(__Q.value, __Q.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}G uses Python identifier G
    __G = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'G'), 'G', '__httpwww_w3_org200009xmldsig_DSAKeyValueType_httpwww_w3_org200009xmldsigG', False)

    
    G = property(__G.value, __G.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}Seed uses Python identifier Seed
    __Seed = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Seed'), 'Seed', '__httpwww_w3_org200009xmldsig_DSAKeyValueType_httpwww_w3_org200009xmldsigSeed', False)

    
    Seed = property(__Seed.value, __Seed.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}P uses Python identifier P
    __P = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'P'), 'P', '__httpwww_w3_org200009xmldsig_DSAKeyValueType_httpwww_w3_org200009xmldsigP', False)

    
    P = property(__P.value, __P.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}PgenCounter uses Python identifier PgenCounter
    __PgenCounter = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PgenCounter'), 'PgenCounter', '__httpwww_w3_org200009xmldsig_DSAKeyValueType_httpwww_w3_org200009xmldsigPgenCounter', False)

    
    PgenCounter = property(__PgenCounter.value, __PgenCounter.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}J uses Python identifier J
    __J = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'J'), 'J', '__httpwww_w3_org200009xmldsig_DSAKeyValueType_httpwww_w3_org200009xmldsigJ', False)

    
    J = property(__J.value, __J.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}Y uses Python identifier Y
    __Y = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Y'), 'Y', '__httpwww_w3_org200009xmldsig_DSAKeyValueType_httpwww_w3_org200009xmldsigY', False)

    
    Y = property(__Y.value, __Y.set, None, None)


    _ElementMap = {
        __Q.name() : __Q,
        __G.name() : __G,
        __Seed.name() : __Seed,
        __P.name() : __P,
        __PgenCounter.name() : __PgenCounter,
        __J.name() : __J,
        __Y.name() : __Y
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'DSAKeyValueType', DSAKeyValueType)


Transforms = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Transforms'), TransformsType)
Namespace.addCategoryObject('elementBinding', Transforms.name().localName(), Transforms)

DigestValue = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DigestValue'), DigestValueType)
Namespace.addCategoryObject('elementBinding', DigestValue.name().localName(), DigestValue)

SignatureProperties = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SignatureProperties'), SignaturePropertiesType)
Namespace.addCategoryObject('elementBinding', SignatureProperties.name().localName(), SignatureProperties)

KeyInfo = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'KeyInfo'), KeyInfoType)
Namespace.addCategoryObject('elementBinding', KeyInfo.name().localName(), KeyInfo)

X509Data = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'X509Data'), X509DataType)
Namespace.addCategoryObject('elementBinding', X509Data.name().localName(), X509Data)

Object = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Object'), ObjectType)
Namespace.addCategoryObject('elementBinding', Object.name().localName(), Object)

CanonicalizationMethod = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CanonicalizationMethod'), CanonicalizationMethodType)
Namespace.addCategoryObject('elementBinding', CanonicalizationMethod.name().localName(), CanonicalizationMethod)

MgmtData = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MgmtData'), pyxb.binding.datatypes.string)
Namespace.addCategoryObject('elementBinding', MgmtData.name().localName(), MgmtData)

SignedInfo = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SignedInfo'), SignedInfoType)
Namespace.addCategoryObject('elementBinding', SignedInfo.name().localName(), SignedInfo)

RetrievalMethod = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RetrievalMethod'), RetrievalMethodType)
Namespace.addCategoryObject('elementBinding', RetrievalMethod.name().localName(), RetrievalMethod)

KeyName = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'KeyName'), pyxb.binding.datatypes.string)
Namespace.addCategoryObject('elementBinding', KeyName.name().localName(), KeyName)

SPKIData = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SPKIData'), SPKIDataType)
Namespace.addCategoryObject('elementBinding', SPKIData.name().localName(), SPKIData)

Transform = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Transform'), TransformType)
Namespace.addCategoryObject('elementBinding', Transform.name().localName(), Transform)

Manifest = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Manifest'), ManifestType)
Namespace.addCategoryObject('elementBinding', Manifest.name().localName(), Manifest)

SignatureMethod = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SignatureMethod'), SignatureMethodType)
Namespace.addCategoryObject('elementBinding', SignatureMethod.name().localName(), SignatureMethod)

Signature = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Signature'), SignatureType)
Namespace.addCategoryObject('elementBinding', Signature.name().localName(), Signature)

PGPData = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PGPData'), PGPDataType)
Namespace.addCategoryObject('elementBinding', PGPData.name().localName(), PGPData)

SignatureProperty = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SignatureProperty'), SignaturePropertyType)
Namespace.addCategoryObject('elementBinding', SignatureProperty.name().localName(), SignatureProperty)

RSAKeyValue = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RSAKeyValue'), RSAKeyValueType)
Namespace.addCategoryObject('elementBinding', RSAKeyValue.name().localName(), RSAKeyValue)

DigestMethod = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DigestMethod'), DigestMethodType)
Namespace.addCategoryObject('elementBinding', DigestMethod.name().localName(), DigestMethod)

KeyValue = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'KeyValue'), KeyValueType)
Namespace.addCategoryObject('elementBinding', KeyValue.name().localName(), KeyValue)

Reference = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Reference'), ReferenceType)
Namespace.addCategoryObject('elementBinding', Reference.name().localName(), Reference)

SignatureValue = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SignatureValue'), SignatureValueType)
Namespace.addCategoryObject('elementBinding', SignatureValue.name().localName(), SignatureValue)

DSAKeyValue = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DSAKeyValue'), DSAKeyValueType)
Namespace.addCategoryObject('elementBinding', DSAKeyValue.name().localName(), DSAKeyValue)



TransformsType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Transform'), TransformType, scope=TransformsType))
TransformsType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TransformsType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Transform')), min_occurs=1, max_occurs=None)
    )
TransformsType._ContentModel = pyxb.binding.content.ParticleModel(TransformsType._GroupModel, min_occurs=1, max_occurs=1)


SignaturePropertyType._GroupModel = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2000/09/xmldsig#')), min_occurs=1, max_occurs=1)
    )
SignaturePropertyType._ContentModel = pyxb.binding.content.ParticleModel(SignaturePropertyType._GroupModel, min_occurs=1, max_occurs=None)



SignaturePropertiesType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SignatureProperty'), SignaturePropertyType, scope=SignaturePropertiesType))
SignaturePropertiesType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SignaturePropertiesType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SignatureProperty')), min_occurs=1, max_occurs=None)
    )
SignaturePropertiesType._ContentModel = pyxb.binding.content.ParticleModel(SignaturePropertiesType._GroupModel, min_occurs=1, max_occurs=1)



KeyInfoType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RetrievalMethod'), RetrievalMethodType, scope=KeyInfoType))

KeyInfoType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SPKIData'), SPKIDataType, scope=KeyInfoType))

KeyInfoType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'KeyName'), pyxb.binding.datatypes.string, scope=KeyInfoType))

KeyInfoType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'X509Data'), X509DataType, scope=KeyInfoType))

KeyInfoType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MgmtData'), pyxb.binding.datatypes.string, scope=KeyInfoType))

KeyInfoType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'KeyValue'), KeyValueType, scope=KeyInfoType))

KeyInfoType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PGPData'), PGPDataType, scope=KeyInfoType))
KeyInfoType._GroupModel = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(KeyInfoType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'KeyName')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(KeyInfoType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'KeyValue')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(KeyInfoType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'RetrievalMethod')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(KeyInfoType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'X509Data')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(KeyInfoType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PGPData')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(KeyInfoType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SPKIData')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(KeyInfoType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'MgmtData')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2000/09/xmldsig#')), min_occurs=1, max_occurs=1)
    )
KeyInfoType._ContentModel = pyxb.binding.content.ParticleModel(KeyInfoType._GroupModel, min_occurs=1, max_occurs=None)



X509DataType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'X509IssuerSerial'), X509IssuerSerialType, scope=X509DataType))

X509DataType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'X509CRL'), pyxb.binding.datatypes.base64Binary, scope=X509DataType))

X509DataType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'X509Certificate'), pyxb.binding.datatypes.base64Binary, scope=X509DataType))

X509DataType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'X509SKI'), pyxb.binding.datatypes.base64Binary, scope=X509DataType))

X509DataType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'X509SubjectName'), pyxb.binding.datatypes.string, scope=X509DataType))
X509DataType._GroupModel_ = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(X509DataType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'X509IssuerSerial')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(X509DataType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'X509SKI')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(X509DataType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'X509SubjectName')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(X509DataType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'X509Certificate')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(X509DataType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'X509CRL')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2000/09/xmldsig#')), min_occurs=1, max_occurs=1)
    )
X509DataType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(X509DataType._GroupModel_, min_occurs=1, max_occurs=1)
    )
X509DataType._ContentModel = pyxb.binding.content.ParticleModel(X509DataType._GroupModel, min_occurs=1, max_occurs=None)



KeyValueType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DSAKeyValue'), DSAKeyValueType, scope=KeyValueType))

KeyValueType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RSAKeyValue'), RSAKeyValueType, scope=KeyValueType))
KeyValueType._GroupModel = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(KeyValueType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DSAKeyValue')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(KeyValueType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'RSAKeyValue')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2000/09/xmldsig#')), min_occurs=1, max_occurs=1)
    )
KeyValueType._ContentModel = pyxb.binding.content.ParticleModel(KeyValueType._GroupModel, min_occurs=1, max_occurs=1)



SignatureMethodType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'HMACOutputLength'), HMACOutputLengthType, scope=SignatureMethodType))
SignatureMethodType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SignatureMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'HMACOutputLength')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2000/09/xmldsig#')), min_occurs=0L, max_occurs=None)
    )
SignatureMethodType._ContentModel = pyxb.binding.content.ParticleModel(SignatureMethodType._GroupModel, min_occurs=1, max_occurs=1)



SPKIDataType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SPKISexp'), pyxb.binding.datatypes.base64Binary, scope=SPKIDataType))
SPKIDataType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SPKIDataType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SPKISexp')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2000/09/xmldsig#')), min_occurs=0L, max_occurs=1)
    )
SPKIDataType._ContentModel = pyxb.binding.content.ParticleModel(SPKIDataType._GroupModel, min_occurs=1, max_occurs=None)


ObjectType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any), min_occurs=1, max_occurs=1)
    )
ObjectType._ContentModel = pyxb.binding.content.ParticleModel(ObjectType._GroupModel, min_occurs=0L, max_occurs=None)


CanonicalizationMethodType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=pyxb.binding.content.Wildcard.NC_any), min_occurs=0L, max_occurs=None)
    )
CanonicalizationMethodType._ContentModel = pyxb.binding.content.ParticleModel(CanonicalizationMethodType._GroupModel, min_occurs=1, max_occurs=1)



TransformType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'XPath'), pyxb.binding.datatypes.string, scope=TransformType))
TransformType._GroupModel = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2000/09/xmldsig#')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(TransformType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'XPath')), min_occurs=1, max_occurs=1)
    )
TransformType._ContentModel = pyxb.binding.content.ParticleModel(TransformType._GroupModel, min_occurs=0L, max_occurs=None)



ReferenceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DigestMethod'), DigestMethodType, scope=ReferenceType))

ReferenceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DigestValue'), DigestValueType, scope=ReferenceType))

ReferenceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Transforms'), TransformsType, scope=ReferenceType))
ReferenceType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ReferenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Transforms')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ReferenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DigestMethod')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ReferenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DigestValue')), min_occurs=1, max_occurs=1)
    )
ReferenceType._ContentModel = pyxb.binding.content.ParticleModel(ReferenceType._GroupModel, min_occurs=1, max_occurs=1)



SignedInfoType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SignatureMethod'), SignatureMethodType, scope=SignedInfoType))

SignedInfoType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Reference'), ReferenceType, scope=SignedInfoType))

SignedInfoType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CanonicalizationMethod'), CanonicalizationMethodType, scope=SignedInfoType))
SignedInfoType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SignedInfoType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'CanonicalizationMethod')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(SignedInfoType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SignatureMethod')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(SignedInfoType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Reference')), min_occurs=1, max_occurs=None)
    )
SignedInfoType._ContentModel = pyxb.binding.content.ParticleModel(SignedInfoType._GroupModel, min_occurs=1, max_occurs=1)



RetrievalMethodType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Transforms'), TransformsType, scope=RetrievalMethodType))
RetrievalMethodType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RetrievalMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Transforms')), min_occurs=0L, max_occurs=1)
    )
RetrievalMethodType._ContentModel = pyxb.binding.content.ParticleModel(RetrievalMethodType._GroupModel, min_occurs=1, max_occurs=1)



ManifestType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Reference'), ReferenceType, scope=ManifestType))
ManifestType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ManifestType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Reference')), min_occurs=1, max_occurs=None)
    )
ManifestType._ContentModel = pyxb.binding.content.ParticleModel(ManifestType._GroupModel, min_occurs=1, max_occurs=1)



SignatureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SignedInfo'), SignedInfoType, scope=SignatureType))

SignatureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'KeyInfo'), KeyInfoType, scope=SignatureType))

SignatureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Object'), ObjectType, scope=SignatureType))

SignatureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SignatureValue'), SignatureValueType, scope=SignatureType))
SignatureType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SignatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SignedInfo')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(SignatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SignatureValue')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(SignatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'KeyInfo')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(SignatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Object')), min_occurs=0L, max_occurs=None)
    )
SignatureType._ContentModel = pyxb.binding.content.ParticleModel(SignatureType._GroupModel, min_occurs=1, max_occurs=1)


DigestMethodType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2000/09/xmldsig#')), min_occurs=0L, max_occurs=None)
    )
DigestMethodType._ContentModel = pyxb.binding.content.ParticleModel(DigestMethodType._GroupModel, min_occurs=1, max_occurs=1)



PGPDataType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PGPKeyID'), pyxb.binding.datatypes.base64Binary, scope=PGPDataType))

PGPDataType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PGPKeyPacket'), pyxb.binding.datatypes.base64Binary, scope=PGPDataType))
PGPDataType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PGPDataType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PGPKeyID')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(PGPDataType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PGPKeyPacket')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2000/09/xmldsig#')), min_occurs=0L, max_occurs=None)
    )
PGPDataType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PGPDataType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PGPKeyPacket')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2000/09/xmldsig#')), min_occurs=0L, max_occurs=None)
    )
PGPDataType._GroupModel = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(PGPDataType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(PGPDataType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
PGPDataType._ContentModel = pyxb.binding.content.ParticleModel(PGPDataType._GroupModel, min_occurs=1, max_occurs=1)



X509IssuerSerialType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'X509SerialNumber'), pyxb.binding.datatypes.integer, scope=X509IssuerSerialType))

X509IssuerSerialType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'X509IssuerName'), pyxb.binding.datatypes.string, scope=X509IssuerSerialType))
X509IssuerSerialType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(X509IssuerSerialType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'X509IssuerName')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(X509IssuerSerialType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'X509SerialNumber')), min_occurs=1, max_occurs=1)
    )
X509IssuerSerialType._ContentModel = pyxb.binding.content.ParticleModel(X509IssuerSerialType._GroupModel, min_occurs=1, max_occurs=1)



RSAKeyValueType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Exponent'), CryptoBinary, scope=RSAKeyValueType))

RSAKeyValueType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Modulus'), CryptoBinary, scope=RSAKeyValueType))
RSAKeyValueType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RSAKeyValueType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Modulus')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(RSAKeyValueType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Exponent')), min_occurs=1, max_occurs=1)
    )
RSAKeyValueType._ContentModel = pyxb.binding.content.ParticleModel(RSAKeyValueType._GroupModel, min_occurs=1, max_occurs=1)



DSAKeyValueType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Q'), CryptoBinary, scope=DSAKeyValueType))

DSAKeyValueType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'G'), CryptoBinary, scope=DSAKeyValueType))

DSAKeyValueType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Seed'), CryptoBinary, scope=DSAKeyValueType))

DSAKeyValueType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'P'), CryptoBinary, scope=DSAKeyValueType))

DSAKeyValueType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PgenCounter'), CryptoBinary, scope=DSAKeyValueType))

DSAKeyValueType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'J'), CryptoBinary, scope=DSAKeyValueType))

DSAKeyValueType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Y'), CryptoBinary, scope=DSAKeyValueType))
DSAKeyValueType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(DSAKeyValueType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'P')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(DSAKeyValueType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Q')), min_occurs=1, max_occurs=1)
    )
DSAKeyValueType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(DSAKeyValueType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Seed')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(DSAKeyValueType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PgenCounter')), min_occurs=1, max_occurs=1)
    )
DSAKeyValueType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(DSAKeyValueType._GroupModel_, min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(DSAKeyValueType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'G')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(DSAKeyValueType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Y')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(DSAKeyValueType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'J')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(DSAKeyValueType._GroupModel_2, min_occurs=0L, max_occurs=1)
    )
DSAKeyValueType._ContentModel = pyxb.binding.content.ParticleModel(DSAKeyValueType._GroupModel, min_occurs=1, max_occurs=1)

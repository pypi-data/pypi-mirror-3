# -*- coding: utf-8 -*-
################################################################################

'''
'''

################################################################################
# Imports


from lxml import etree

from . import xsd


################################################################################
# Constants


ENVELOPE_NAMESPACE = 'http://www.w3.org/2003/05/soap-envelope'
BINDING_NAMESPACE = 'http://schemas.xmlsoap.org/wsdl/soap12/'
CONTENT_TYPE = 'application/soap+xml'


################################################################################
# Functions


def determin_soap_action(request):
    '''
    '''
    content_types = request.META['CONTENT_TYPE'].split(';')
    for content_type in content_types:
        if content_type.strip(' ').startswith('action='):
            action = content_type.split('=')[1]
            return action.replace('"', '')
    return None


def build_header(soapAction):
    '''
    '''
    return {'content-type': CONTENT_TYPE + 'action=%s' % soapAction}


def get_error_response(code, message):
    '''
    '''
    code = Code(Value=code)
    reason = Reason(Text=message)
    fault = Fault(Code=code, Reason=reason)
    envelope = Envelope()
    envelope.Body = Body(Fault=fault)
    return envelope.xml('Envelope', namespace=ENVELOPE_NAMESPACE,
                        elementFormDefault=xsd.ElementFormDefault.QUALIFIED)


def parse_fault_message(fault):
    '''
    '''
    return fault.Code.Value, fault.Reason.Text


################################################################################
# Classes


class Header(xsd.ComplexType):
    '''
    SOAP Envelope Header.
    '''
    pass


class Code(xsd.ComplexType):
    '''
    '''
    CLIENT = 'ns0:Sender'
    SERVER = 'ns0:Receiver'
    Value = xsd.Element(xsd.String)


class LanguageString(xsd.String):
    '''
    '''

    def render(self, parent, value, namespace, elementFormDefault):
        '''
        '''
        parent.text = self.xmlvalue(value)
        parent.set('{http://www.w3.org/XML/1998/namespace}lang', 'en')


class Reason(xsd.ComplexType):
    '''
    '''
    Text = xsd.Element(LanguageString)


class Fault(xsd.ComplexType):
    '''
    SOAP Envelope Fault.
    '''
    Code = xsd.Element(Code)
    Reason = xsd.Element(Reason)


class Body(xsd.ComplexType):
    '''
    SOAP Envelope Body.
    '''
    message = xsd.ClassNamedElement(xsd.ComplexType, minOccurs=0)
    Fault = xsd.Element(Fault, minOccurs=0)

    def content(self):
        '''
        '''
        return etree.tostring(self._xmlelement[0], pretty_print=True)


class Envelope(xsd.ComplexType):
    '''
    SOAP Envelope.
    '''
    Header = xsd.Element(Header, nillable=True)
    Body = xsd.Element(Body)

    @classmethod
    def response(cls, tagname, return_object):
        '''
        '''
        envelope = Envelope()
        envelope.Body = Body()
        envelope.Body.message = xsd.NamedType(name=tagname, value=return_object)
        return envelope.xml('Envelope', namespace=ENVELOPE_NAMESPACE,
                            elementFormDefault=xsd.ElementFormDefault.QUALIFIED)


SCHEMA = xsd.Schema(
    targetNamespace=ENVELOPE_NAMESPACE,
    elementFormDefault=xsd.ElementFormDefault.QUALIFIED,
    complexTypes=[Header, Body, Envelope, Code, Reason, Fault],
)


################################################################################
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4

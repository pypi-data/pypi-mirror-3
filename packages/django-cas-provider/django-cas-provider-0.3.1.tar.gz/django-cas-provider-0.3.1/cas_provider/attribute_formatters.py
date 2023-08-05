from lxml import etree

CAS_URI = 'http://www.yale.edu/tp/cas'
NSMAP = {'cas': CAS_URI}
CAS = '{%s}' % CAS_URI


def jasig(auth_success, attrs):
    attributes = etree.SubElement(auth_success, CAS + 'attributes')
    style = etree.SubElement(attributes, CAS + 'attraStyle')
    style.text = u'Jasig'
    for name, value in attrs.items():
        if isinstance(value, list):
            for e in value:
                element = etree.SubElement(attributes, CAS + name)
                element.text = e
        else:
            element = etree.SubElement(attributes, CAS + name)
            element.text = value


def ruby_cas(auth_success, attrs):
    style = etree.SubElement(auth_success, CAS + 'attraStyle')
    style.text = u'RubyCAS'
    for name, value in attrs.items():
        if isinstance(value, list):
            for e in value:
                element = etree.SubElement(auth_success, CAS + name)
                element.text = e
        else:
            element = etree.SubElement(auth_success, CAS + name)
            element.text = value

def name_value(auth_success, attrs):
    etree.SubElement(auth_success, CAS + 'attribute', name=u'attraStyle', value=u'Name-Value')
    for name, value in attrs.items():
        if isinstance(value, list):
            for e in value:
                etree.SubElement(auth_success, CAS + 'attribute', name=name, value=e)
        else:
            etree.SubElement(auth_success, CAS + 'attribute', name=name, value=value)

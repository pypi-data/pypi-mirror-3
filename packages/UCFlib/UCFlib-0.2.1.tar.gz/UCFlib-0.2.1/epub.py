from __future__ import unicode_literals
from xml.etree import ElementTree as ET
import ucf


NSMAP = {
    'opf': 'http://www.idpf.org/2007/opf',
    'dc': 'http://purl.org/dc/elements/1.1/',
}

for prefix in NSMAP:
    ET.register_namespace(prefix, NSMAP[prefix])


class EPub(object):
    def __init__(self):
        self.identifier
        self.title
        self.language
        




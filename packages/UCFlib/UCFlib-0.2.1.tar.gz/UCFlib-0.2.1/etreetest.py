# Test for ElementTree 1.3.0 + Py2/3 compatibility

from __future__ import unicode_literals, print_function

from xml.etree import ElementTree as ET
from io import BytesIO, StringIO
import sys


print("ElementTree {0}, Python {1.major}.{1.minor}.{1.micro}".format(
        ET.VERSION, sys.version_info))


element = ET.Element('example')

tree = ET.ElementTree(element)
tree.write(BytesIO(), xml_declaration=True, encoding='utf-8')

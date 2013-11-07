#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""feedback.py
"""
__all__ = ('to_xml',)
from xml.etree import ElementTree as et

def to_xml(items):
    """
    Convert a list of items to XML and return
    it as a string.
    """
    items_node = et.Element(u'items')

    for item_attr, item_elements in items:
        item_node = et.SubElement(items_node, 'item', attrib=item_attr)
        for el_name, el_val in item_elements.iteritems():
            if isinstance(el_val, (tuple, list)):
                attrib, el_val = el_val
            else:
                attrib = {}

            el_node = et.SubElement(item_node, el_name, attrib=attrib)
            el_node.text = el_val

    return et.tostring(items_node)

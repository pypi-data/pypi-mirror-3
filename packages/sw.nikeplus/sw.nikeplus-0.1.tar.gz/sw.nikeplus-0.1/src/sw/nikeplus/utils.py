# -*- coding: utf-8 -*-
# Copyright (c) 2012 Sebastian Wehrmann
# See also LICENSE.txt

import lxml.etree


def xml2json(xml_string):
    if not xml_string:
        return
    xml = lxml.etree.fromstring(xml_string)

    def _unique_ids(elements):
        ids = [e.tag for e in elements]
        return len(ids) == len(set(ids))

    def _parse(element):
        children = element.getchildren()
        if children:
            if _unique_ids(children):
                result = {}
                for child in children:
                    result[child.tag] = _parse(child)
                for id, value in element.attrib.items():
                    result[id] = value
                return result
            else:
                result = []
                for child in children:
                    result.append(_parse(child))
                return result
        else:
            return element.text

    return _parse(xml)

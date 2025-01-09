# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ZSConvert
                        A tool for converting XSD to other formats
                        -------------------
        begin           : 2024-12-24
        git sha         : $Format:%H$
        copyright       : (C) 2024 by https://github.com/kancve
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from lxml import etree
from zs_element import ZSElement


class ZSConvert:
    xsns = {'xs': 'http://www.w3.org/2001/XMLSchema'}

    def __init__(self, xsd='OpenDRIVE.xsd') -> None:
        self.xs_sechema = etree.parse(xsd)

    def to_zserio(self) -> list:
        zs_elements = list()
        # Using xpath to query specific elements
        simple_types = self.xs_sechema.xpath(
            '//xs:simpleType', namespaces=ZSConvert.xsns)
        complex_types = self.xs_sechema.xpath(
            '//xs:complexType', namespaces=ZSConvert.xsns)

        # xs:simpleType
        for simple_type in simple_types:
            zs_element = self.simple_to_zs(simple_type)
            zs_elements.append(zs_element)

        # xs:complexType
        for complex_type in complex_types:
            zs_element = self.complex_to_zs(complex_type)
            zs_elements.append(zs_element)

        return zs_elements

    def get_comments(self, xs_element) -> str:
        # Get comments for element
        annotation = xs_element.find(
            'xs:annotation', namespaces=ZSConvert.xsns)
        if annotation is not None:
            documentation = annotation.find(
                'xs:documentation', namespaces=ZSConvert.xsns)
            if documentation is not None:
                return documentation.text
        return None

    def simple_to_zs(self, xs_simple_type) -> ZSElement:
        zs_element = ZSElement(
            comment=self.get_comments(xs_simple_type),
            name=xs_simple_type.get('name'),
            type=xs_simple_type.get('name'))

        # Attributes
        restriction = xs_simple_type.find(
            'xs:restriction', namespaces=ZSConvert.xsns)
        if restriction is not None:
            # enumerations
            enumerations = restriction.findall(
                'xs:enumeration', namespaces=ZSConvert.xsns)
            for enumeration in enumerations:
                zs_element.append(ZSElement(
                    comment=self.get_comments(enumeration),
                    name=enumeration.get('value').replace(' ', '_'),
                    type=restriction.get('base').replace('xs:', '')))

        return zs_element

    def complex_to_zs(self, xs_complex_type) -> ZSElement:
        name = xs_complex_type.get('name')
        if name is None:
            parent = xs_complex_type.getparent()
            if parent is not None:
                name = parent.get('name')
        name = name or 'undefined'

        zs_element = ZSElement(
            comment=self.get_comments(xs_complex_type),
            name=name,
            type=name)

        complex_type = xs_complex_type
        content = xs_complex_type.find(
            'xs:complexContent', namespaces=ZSConvert.xsns)
        if content is not None:
            complex_type = content
            extension = content.find('xs:extension', namespaces=ZSConvert.xsns)
            if extension is not None:
                complex_type = extension
                # base
                if extension.get('base') not in ['_OpenDriveElement']:
                    zs_element.append(ZSElement(
                        comment=None,
                        name='base',
                        type=extension.get('base')))

        # Attributes
        attributes = complex_type.findall(
            'xs:attribute', namespaces=ZSConvert.xsns)
        for attribute in attributes:
            zs_element.append(ZSElement(
                comment=self.get_comments(attribute),
                name=attribute.get('name'),
                type=attribute.get('type').replace('xs:', ''),
                use=attribute.get('use')))
        # Sequence
        sequence = complex_type.find('xs:sequence', namespaces=ZSConvert.xsns)
        if sequence is not None:
            elements = sequence.findall(
                'xs:element', namespaces=ZSConvert.xsns)
            for element in elements:
                zs_element.append(ZSElement(
                    comment=self.get_comments(element),
                    name=element.get('name'),
                    type=element.get('type').replace('xs:', ''),
                    use=(element.get('minOccurs') or '') + '..' + (element.get('maxOccurs') or '')))

                # Alternative ?
                alternatives = element.findall(
                    'xs:alternative', namespaces=ZSConvert.xsns)
                if alternatives is not None:
                    for alternative in alternatives:
                        zs_element.append(ZSElement(
                            comment=self.get_comments(alternative),
                            name=alternative.get('type'),
                            type=alternative.get('type').replace('xs:', '')))

        # choice
        choice = complex_type.find('xs:choice', namespaces=ZSConvert.xsns)
        if choice is not None:
            elements = choice.findall(
                'xs:element', namespaces=ZSConvert.xsns)
            for element in elements:
                zs_element.append(ZSElement(
                    comment=self.get_comments(element),
                    name=element.get('name'),
                    type=element.get('type').replace('xs:', ''),
                    use=(element.get('minOccurs') or '') + '..' + (element.get('maxOccurs') or '')))

        return zs_element

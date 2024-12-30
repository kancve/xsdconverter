# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ZSElement
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


class ZSElement:
    # When the keyword or operator named zs needs to be changed or replaced
    keywords = ['subtype', 'default', 'explicit', 'rule', 'true', 'false']
    operators = {'+': 'add', '-': 'reduce', '%': 'percent',
                 'm/s': 'm_divide_s', 'km/h': 'km_divide_h'}

    def __init__(self,
                 comment: str = str(),
                 name: str = str(),
                 type: str = str(),
                 use: str = str()
                 ) -> None:
        self.comment = comment
        self.name = name
        self.type = type
        self.use = use
        self.children: list[ZSElement] = list()

    def __lt__(self, other) -> bool:
        return self.name < other.name

    def append(self, child) -> None:
        self.children.append(child)

    def text(self, ignorecomments=False, sortchildren=False) -> str:
        text = str()
        # comment
        if (not ignorecomments) and (self.comment is not None):
            text = text + '/** ' + self.comment + ' */\n'
        # name
        text = text + 'struct ' + self.name + '\n{\n'
        # children
        if sortchildren:
            self.children.sort()
        for child in self.children:
            # comment
            if (not ignorecomments) and (child.comment is not None):
                text = text + '    /** ' + child.comment + ' */\n'
            # name
            replace_name = child.name
            if (replace_name in ZSElement.keywords) or replace_name[0].isnumeric():
                replace_name = '_' + replace_name
            elif replace_name in ZSElement.operators:
                replace_name = ZSElement.operators[replace_name]

            text = text + '    ' + child.type + ' ' + replace_name + ';\n'
        # close
        text += '};\n\n'
        return text

    def to_dict(self) -> dict:
        result = {
            'comment': self.comment,
            'name': self.name,
            'type': self.type,
            'use': self.use,
            'children': list()
        }
        for child in self.children:
            result['children'].append({
                'comment': child.comment,
                'name': child.name,
                'type': child.type,
                'use': child.use,
                'children': list()
            })

        return result

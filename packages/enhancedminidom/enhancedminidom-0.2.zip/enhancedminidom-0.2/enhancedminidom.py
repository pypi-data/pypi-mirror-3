# -*- coding: utf-8 -*-

from xml.dom import minidom

from collections import OrderedDict


def enhance_minidom():
    if not hasattr(minidom, 'SORTEDATTRIBUTES'):
        minidom.SORTEDATTRIBUTES = False

    def _get_elements_by_attributeName_helper(node, attr_name, tag_name=None):
        #print node
        elements = []
        sub_elements = []
        if hasattr(node, 'hasAttribute') and node.hasAttribute(attr_name) and node not in elements:
            elements.append(node)
        if hasattr(node, 'childNodes'):
            sub_elements = node.childNodes
        elif isinstance(node, NodeList):
            sub_elements = node
        for sub_element in sub_elements:
            newelts = _get_elements_by_attributeName_helper(sub_element, attr_name, tag_name)
            if len(newelts):
                elements.extend(newelts)
        if tag_name:
            for index, element in enumerate(elements):
                if hasattr(element, 'tagName') and element.tagName != tag_name:
                    elements.pop(index)
                elif not hasattr(element, 'tagName'):
                    elements.pop(index)
        return elements
        if not hasattr(minidom, '_get_elements_by_attributeName_helper'):
            minidom._get_elements_by_attributeName_helper = _get_elements_by_attributeName_helper


    if not hasattr(minidom.Element, 'Parent'):
        OrigElement = minidom.Element

        class EnhancedElement(OrigElement):
            Parent = OrigElement
            def __init__(self, *args, **kwargs):
                self.Parent.__init__(self, *args, **kwargs)
                self._attrs = OrderedDict()
                self._attrsNS = OrderedDict()

            def writexml(self, writer, indent="", addindent="", newl=""):
                # indent = current indentation
                # addindent = indentation to add to higher levels
                # newl = newline string
                writer.write(indent+"<" + self.tagName)

                attrs = self._get_attributes()
                a_names = attrs.keys()
                if hasattr(minidom, 'SORTEDATTRIBUTES') and minidom.SORTEDATTRIBUTES:
                    a_names.sort()

                for a_name in a_names:
                    writer.write(" %s=\"" % a_name)
                    minidom._write_data(writer, attrs[a_name].value)
                    writer.write("\"")
                if self.childNodes:
                    writer.write(">%s"%(newl))
                    for node in self.childNodes:
                        node.writexml(writer,indent+addindent,addindent,newl)
                    writer.write("%s</%s>%s" % (indent,self.tagName,newl))
                else:
                    writer.write("/>%s"%(newl))

            def getElementsByAttributeName(self, name, tag_name=None):
                return _get_elements_by_attributeName_helper(self, name, tag_name)

        minidom.Element = EnhancedElement


    if not hasattr(minidom.Document, 'Parent'):
        OrigDocument = minidom.Document
        class EnhancedDocument(OrigDocument):
            Parent = OrigDocument
            def getElementsByAttributeName(self, name, tag_name=None):
                return _get_elements_by_attributeName_helper(self, name, tag_name)
        minidom.Document = EnhancedDocument


enhance_minidom()

"""
                   THE BOX MODEL
┌╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶┐
╎                      margin                       ╎
╎    ┏╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺┓    ╎
╎    ╹  (x, y)         border                  ╹    ╎
╎    ╹    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓    ╹    ╎
╎    ╹    ┃           padding             ┃ h  ╹    ╎
╎    ╹    ┃    ┌─────────────────────┐    ┃ e  ╹    ╎
╎    ╹    ┃    │                     │    ┃ i  ╹    ╎
╎    ╹    ┃    │      content        │    ┃ g  ╹    ╎
╎    ╹    ┃    │                     │    ┃ h  ╹    ╎
╎    ╹    ┃    └─────────────────────┘    ┃ t  ╹    ╎
╎    ╹    ┃            width              ┃    ╹    ╎
╎    ╹    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛    ╹    ╎
╎    ╹                                         ╹    ╎
╎    ┗╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺┛    ╎
╎                                                   ╎
└╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶┘
"""
from __future__ import annotations
from typing import Tuple, List, Dict, Type
from lxml import etree
import skia

if __name__ == '__main__':
    from default_stylesheet import *
else:
    from .default_stylesheet import *

# noinspection PyProtectedMember
etree_node = etree._Element


class LayoutBox:
    """
    All boxes in the layout tree inherit from this class.
    """

    # noinspection PyProtectedMember
    def __init__(self, dom_node: etree_node | None, style: Dict | None = None, parent_box=None, last_sibling_box=None):
        self.dom_node = dom_node
        self.style = style

        self.parent_box: LayoutBox | None = parent_box
        self.last_sibling_box: LayoutBox | None = last_sibling_box
        self.children: List[LayoutBox] = []

        self.main_box = Rectangle()
        self.margin = BoxProperty(self, "margin")
        self.border = BoxProperty(self, "border")
        self.padding = BoxProperty(self, "padding")

        self.init_box()

    def init_box(self):
        # will be defined by child classes due to dependency on box type
        pass

    @property
    def has_parent(self):
        return not (self.parent_box is None)

    @property
    def has_last_sibling(self):
        return not (self.last_sibling_box is None)

    def layout(self):
        # will be defined by child classes due to dependency on box type
        pass


class Rectangle:
    def __init__(self):
        self.x1 = 0
        self.y1 = 0
        self.width = 0
        self.height = 0

    @property
    def x2(self) -> int:
        return self.x1 + self.width

    @property
    def y2(self) -> int:
        return self.y1 + self.width

    @property
    def box_dimensions(self) -> Dimensions:
        dimensions = Dimensions(self.x1, self.y1, self.x2, self.y2, self.width, self.height)
        return dimensions


class BoxProperty:
    def __init__(self, parent_box: LayoutBox, property_name: str):
        self.parent_box = parent_box
        self.main_box: Rectangle = parent_box.main_box

        self.property_name = property_name
        # Since padding is the only one where the area is inside the main box
        self.sign = 1 if property_name == "padding" else -1

        self.top = 0
        self.right = 0
        self.bottom = 0
        self.left = 0

        self.color = None
        self.set_properties_from_style()

    def set_properties_from_style(self):
        style = self.parent_box.style
        self.top = style.get(self.property_name + "-top", 0)
        self.right = style.get(self.property_name + "-right", 0)
        self.bottom = style.get(self.property_name + "-bottom", 0)
        self.left = style.get(self.property_name + "-left", 0)

        self.color = style.get("border-color")

    @property
    def x1(self) -> int:
        return self.main_box.x1 + (self.sign * self.left)

    @property
    def y1(self) -> int:
        return self.main_box.y1 + (self.sign * self.top)

    @property
    def x2(self) -> int:
        return self.main_box.x2 + (-self.sign * self.right)

    @property
    def y2(self) -> int:
        return self.main_box.y2 + (-self.sign * self.bottom)

    @property
    def width(self) -> int:
        return self.x2 - self.x1

    @property
    def height(self) -> int:
        return self.y2 - self.y1

    @property
    def box_dimensions(self) -> Dimensions:
        x2, y2 = self.x2, self.y2
        width, height = x2 - self.x1, y2 - self.x2
        dimensions = Dimensions(self.x1, self.y1, x2, y2, width, height)
        return dimensions


class Dimensions:
    def __init__(self, x1, y1, x2, y2, width, height):
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        self.width, self.height = width, height


class BlockLayoutBox(LayoutBox):
    def init_box(self):
        if self.has_parent:
            self.inherit_parent_dimensions()

        if self.has_last_sibling:
            self.position_after_last_sibling()

    def inherit_parent_dimensions(self):
        parent_dimensions = self.parent_box.padding.box_dimensions
        self.main_box.x1 = parent_dimensions.x1 + self.margin.left
        self.main_box.y1 = parent_dimensions.y1 + self.margin.top
        self.main_box.width = parent_dimensions.x2 - self.margin.right

    def position_after_last_sibling(self):
        last_sibling_dimensions = self.last_sibling_box.margin.box_dimensions
        self.main_box.y1 = last_sibling_dimensions.y2

    def layout(self):
        first_text = self.dom_node.text
        self.children.append(TextLayoutBox(first_text, self))

        last_sibling: LayoutBox | None = None
        for child_dom_node in self.dom_node.iterchildren():  # type: etree_node
            layout_box = self.handle_child(child_dom_node, last_sibling)
            last_sibling = layout_box

    def handle_child(self, child_dom_node: etree_node, last_sibling: LayoutBox) -> LayoutBox:
        layout = get_node_layout_and_style(child_dom_node)

        style = STYLESHEET.get(child_dom_node.tag)
        layout_box = layout(child_dom_node, style, self, last_sibling)
        layout_box.layout()
        self.children.append(layout_box)
        self.main_box.height += layout_box.main_box.box_dimensions.height
        y1 = layout_box.main_box.box_dimensions.y1

        text_after_current_node = child_dom_node.tail
        if text_after_current_node:
            layout_box = TextLayoutBox(text_after_current_node, self, layout_box)
            self.children.append(layout_box)
            if layout is BlockLayoutBox:
                self.main_box.height += layout_box.main_box.box_dimensions.height
            else:
                new_y1 = layout_box.main_box.box_dimensions.y1
                if y1 != new_y1:
                    self.main_box.height += layout_box.main_box.box_dimensions.height

        return layout_box


class InlineLayoutBox(LayoutBox):
    def init_box(self):
        if not self.has_last_sibling:
            self.inherit_parent_dimensions()
            return

        if isinstance(self.last_sibling_box, BlockLayoutBox):
            self.position_after_block_sibling()
        else:
            self.position_after_inline_sibling()

    def inherit_parent_dimensions(self):
        parent_dimensions = self.parent_box.padding.box_dimensions
        self.main_box.x1 = parent_dimensions.x1 + self.margin.left
        self.main_box.y1 = parent_dimensions.y1 + self.margin.top

    def position_after_block_sibling(self):
        parent_dimensions = self.parent_box.padding.box_dimensions
        last_sibling_dimensions = self.last_sibling_box.margin.box_dimensions
        self.main_box.x1 = parent_dimensions.x1 + self.margin.left
        self.main_box.y1 = last_sibling_dimensions.y2 + self.margin.top

    def position_after_inline_sibling(self):
        last_sibling_dimensions = self.last_sibling_box.margin.box_dimensions
        self.main_box.x1 = last_sibling_dimensions.x2 + self.margin.left
        self.main_box.y1 = last_sibling_dimensions.y1  # margin top and bottom does not work on inline elements

    def layout(self):
        first_text = self.dom_node.text
        self.children.append(TextLayoutBox(first_text, self))

        last_sibling: LayoutBox | None = None
        for child_dom_node in self.dom_node.iterchildren():  # type: etree_node
            layout_box = self.handle_child(child_dom_node, last_sibling)
            last_sibling = layout_box

    def handle_child(self, child_dom_node: etree_node, last_sibling: LayoutBox) -> LayoutBox:
        layout = get_node_layout_and_style(child_dom_node)

        if layout is BlockLayoutBox:
            layout_box = self.handle_misnested_block_child(child_dom_node, last_sibling)
        else:
            layout_box = self.handle_inline_child(child_dom_node, last_sibling)

        return layout_box

    def handle_misnested_block_child(self, child_dom_node, last_sibling):
        raise NotImplementedError("Block box as child of inline parent is not implemented at the moment.")

    def handle_inline_child(self, child_dom_node: etree_node, last_sibling: LayoutBox) -> LayoutBox:
        style = STYLESHEET.get(child_dom_node.tag)
        layout_box = InlineLayoutBox(child_dom_node, style, self, last_sibling)
        layout_box.layout()
        height = layout_box.main_box.box_dimensions.height
        y1 = layout_box.main_box.box_dimensions.y1
        self.children.append(layout_box)

        self.main_box.width = max(layout_box.margin.box_dimensions.width, self.main_box.width)

        text_after_current_node = child_dom_node.tail
        if text_after_current_node:
            layout_box = TextLayoutBox(text_after_current_node, self, layout_box)
            new_y1 = layout_box.main_box.box_dimensions.height
            if y1 != new_y1:
                height += layout_box.main_box.box_dimensions.height
            self.children.append(layout_box)

        # UPDATE SELF HEIGHT (sum of children heights)
        self.main_box.height += height
        # UPDATE SELF WIDTH (equal to the width of the child with the greatest width)
        self.main_box.width = max(layout_box.margin.box_dimensions.width, self.main_box.width)

        return layout_box


class TextLayoutBox(LayoutBox):
    DEFAULT_FONT_SIZE = 18
    DEFAULT_TEXT_COLOR = skia.ColorBLACK
    DEFAULT_FONT = skia.Font(None, size=DEFAULT_FONT_SIZE)
    DEFAULT_LINE_HEIGHT = DEFAULT_FONT.getMetrics().fDescent - DEFAULT_FONT.getMetrics().fAscent

    def __init__(self, text: str, parent_box=None, last_sibling_box=None, font_styles: Tuple[str] = ()):
        super().__init__(None, None, parent_box, last_sibling_box)
        self.text = text.split(" ")
        self.text_nodes: List[TextNode] = []
        self.font_styles = font_styles
        self.init_box()

    def init_cursor(self):
        parent_box = self.parent_box.padding.box_dimensions
        if self.has_last_sibling:
            last_sibling = self.last_sibling_box
            if isinstance(last_sibling, BlockLayoutBox):
                cursor_x = parent_box.x1
                cursor_y = parent_box.y1
            else:
                cursor_x = last_sibling.margin.box_dimensions.x2
                cursor_y = last_sibling.main_box.y1
        else:
            cursor_x = parent_box.x1
            cursor_y = parent_box.y1

        return cursor_x, cursor_y

    def init_box(self):
        max_x_pos = self.parent_box.padding.box_dimensions.x2
        cursor_x, cursor_y = self.init_cursor()

        measuring_text_width = self.DEFAULT_FONT.measureText
        line_height = self.DEFAULT_LINE_HEIGHT
        for word in self.text:
            if cursor_x >= max_x_pos:
                cursor_y += line_height

            # noinspection PyArgumentList
            width = measuring_text_width(word)
            text_node = TextNode(word, width, line_height)
            text_node.bounding_box.x1 = cursor_x
            text_node.bounding_box.y1 = cursor_y

            self.text_nodes.append(text_node)
            cursor_x += width

        self.main_box = self.text_nodes[-1].bounding_box


class TextNode:
    def __init__(self, text: str, width: int, line_height: int):
        self.text = text
        self.bounding_box = Rectangle()
        self.bounding_box.width = width
        self.bounding_box.height = line_height


def get_node_layout_and_style(node) -> Type[BlockLayoutBox] | Type[InlineLayoutBox]:
    tag_name = node.tag
    if tag_name in BLOCK_ELEMENTS:
        layout = BlockLayoutBox
    else:
        layout = InlineLayoutBox

    return layout

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


class Box:
    def __init__(self):
        # POSITION
        self.x, self.y = 0, 0

        # DIMENSIONS
        self.width, self.height = 0, 0

        # BOX PROPERTIES
        self.margin = Margin(self)
        self.border = Border(self)
        self.padding = Padding(self)

    @property
    def content_box(self):
        return self.padding.get_box()

    @property
    def full_box(self):
        return self.margin.get_box()


class BoxProperty:
    """
    The base class for basic box properties.
    """

    def __init__(self, parent_box: Box, top=0, right=0, bottom=0, left=0):
        self.parent_box = parent_box

        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left

    def get_box(self):
        x1 = self.parent_box.x - self.right
        y1 = self.parent_box.y - self.top
        x2 = self.parent_box.x + self.parent_box.width + self.right
        y2 = self.parent_box.y + self.parent_box.height + self.bottom
        return x1, y1, x2, y2

    def __repr__(self):
        class_name = self.__class__.__name__
        return class_name + f"({self.top}, {self.right}, {self.bottom}, {self.right})"


class Margin(BoxProperty):
    pass


class Border(BoxProperty):
    def __init__(self, parent_box: Box, top=0, right=0, bottom=0, left=0, stroke_color="transparent"):
        super().__init__(parent_box, top, right, bottom, left)
        self.stroke_color = stroke_color


class Padding(BoxProperty):
    def get_box(self):
        x1 = self.parent_box.x + self.right
        x2 = self.parent_box.x + self.parent_box.width - self.right
        y1 = self.parent_box.y + self.top
        y2 = self.parent_box.y + self.parent_box.height - self.bottom

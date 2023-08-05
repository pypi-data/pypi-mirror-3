# -*- coding: utf-8 -*-
#  Copyright 2011 Takeshi KOMIYA
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from blockdiag.noderenderer import NodeShape
from blockdiag.noderenderer import install_renderer
from blockdiag.utils.XY import XY


class BeginPoint(NodeShape):
    def __init__(self, node, metrix=None):
        super(BeginPoint, self).__init__(node, metrix)

        m = metrix.cell(node)

        self.radius = metrix.cellSize
        self.center = m.center()
        self.textbox = [m.top().x, m.top().y, m.right().x, m.right().y]
        self.textalign = 'left'
        self.connectors = [XY(self.center.x, self.center.y - self.radius),
                           XY(self.center.x + self.radius, self.center.y),
                           XY(self.center.x, self.center.y + self.radius),
                           XY(self.center.x - self.radius, self.center.y)]

    def render_shape(self, drawer, format, **kwargs):
        outline = kwargs.get('outline')
        fill = kwargs.get('fill')

        # draw outline
        r = self.radius
        box = (self.center.x - r, self.center.y - r,
               self.center.x + r, self.center.y + r)
        if kwargs.get('shadow'):
            box = self.shift_shadow(box)
            drawer.ellipse(box, fill=fill, outline=fill, filter='transp-blur')
        else:
            if self.node.color == self.node.basecolor:
                color = outline
            else:
                color = self.node.color

            drawer.ellipse(box, fill=color, outline=outline,
                           style=self.node.style)


def setup(self):
    install_renderer('beginpoint', BeginPoint)

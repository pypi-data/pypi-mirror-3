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


class LoopOut(NodeShape):
    def __init__(self, node, metrix=None):
        super(LoopOut, self).__init__(node, metrix)

        m = self.metrix.cell(self.node)
        xdiff = self.metrix.nodeWidth / 4
        ydiff = self.metrix.nodeHeight / 4

        self.textbox = (m.topLeft().x, m.topLeft().y,
                        m.bottomRight().x, m.bottomRight().y - ydiff)

    def render_shape(self, drawer, format, **kwargs):
        outline = kwargs.get('outline')
        fill = kwargs.get('fill')

        m = self.metrix.cell(self.node)
        xdiff = self.metrix.nodeWidth / 4
        ydiff = self.metrix.nodeHeight / 4

        shape = [XY(m.topLeft().x, m.topLeft().y),
                XY(m.topRight().x, m.topRight().y),
                XY(m.bottomRight().x, m.bottomRight().y - ydiff),
                XY(m.bottomRight().x - xdiff, m.bottomRight().y),
                XY(m.bottomLeft().x + xdiff, m.bottomLeft().y),
                XY(m.bottomLeft().x, m.bottomLeft().y - ydiff),
                XY(m.topLeft().x, m.topLeft().y)]

        # draw outline
        if kwargs.get('shadow'):
            shape = self.shift_shadow(shape)
            drawer.polygon(shape, fill=fill, outline=fill,
                           filter='transp-blur')
        elif self.node.background:
            drawer.polygon(shape, fill=self.node.color,
                             outline=self.node.color)
            drawer.loadImage(self.node.background, self.textbox)
            drawer.polygon(shape, fill="none", outline=outline,
                           style=self.node.style)
        else:
            drawer.polygon(shape, fill=self.node.color, outline=outline,
                           style=self.node.style)


def setup(self):
    install_renderer('flowchart.loopout', LoopOut)

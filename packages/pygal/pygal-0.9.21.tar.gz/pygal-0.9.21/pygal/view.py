# -*- coding: utf-8 -*-
# This file is part of pygal
#
# A python svg graph plotting library
# Copyright © 2012 Kozea
#
# This library is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with pygal. If not, see <http://www.gnu.org/licenses/>.
from __future__ import division
from math import sin, cos, log10


class Margin(object):
    def __init__(self, top, right, bottom, left):
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left

    @property
    def x(self):
        return self.left + self.right

    @property
    def y(self):
        return self.top + self.bottom


class Box(object):
    _margin = .02

    def __init__(self):
        self.xmin = self.ymin = 0
        self.xmax = self.ymax = 1

    @property
    def width(self):
        return self.xmax - self.xmin

    @property
    def height(self):
        return self.ymax - self.ymin

    def swap(self):
        self.xmin, self.ymin = self.ymin, self.xmin
        self.xmax, self.ymax = self.ymax, self.xmax

    def fix(self, with_margin=True):
        if not self.width:
            self.xmax = self.xmin + 1
        if not self.height:
            self.ymin -= .5
            self.ymax = self.ymin + 1
        xmargin = self._margin * self.width
        self.xmin -= xmargin
        self.xmax += xmargin
        if with_margin:
            ymargin = self._margin * self.height
            self.ymin -= ymargin
            self.ymax += ymargin


class View(object):
    def __init__(self, width, height, box):
        self.width = width
        self.height = height
        self.box = box
        self.box.fix()

    def x(self, x):
        if x == None:
            return None
        return self.width * (x - self.box.xmin) / self.box.width

    def y(self, y):
        if y == None:
            return None
        return (self.height - self.height *
                (y - self.box.ymin) / self.box.height)

    def __call__(self, xy):
        x, y = xy
        return (self.x(x), self.y(y))


class PolarView(View):
    def __call__(self, rhotheta):
        if None in rhotheta:
            return None, None
        rho, theta = rhotheta
        rho = max(rho, 0)
        return super(PolarView, self).__call__(
            (rho * cos(theta), rho * sin(theta)))


class LogView(View):
    def __init__(self, width, height, box):
        self.width = width
        self.height = height
        self.box = box
        self.ymin = self.box.ymin
        self.ymax = self.box.ymax
        self.log10_ymax = log10(self.box.ymax)
        self.log10_ymin = log10(self.box.ymin)
        self.box.fix(False)

    def y(self, y):
        if y == None or y <= 0:
            return None
        return (self.height - self.height *
                (log10(y) - self.log10_ymin)
                / (self.log10_ymax - self.log10_ymin))

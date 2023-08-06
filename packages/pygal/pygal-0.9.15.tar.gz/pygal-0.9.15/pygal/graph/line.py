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
from pygal.graph.graph import Graph
from pygal.util import cached_property
from pygal.interpolate import interpolation
from math import isnan


class Line(Graph):
    """Line graph"""

    def _get_value(self, values, i):
        return self.format(values[i][1])

    @cached_property
    def _values(self):
        if self.interpolate:
            return [val[1]
                    for serie in self.series
                    for val in serie.interpolated
                    if val[1] != None]
        else:
            return  [val[1]
                     for serie in self.series
                     for val in serie.points
                    if val[1] != None]

    def _fill(self, values):
        zero = self.view.y(min(max(self.zero, self._box.ymin), self._box.ymax))
        return ([(values[0][0], zero)] +
                values +
                [(values[-1][0], zero)])

    def line(self, serie_node, serie):
        view_values = map(self.view, serie.points)
        if self.show_dots:
            for i, (x, y) in enumerate(view_values):
                if None in (x, y):
                    continue
                dots = self.svg.node(serie_node['overlay'], class_="dots")
                val = self._get_value(serie.points, i)
                self.svg.node(dots, 'circle', cx=x, cy=y, r=2.5,
                              class_='dot reactive tooltip-trigger')
                self.svg.node(dots, 'desc', class_="value").text = val
                self.svg.node(dots, 'desc', class_="x").text = str(x)
                self.svg.node(dots, 'desc', class_="y").text = str(y)
                if self.print_values:
                    self.svg.node(
                        serie_node['text_overlay'], 'text',
                        x=x + self.value_font_size,
                        y=y + self.value_font_size,
                    ).text = val

        if self.stroke:
            if self.interpolate:
                view_values = map(self.view, serie.interpolated)
            if self.fill:
                view_values = self._fill(view_values)
            self.svg.line(
                serie_node['plot'], view_values,
                class_='line reactive' + (' nofill' if not self.fill else ''))

    def _compute(self):
        self._x_pos = [x / float(self._len - 1) for x in range(self._len)
        ] if self._len != 1 else [.5]  # Center if only one value
        for serie in self.series:
            if not hasattr(serie, 'points'):
                serie.points = [
                    (self._x_pos[i], v)
                    for i, v in enumerate(serie.values)]
                if self.interpolate:
                    interpolate = interpolation(
                        self._x_pos, serie.values, kind=self.interpolate)
                    p = float(self.interpolation_precision)
                    serie.interpolated = [
                        (x / p, float(interpolate(x / p)))
                        for x in range(int(p + 1))
                        if not isnan(float(interpolate(x / p)))]
        if self.include_x_axis:
            self._box.ymin = min(min(self._values), 0)
            self._box.ymax = max(max(self._values), 0)
        else:
            self._box.ymin = min(self._values)
            self._box.ymax = max(self._values)

        self._y_pos = self._pos(self._box.ymin, self._box.ymax, self.y_scale
        ) if not self.y_labels else map(int, self.y_labels)

        self._x_labels = self.x_labels and zip(self.x_labels, self._x_pos)
        self._y_labels = zip(map(self.format, self._y_pos), self._y_pos)

    def _plot(self):
        for serie in self.series:
            self.line(self._serie(serie.index), serie)

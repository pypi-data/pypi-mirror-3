# This file is part of wwchartlib
# Copyright (C) 2011 Benon Technologies Pty Ltd
#
# wwchartlib is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Pie chart widget.

Positive angles are counter-clockwise.  Angle of zero is the 3 o'clock
position.
"""

from __future__ import division

import itertools
import math
import numbers

from PySide.QtCore import *
from PySide.QtGui import *

from . import chart


def fraction_to_angle(fraction):
    """Convert a fraction to an angle (in Qt terms).

    Qt understands angels in 16ths-of-a-degree (i.e., one revolution is
    5760).
    """
    return fraction * 360 * 16


def angle_to_fraction(angle):
    """Convert an angle (in Qt terms) to a fraction."""
    return angle / 16 / 360


def theta_to_angle(theta):
    """Convert an angle in radians to an angle in Qt terms."""
    return theta * 360 / (2 * math.pi) * 16


def angle_to_theta(angle):
    """Convert an angle in Qt terms to radians."""
    return angle / 16 / 360 * (2 * math.pi)


def opposite_angle(angle):
    """Determine the opposite angle to the angle given, in Qt terms."""
    angle += 180 * 16
    if angle >= 360 * 16:
        angle -= 360 * 16
    return angle


class PieChartItem(chart.ChartItem):
    def __init__(self, fraction=None, **kwargs):
        """Initialise the pie chart item.

        fraction:
          The fraction of this pie chart item, in range ``0..1``.
        """
        super(PieChartItem, self).__init__(**kwargs)
        self.fraction = fraction or 0

        """The ``QColor`` of this slice.

        Initialised to ``QColor(0, 0, 0)``.  This property is only set
        by ``PieChart``, not read.  Setting it will have no effect, and
        it will be overwritten when the chart is next painted.
        """
        self.colour = QColor(0, 0, 0)


class PieChart(chart.Chart):
    """Pie chart widget.

    The default size policy is
    ``QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)``
    """
    _item_class = PieChartItem

    @classmethod
    def _check_item(cls, item):
        if not isinstance(item.fraction, numbers.Number):
            raise TypeError('PieChartItem fraction must be a Number.')
        if item.fraction < 0:
            raise ValueError('PieChartItem fraction cannot be less than 0.')
        if item.fraction > 1:
            raise ValueError('PieChartItem fraction cannot be greater than 1.')
        return super(PieChart, cls)._check_item(item)

    @classmethod
    def _check_items(cls, items):
        if sum(item.fraction for item in items) > 1:
            raise ValueError(
                'Sum of PieChartItem fractions cannot be greater than 1.'
            )
        return super(PieChart, cls)._check_items(items)

    @property
    def x(self):
        """x component of the origin of the chart."""
        return self.width() / 2

    @property
    def y(self):
        return self.height() / 2
        """y component of the origin of the chart."""

    @property
    def origin(self):
        """The origin of this pie chart, as tuple (x, y)."""
        return self.x, self.y

    @property
    def radius(self):
        """The radius of the chart.

        This is slightly less than half the shortest (cartesian)
        dimension of the widget, so that the graph does not go all the
        way to the edge.
        """
        return min(self.origin) - 5

    def __init__(self, **kwargs):
        super(PieChart, self).__init__(**kwargs)
        # get as much space as possible
        self.setSizePolicy(
            QSizePolicy.MinimumExpanding,
            QSizePolicy.MinimumExpanding
        )

    def setChartItems(self, *args, **kwargs):
        super(PieChart, self).setChartItems(*args, **kwargs)
        self._set_colours()

    def addChartItem(self, item, **kwargs):
        self._check_item(item)
        if sum((x.fraction for x in self._items), item.fraction) > 1:
            raise ValueError('PieChartItem fraction is too large.')
        super(PieChart, self).addChartItem(item, **kwargs)
        self._set_colours()

    def removeChartItem(self, *args, **kwargs):
        super(PieChart, self).removeChartItems(*args, **kwargs)
        self._set_colours()

    def _square(self):
        """Return a centered, square QRect of the maximum size possible."""
        return QRect(
            self.width() / 2 - self.radius,
            self.height() / 2 - self.radius,
            self.radius * 2,
            self.radius * 2
        )

    def _colours(self):
        """A generator of ``QColor`` objects for the pie chart.

        One colour will be generated for each slice.  In the HSV colour
        space, the colours will be evenly spaced around the cylinder
        (i.e., the hues will be as distinct as possible), with set
        saturation and value.
        """
        hue_delta = 360 / len(self._items)
        hue = 0
        for i in xrange(len(self._items)):
            yield QColor.fromHsv(int(math.floor(hue)), 191, 255)
            hue += hue_delta

    def _set_colours(self):
        """Set the colours of all items in the cart."""
        for item, colour in itertools.izip(self._items, self._colours()):
            item.colour = colour  # set the current colour

    def paintEvent(self, ev):
        """Paint the pie chart."""
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen()
        pen.setWidth(2)
        p.setPen(pen)
        rect = self._square()

        angle = 0
        for item in self._items:
            if item.fraction > 0:
                p.setBrush(QBrush(item.colour))
                span = fraction_to_angle(item.fraction)
                p.drawPie(rect, angle, span)
                angle += span


class AdjustablePieChart(PieChart):
    """A ``PieChart`` with adjustable slices."""
    _grip_radius = 5

    """Signal emitted during slice adjustment.

    The argument is the ``PieChartItem`` whose fraction changed.
    """
    itemAdjusted = Signal(PieChartItem)

    """Signal emitted when adjustment has finished."""
    finishedAdjusting = Signal()

    @property
    def radius(self):
        """The radius of the chart.

        So that the handles can be drawn properly, this is slightly less
        than half the shortest (cartesian) dimension of the widget.
        """
        return min(self.origin) - self._grip_radius * 4

    def __init__(self, maintain_total=False, **kwargs):
        """Initialise the adjustable pie chart.

        ``maintain_total``
          Whether the total of the items' fractions should be kept the
          same.  Defaults to ``False``.
        """
        super(AdjustablePieChart, self).__init__(**kwargs)
        self._gripped = []  # currently-active grips
        self._maintain_total = maintain_total

    def _polar(self, x, y):
        """Convert cartisian coordinates to polar coordinates.

        Return (radius, angle) (angle in Qt terms).
        """
        rel_x = x - self.x
        rel_y = self.y - y
        theta = math.atan2(rel_y, rel_x)
        theta = theta if theta >= 0 else theta + math.pi * 2
        return self.radius, theta_to_angle(theta)

    def _cartesian(self, angle):
        """Returns cartesian coordinates of point on graph at given angle.

        The point returned is on the circumference of the graph.

        angle
          The angle, in Qt terms.
        """
        theta = angle_to_theta(angle)
        x, y = self.radius * math.cos(theta), self.radius * math.sin(theta)
        return self.x + x, self.y - y

    def _grips(self):
        """A generator for the cartesian coordinates of all grips.

        Return ``x, y, angle, item`` where ``angle`` is the angle of the
        grip and ``item`` is the items whose grip should be found at the
        given coordinates.
        """
        angle = 0
        n = len(self._items)
        # omit last grip if we need to maintain the total fraction
        stop = n - 1 if self._maintain_total else n
        for item in self._items[:stop]:
            angle += fraction_to_angle(item.fraction)
            yield self._cartesian(angle) + (angle, item)

    def paintEvent(self, ev):
        super(AdjustablePieChart, self).paintEvent(ev)

        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen()
        pen.setWidth(2)
        p.setPen(pen)
        p.setBrush(Qt.GlobalColor.white)
        angle = 0
        for x, y, angle, item in self._grips():
            p.drawEllipse(QPointF(x, y), self._grip_radius, self._grip_radius)

    def mousePressEvent(self, ev):
        """Record the active grips."""
        self._gripped = [
            (x, y, angle, item)
            for x, y, angle, item in self._grips()
            if math.sqrt((x - ev.x()) ** 2 + (y - ev.y()) ** 2)
                < self._grip_radius
        ]

    def mouseMoveEvent(self, ev):
        if self._gripped:
            # calculate current angle of pointer
            radius, angle = self._polar(ev.x(), ev.y())

            # if there are multiple grips (in same spot), use first item
            # if the angle has decreased wrt the grip angle, otherwise
            # use the last item.
            #
            # Use angle of the last grip for the comparison: if two grips
            # are superimposed at 0 and 360 degrees, we need to be able
            # to manipulate the last item.
            if len(self._gripped) > 1 and angle < self._gripped[-1][2]:
                self._gripped = [self._gripped[0]]
            else:
                self._gripped = [self._gripped[-1]]

            gripped_item = self._gripped[0][3]
            index = self._items.index(gripped_item)
            previous_items = self._items[:index]
            next_items = self._items[index + 1:]

            # calculate some interesting angles for this item
            #
            # A slice cannot become smaller than its base_angle and
            # cannot become larger than its max_angle
            base_angle = fraction_to_angle(
                sum(item.fraction for item in previous_items)
            )
            cur_angle = base_angle + fraction_to_angle(gripped_item.fraction)
            max_angle = cur_angle + fraction_to_angle(next_items[0].fraction) \
                if next_items else fraction_to_angle(1)

            # determine whether we have grown to max or shrunk to base
            # if the angle is not between base and max
            if not base_angle <= angle <= max_angle:
                midline = opposite_angle((max_angle + base_angle) / 2)
                if midline < 180 * 16 and 0 <= angle < midline:
                    angle = max_angle
                elif midline >= 180 * 16 and midline <= angle <= 360 * 16:
                    angle = base_angle
                elif angle < base_angle:
                    angle = base_angle
                else:
                    angle = max_angle

            if angle != cur_angle:  # angle has changed
                # set the fraction of the gripped_item
                gripped_item.fraction = \
                    max(angle_to_fraction(angle - base_angle), 0)
                self.itemAdjusted.emit(gripped_item)

                # subtract new angle from next item (if there is one)
                if next_items:
                    fraction_delta = angle_to_fraction(angle - cur_angle)
                    next_items[0].fraction = \
                        max(next_items[0].fraction - fraction_delta, 0)
                    self.itemAdjusted.emit(next_items[0])

            self.update()

    def mouseReleaseEvent(self, ev):
        if self._gripped:
            # something was gripped, but now is not; emit finishedAdjusting
            self.finishedAdjusting.emit()
        self._gripped = []

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
Common classes and routines for ``wwchartlib``.
"""

from PySide.QtGui import *


class ChartItem(object):
    def __init__(self, label=None, value=None, data=None, **kwargs):
        """Initialise the chart item.

        label
          An object which will be passed as the parameter to ``unicode``
          to determine a label for the chart item.
        value
          A value that will be displayed as the value of an item (via
          ``unicode(value)`` and *may* be used by subclasses of
          ``Chart`` as the numeric value of the item in determining how
          to draw the chart.
        data
          Arbitrary data attribute; not used by ``wwchartlib``.
        """
        self.label = label
        self.value = value
        self.data = data


class Chart(QWidget):
    _item_class = ChartItem

    @classmethod
    def _check_item(cls, item):
        """Check the item, returning it if the check is successful.

        Raise an exception if the item is not valid.
        """
        if not isinstance(item, cls._item_class):
            raise TypeError('Not a {}.'.format(cls._item_class))
        return item

    @classmethod
    def _check_items(cls, items):
        """Check the item list, returning it if the check is successful.

        Raise an exception if the item list is not valid.
        """
        if any(items.count(item) > 1 for item in items):
            raise ValueError('Item appears multiple times in list.')
        return items

    def __init__(self, parent=None, items=None):
        super(Chart, self).__init__(parent=parent)
        self._items = []
        if items:
            self.setChartItems(items)

    def setChartItems(self, items):
        """Set the list of ``PieChartItem``s."""
        items = [self._check_item(item) for item in items]
        self._items = self._check_items(items)
        self.update()  # repaint

    def chartItems(self):
        """Return the list of ``ChartItem``s."""
        return self._items

    def addChartItem(self, item, index=-1):
        """Add a ``ChartItem`` to this chart.

        item
          A ``PieChartItem``
        index
          Where to insert the item.  If negative, item is inserted as
          the last item.

        The same item cannot be added to the list multiple times.
        """
        self._check_item(item)
        if item in self._items:
            raise ValueError('Item is already in the chart.')
        if self._items is None:
            self._items = [item]
        elif index < 0:
            self._items.append(item)
        else:
            self._items.insert(index, item)
        self.update()  # repaint

    def removeChartItem(self, index):
        """Remove a ``ChartItem`` from this ``PieChart``.

        index
          The index of the item to remove.  If negative, the Nth item
          from the end is removed.

        Return the removed item.
        """
        item = self._items.pop(index)
        self.update()
        return item

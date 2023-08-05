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

import unittest

from PySide.QtGui import *

import wwchartlib.chart

from . import qt


class TestChartItem(unittest.TestCase):
    def test_base(self):
        pass

    def test_init(self):
        item = wwchartlib.chart.ChartItem()
        self.assertIsNone(item.label)
        self.assertIsNone(item.value)
        self.assertIsNone(item.data)
        item = wwchartlib.chart.ChartItem(label='a', value=2, data=True)
        self.assertIs(item.label, 'a')
        self.assertIs(item.value, 2)
        self.assertTrue(item.data)


class TestChart(qt.QtTestCase):
    i1 = wwchartlib.chart.ChartItem()
    i2 = wwchartlib.chart.ChartItem()
    i3 = wwchartlib.chart.ChartItem()
    i4 = wwchartlib.chart.ChartItem()
    i5 = wwchartlib.chart.ChartItem()
    items = [i1, i2, i3]

    def setUp(self):
        self.chart = wwchartlib.chart.Chart()

    def test_base(self):
        self.assertIsInstance(self.chart, QWidget)

    def test_init(self):
        self.assertListEqual(self.chart.chartItems(), [])

        # init with items; use tuple to test list conversion
        chart = wwchartlib.chart.Chart(items=tuple(self.items))
        self.assertListEqual(chart.chartItems(), self.items)

    def test_set_items(self):
        # use tuple to test list conversion
        self.chart.setChartItems(tuple(self.items))
        self.assertListEqual(self.chart.chartItems(), self.items)

    def test_add_remove_items(self):
        # add items
        self.chart.addChartItem(self.i1)
        self.assertListEqual(self.chart.chartItems(), [self.i1])
        self.chart.addChartItem(self.i2)
        self.assertListEqual(self.chart.chartItems(), [self.i1, self.i2])
        self.chart.addChartItem(self.i3, 0)
        self.assertListEqual(
            self.chart.chartItems(),
            [self.i3, self.i1, self.i2]
        )
        self.chart.addChartItem(self.i4, -1)
        self.assertListEqual(
            self.chart.chartItems(),
            [self.i3, self.i1, self.i2, self.i4]
        )
        self.chart.addChartItem(self.i5, 8)  # should go to very end
        self.assertListEqual(
            self.chart.chartItems(),
            [self.i3, self.i1, self.i2, self.i4, self.i5]
        )

        # remove items
        with self.assertRaisesRegexp(IndexError, 'out of range'):
            self.chart.removeChartItem(5)
        self.assertIs(self.chart.removeChartItem(4), self.i5)
        self.assertListEqual(
            self.chart.chartItems(),
            [self.i3, self.i1, self.i2, self.i4]
        )
        self.assertIs(self.chart.removeChartItem(0), self.i3)
        self.assertListEqual(
            self.chart.chartItems(),
            [self.i1, self.i2, self.i4]
        )
        self.assertIs(self.chart.removeChartItem(1), self.i2)
        self.assertListEqual(self.chart.chartItems(), [self.i1, self.i4])
        self.assertIs(self.chart.removeChartItem(-1), self.i4)  # pop from end
        self.assertListEqual(self.chart.chartItems(), [self.i1])

    def test_add_same_item(self):
        self.chart.addChartItem(self.i1)
        with self.assertRaisesRegexp(
            ValueError,
            '[Ii]tem is already in .*[Cc]hart'
        ):
            self.chart.addChartItem(self.i1)

        # make sure the failure didn't affect the list of items
        self.assertListEqual(self.chart.chartItems(), [self.i1])

        # test setChartItems
        with self.assertRaisesRegexp(
            ValueError,
            '[Ii]tem appears multiple times'
        ):
            self.chart.setChartItems([self.i2, self.i2])

        # make sure the failure didn't affect the list of items
        self.assertListEqual(self.chart.chartItems(), [self.i1])

    def test_add_bogus_item(self):
        with self.assertRaisesRegexp(TypeError, '[Nn]ot a .*ChartItem.*'):
            self.chart.addChartItem(1)

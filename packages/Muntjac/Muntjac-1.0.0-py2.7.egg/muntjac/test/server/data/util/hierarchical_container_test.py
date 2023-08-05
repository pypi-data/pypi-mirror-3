# Copyright (C) 2011 Vaadin Ltd.
# Copyright (C) 2011 Richard Lincoln
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from muntjac.test.server.data.util.abstract_hierarchical_container_test \
    import AbstractHierarchicalContainerTest

from muntjac.data.container import IFilter
from muntjac.data.util.hierarchical_container import HierarchicalContainer


class TestHierarchicalContainer(AbstractHierarchicalContainerTest):

    def testBasicOperations(self):
        self._testBasicContainerOperations(HierarchicalContainer())


    def testFiltering(self):
        self._testContainerFiltering(HierarchicalContainer())


    def testSorting(self):
        self._testContainerSorting(HierarchicalContainer())


    def testOrdered(self):
        self._testContainerOrdered(HierarchicalContainer())


    def testHierarchicalSorting(self):
        self._testHierarchicalSorting(HierarchicalContainer())


    def testSortingAndFiltering(self):
        self._testContainerSortingAndFiltering(HierarchicalContainer())


    def testRemovingItemsFromFilteredContainer(self):
        container = HierarchicalContainer()
        self.initializeHierarchicalContainer(container)
        container.setIncludeParentsWhenFiltering(True)
        container.addContainerFilter(self.FULLY_QUALIFIED_NAME, 'ab',
                False, False)
        p1 = container.getParent('com.vaadin.ui.TabSheet')
        self.assertEquals('com.vaadin.ui', p1)

        container.removeItem('com.vaadin.ui.TabSheet')
        # Parent for the removed item must be null because the item is no
        # longer in the container
        p1 = container.getParent('com.vaadin.ui.TabSheet')
        self.assertIsNone(p1, 'Parent should be null, is ' + str(p1))

        container.removeAllItems()
        p1 = container.getParent('com.vaadin.terminal.gwt.client.Focusable')
        self.assertIsNone(p1, 'Parent should be null, is ' + str(p1))


    def testParentWhenRemovingFilterFromContainer(self):
        container = HierarchicalContainer()
        self.initializeHierarchicalContainer(container)
        container.setIncludeParentsWhenFiltering(True)
        container.addContainerFilter(self.FULLY_QUALIFIED_NAME, 'ab',
                False, False)
        p1 = container.getParent('com.vaadin.ui.TabSheet')
        self.assertEquals('com.vaadin.ui', p1)
        p1 = container.getParent(
                'com.vaadin.terminal.gwt.client.ui.VPopupCalendar')
        self.assertIsNone(p1)
        container.removeAllContainerFilters()
        p1 = container.getParent(
                'com.vaadin.terminal.gwt.client.ui.VPopupCalendar')
        self.assertEquals('com.vaadin.terminal.gwt.client.ui', p1)


    def testChangeParentInFilteredContainer(self):
        container = HierarchicalContainer()
        self.initializeHierarchicalContainer(container)
        container.setIncludeParentsWhenFiltering(True)
        container.addContainerFilter(self.FULLY_QUALIFIED_NAME, 'Tab',
                False, False)

        # Change parent of filtered item
        p1 = container.getParent('com.vaadin.ui.TabSheet')
        self.assertEquals('com.vaadin.ui', p1)
        container.setParent('com.vaadin.ui.TabSheet', 'com.vaadin')
        p1 = container.getParent('com.vaadin.ui.TabSheet')
        self.assertEquals('com.vaadin', p1)
        container.setParent('com.vaadin.ui.TabSheet', 'com')
        p1 = container.getParent('com.vaadin.ui.TabSheet')
        self.assertEquals('com', p1)
        container.setParent('com.vaadin.ui.TabSheet', None)
        p1 = container.getParent('com.vaadin.ui.TabSheet')
        self.assertIsNone(p1)

        # root -> non-root
        container.setParent('com.vaadin.ui.TabSheet', 'com')
        p1 = container.getParent('com.vaadin.ui.TabSheet')
        self.assertEquals('com', p1)

    def testHierarchicalFilteringWithParents(self):
        container = HierarchicalContainer()
        self.initializeHierarchicalContainer(container)
        container.setIncludeParentsWhenFiltering(True)

        # Filter by "contains ab"
        container.addContainerFilter(self.FULLY_QUALIFIED_NAME, 'ab',
                False, False)

        # 20 items match the filters and the have 8 parents that should also be
        # included
        # only one root "com" should exist
        # filtered
        expectedSize = 29
        expectedRoots = 1

        self.validateHierarchicalContainer(container, 'com',
                'com.vaadin.ui.TabSheet',
                'com.vaadin.terminal.gwt.client.Focusable',
                'blah', True, expectedSize, expectedRoots, True)

        # only include .gwt.client classes
        container.removeAllContainerFilters()
        container.addContainerFilter(self.FULLY_QUALIFIED_NAME, '.gwt.client.',
                False, False)

        packages = 6
        classes = 112

        expectedSize = packages + classes
        expectedRoots = 1

        self.validateHierarchicalContainer(container, 'com',
                'com.vaadin.terminal.gwt.client.WidgetSet',
                'com.vaadin.terminal.gwt.client.ui.VSplitPanelVertical',
                'blah', True, expectedSize, expectedRoots, True)

        # Additionally remove all without 'm' in the simple name.
        container.addContainerFilter(self.SIMPLE_NAME, 'm', False, False)

        expectedSize = 7 + 18
        expectedRoots = 1

        self.validateHierarchicalContainer(container, 'com',
            'com.vaadin.terminal.gwt.client.ui.VUriFragmentUtility',
            'com.vaadin.terminal.gwt.client.ui.layout.ChildComponentContainer',
            'blah', True, expectedSize, expectedRoots, True)


    def testRemoveLastChild(self):
        c = HierarchicalContainer()

        c.addItem('root')
        self.assertEquals(False, c.hasChildren('root'))

        c.addItem('child')
        c.setParent('child', 'root')
        self.assertEquals(True, c.hasChildren('root'))

        c.removeItem('child')
        self.assertFalse(c.containsId('child'))
        self.assertIsNone(c.getChildren('root'))
        self.assertIsNone(c.getChildren('child'))
        self.assertFalse(c.hasChildren('child'))
        self.assertFalse(c.hasChildren('root'))


    def testRemoveLastChildFromFiltered(self):
        c = HierarchicalContainer()

        c.addItem('root')
        self.assertEquals(False, c.hasChildren('root'))

        c.addItem('child')
        c.setParent('child', 'root')
        self.assertEquals(True, c.hasChildren('root'))

        # Dummy filter that does not remove any items
        class DummyFilter(IFilter):

            def passesFilter(self, itemId, item):
                return True

            def appliesToProperty(self, propertyId):
                return True

        c.addContainerFilter(DummyFilter())
        c.removeItem('child')

        self.assertFalse(c.containsId('child'))
        self.assertIsNone(c.getChildren('root'))
        self.assertIsNone(c.getChildren('child'))
        self.assertFalse(c.hasChildren('child'))
        self.assertFalse(c.hasChildren('root'))


    def testHierarchicalFilteringWithoutParents(self):
        container = HierarchicalContainer()

        self.initializeHierarchicalContainer(container)
        container.setIncludeParentsWhenFiltering(False)

        # Filter by "contains ab"
        container.addContainerFilter(self.SIMPLE_NAME, 'ab', False, False)

        # 20 items match the filter.
        # com.vaadin.data.BufferedValidatable
        # com.vaadin.data.Validatable
        # com.vaadin.terminal.gwt.client.Focusable
        # com.vaadin.terminal.gwt.client.Paintable
        # com.vaadin.terminal.gwt.client.ui.Table
        # com.vaadin.terminal.gwt.client.ui.VLabel
        # com.vaadin.terminal.gwt.client.ui.VScrollTable
        # com.vaadin.terminal.gwt.client.ui.VTablePaging
        # com.vaadin.terminal.gwt.client.ui.VTabsheet
        # com.vaadin.terminal.gwt.client.ui.VTabsheetBase
        # com.vaadin.terminal.gwt.client.ui.VTabsheetPanel
        # com.vaadin.terminal.gwt.server.ChangeVariablesErrorEvent
        # com.vaadin.terminal.Paintable
        # com.vaadin.terminal.Scrollable
        # com.vaadin.terminal.Sizeable
        # com.vaadin.terminal.VariableOwner
        # com.vaadin.ui.Label
        # com.vaadin.ui.Table
        # com.vaadin.ui.TableFieldFactory
        # com.vaadin.ui.TabSheet
        # all become roots.
        expectedSize = 20
        expectedRoots = 20

        self.validateHierarchicalContainer(container,
                'com.vaadin.data.BufferedValidatable',
                'com.vaadin.ui.TabSheet',
                'com.vaadin.terminal.gwt.client.ui.VTabsheetBase',
                'blah', True, expectedSize, expectedRoots, False)

        # only include .gwt.client classes
        container.removeAllContainerFilters()
        container.addContainerFilter(self.FULLY_QUALIFIED_NAME,
                '.gwt.client.', False, False)

        packages = 3
        classes = 110

        expectedSize = packages + classes
        expectedRoots = 35 + 1  # com.vaadin.terminal.gwt.client.ui +
        # com.vaadin.terminal.gwt.client.*

        # Sorting is case insensitive
        self.validateHierarchicalContainer(container,
                'com.vaadin.terminal.gwt.client.ApplicationConfiguration',
                'com.vaadin.terminal.gwt.client.WidgetSet',
                'com.vaadin.terminal.gwt.client.ui.VOptionGroup',
                'blah', True, expectedSize, expectedRoots, False)

        # Additionally remove all without 'P' in the simple name.
        container.addContainerFilter(self.SIMPLE_NAME, 'P', False, False)

        expectedSize = 13
        expectedRoots = expectedSize

        self.validateHierarchicalContainer(container,
                'com.vaadin.terminal.gwt.client.Paintable',
                'com.vaadin.terminal.gwt.client.ui.VTabsheetPanel',
                'com.vaadin.terminal.gwt.client.ui.VPopupCalendar',
                'blah', True, expectedSize, expectedRoots, False)

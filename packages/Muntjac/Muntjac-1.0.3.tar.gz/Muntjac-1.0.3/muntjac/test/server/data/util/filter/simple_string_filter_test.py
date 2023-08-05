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
#
# Note: This is a modified file from Vaadin. For further information on
#       Vaadin please visit http://www.vaadin.com.

from muntjac.test.server.data.util.filter.abstract_filter_test \
    import AbstractFilterTest, TestItem, NullProperty

from muntjac.data.util.filter.simple_string_filter import SimpleStringFilter


class SimpleStringFilterTest(AbstractFilterTest):

    @classmethod
    def createTestItem(cls):
        return TestItem('abcde', 'TeSt')


    def getTestItem(self):
        return self.createTestItem()


    def f(self, propertyId, filterString, ignoreCase, onlyMatchPrefix):
        return SimpleStringFilter(propertyId, filterString, ignoreCase,
                onlyMatchPrefix)


    def passes(self, propertyId, filterString, ignoreCase, onlyMatchPrefix):
        return self.f(propertyId, filterString, ignoreCase,
                onlyMatchPrefix).passesFilter(None, self.getTestItem())


    def testStartsWithCaseSensitive(self):
        self.assertTrue( self.passes(self.PROPERTY1, 'ab', False, True) )
        self.assertTrue( self.passes(self.PROPERTY1, '', False, True) )

        self.assertFalse( self.passes(self.PROPERTY2, 'ab', False, True) )
        self.assertFalse( self.passes(self.PROPERTY1, 'AB', False, True) )


    def testStartsWithCaseInsensitive(self):
        self.assertTrue( self.passes(self.PROPERTY1, 'AB', True, True) )
        self.assertTrue( self.passes(self.PROPERTY2, 'te', True, True) )
        self.assertFalse( self.passes(self.PROPERTY2, 'AB', True, True) )


    def testContainsCaseSensitive(self):
        self.assertTrue( self.passes(self.PROPERTY1, 'ab', False, False) )
        self.assertTrue( self.passes(self.PROPERTY1, 'abcde', False, False) )
        self.assertTrue( self.passes(self.PROPERTY1, 'cd', False, False) )
        self.assertTrue( self.passes(self.PROPERTY1, 'e', False, False) )
        self.assertTrue( self.passes(self.PROPERTY1, '', False, False) )

        self.assertFalse( self.passes(self.PROPERTY2, 'ab', False, False) )
        self.assertFalse( self.passes(self.PROPERTY1, 'es', False, False) )


    def testContainsCaseInsensitive(self):
        self.assertTrue( self.passes(self.PROPERTY1, 'AB', True, False) )
        self.assertTrue( self.passes(self.PROPERTY1, 'aBcDe', True, False) )
        self.assertTrue( self.passes(self.PROPERTY1, 'CD', True, False) )
        self.assertTrue( self.passes(self.PROPERTY1, '', True, False) )

        self.assertTrue( self.passes(self.PROPERTY2, 'es', True, False) )

        self.assertFalse( self.passes(self.PROPERTY2, 'ab', True, False) )


    def testAppliesToProperty(self):
        fltr = self.f(self.PROPERTY1, 'ab', False, True)
        self.assertTrue( fltr.appliesToProperty(self.PROPERTY1) )
        self.assertFalse( fltr.appliesToProperty(self.PROPERTY2) )
        self.assertFalse( fltr.appliesToProperty('other') )


    def testEqualsHashCode(self):
        fltr = self.f(self.PROPERTY1, 'ab', False, True)

        f1 = self.f(self.PROPERTY2, 'ab', False, True)
        f1b = self.f(self.PROPERTY2, 'ab', False, True)
        f2 = self.f(self.PROPERTY1, 'cd', False, True)
        f2b = self.f(self.PROPERTY1, 'cd', False, True)
        f3 = self.f(self.PROPERTY1, 'ab', True, True)
        f3b = self.f(self.PROPERTY1, 'ab', True, True)
        f4 = self.f(self.PROPERTY1, 'ab', False, False)
        f4b = self.f(self.PROPERTY1, 'ab', False, False)

        # equal but not same instance
        self.assertEquals(f1, f1b)
        self.assertEquals(f2, f2b)
        self.assertEquals(f3, f3b)
        self.assertEquals(f4, f4b)

        # more than one property differ
        self.assertFalse(f1 == f2)
        self.assertFalse(f1 == f3)
        self.assertFalse(f1 == f4)
        self.assertFalse(f2 == f1)
        self.assertFalse(f2 == f3)
        self.assertFalse(f2 == f4)
        self.assertFalse(f3 == f1)
        self.assertFalse(f3 == f2)
        self.assertFalse(f3 == f4)
        self.assertFalse(f4 == f1)
        self.assertFalse(f4 == f2)
        self.assertFalse(f4 == f3)

        # only one property differs
        self.assertFalse(fltr == f1)
        self.assertFalse(fltr == f2)
        self.assertFalse(fltr == f3)
        self.assertFalse(fltr == f4)

        self.assertFalse(f1 is None)
        self.assertFalse(f1 == object())

        self.assertEquals(hash(f1), hash(f1b))
        self.assertEquals(hash(f2), hash(f2b))
        self.assertEquals(hash(f3), hash(f3b))
        self.assertEquals(hash(f4), hash(f4b))


    def testNonExistentProperty(self):
        self.assertFalse( self.passes('other1', 'ab', False, True) )


    def testNullValueForProperty(self):
        item = self.createTestItem()
        item.addItemProperty('other1', NullProperty())
        self.assertFalse( self.f('other1', 'ab', False,
                True).passesFilter(None, item) )

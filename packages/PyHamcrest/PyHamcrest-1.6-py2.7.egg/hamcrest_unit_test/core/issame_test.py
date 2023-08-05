if __name__ == '__main__':
    import sys
    sys.path.insert(0, '..')
    sys.path.insert(0, '../..')

from hamcrest.core.core.issame import *

from hamcrest.core.string_description import StringDescription
from hamcrest_unit_test.matcher_test import MatcherTest
import re
import unittest

__author__ = "Jon Reid"
__copyright__ = "Copyright 2011 hamcrest.org"
__license__ = "BSD, see License.txt"


class IsSameTest(MatcherTest):

    def testEvaluatesToTrueIfArgumentIsReferenceToASpecifiedObject(self):
        o1 = object()
        o2 = object()

        self.assert_matches('same', same_instance(o1), o1)
        self.assert_does_not_match('different', same_instance(o1), o2)

    def testDescriptionIncludesMemoryAddress(self):
        description = StringDescription()
        expected = re.compile("same instance as 0x[0-9a-fA-F]+ 'abc'")

        description.append_description_of(same_instance('abc'));
        self.assertTrue(expected.match(str(description)))

    def testSuccessfulMatchDoesNotGenerateMismatchDescription(self):
        o1 = object()
        self.assert_no_mismatch_description(same_instance(o1), o1)

    def testMismatchDescriptionShowsActualArgumentAddress(self):
        matcher = same_instance('foo')
        description = StringDescription()
        expected = re.compile("was 0x[0-9a-fA-F]+ 'hi'")

        result = matcher.matches('hi', description)
        self.assertFalse(result, 'Precondition: Matcher should not match item')
        self.assertTrue(expected.match(str(description)))

    def testMismatchDescriptionWithNilShouldNotIncludeAddress(self):
        self.assert_mismatch_description("was <None>", same_instance('foo'), None)

    def testDescribeMismatch(self):
        matcher = same_instance('foo')
        description = StringDescription()
        expected = re.compile("was 0x[0-9a-fA-F]+ 'hi'")

        matcher.describe_mismatch('hi', description)
        expected = re.compile("was 0x[0-9a-fA-F]+ 'hi'")
        self.assertTrue(expected.match(str(description)))

    def testDescribeMismatchWithNilShouldNotIncludeAddress(self):
        self.assert_describe_mismatch("was <None>", same_instance('foo'), None)


if __name__ == '__main__':
    unittest.main()

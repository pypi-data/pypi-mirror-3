# Copyright 2012 Craig Eales

# This file is part of pydstruct
#
# pydstruct is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.#
#
# pydstruct is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pydstruct.  If not, see <http://www.gnu.org/licenses/>.

import unittest
from .lists import test_all as test_all_lists

def test_suite():
    """Construct a test suite with all of the tests for the data structure families:
    lists
    """
    return unittest.TestSuite(
        test_all_lists.test_suite()
        )

def test(runner):
    """Run all of the tests for data structure family with the supplied runner"""
    runner.run(test_suite())

# Copyright (C) 2014 Daniel Lintott.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
import unittest
import sys
from gns3converter import utils


class TestUtils(unittest.TestCase):
    def test_fix_path_win(self):
        res = utils.fix_path('configs\R1.cfg')

        if sys.platform == 'win32':
            exp_res = 'configs\\R1.cfg'
        else:
            exp_res = 'configs/R1.cfg'

        self.assertEqual(res, exp_res)

    def test_fix_path_unix(self):
        res = utils.fix_path('configs/R1.cfg')

        if sys.platform == 'win32':
            exp_res = 'configs\\R1.cfg'
        else:
            exp_res = 'configs/R1.cfg'

        self.assertEqual(res, exp_res)
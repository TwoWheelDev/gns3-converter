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
"""
Anything to do with interfaces, also contains:
    * INTERFACE_RE for matching interfaces in a .net topology
    * ETHSWINT_RE for matching Ethernet switch port in a .net topology
"""
import re

# Regex matching interfaces (e.g. "f0/0")
INTERFACE_RE = re.compile(r"""^(g|gi|f|fa|a|at|s|se|e|et|p|po|i|id|IDS-Sensor
|an|Analysis-Module)([0-9]+)/([0-9]+)""", re.IGNORECASE)
# Regex matching a number (means an Ethernet switch port config)
ETHSWINT_RE = re.compile(r"""^([0-9]+)""")


class Interfaces():
    """
    Base Interface Class

    :param int port_id: starting port ID
    """
    def __init__(self, port_id):
        self.interfaces = []
        self.links = []
        self.port_id = port_id
        self.connections = None

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
Convenience module for adapters containing:
    * Adapter and port number/type matrix
    * Port type conversions (short to long)
"""

# Adapter Cards Matrix
ADAPTER_MATRIX = {'NM-16ESW': {'ports': 16, 'type': 'F'},
                  'NM-1E': {'ports': 1, 'type': 'E'},
                  'NM-1FE-TX': {'ports': 1, 'type': 'F'},
                  'NM-4E': {'ports': 4, 'type': 'E'},
                  'NM-4T': {'ports': 4, 'type': 'S'},
                  'PA-2FE-TX': {'ports': 2, 'type': 'F'},
                  'PA-4E': {'ports': 4, 'type': 'E'},
                  'PA-4T+': {'ports': 4, 'type': 'S'},
                  'PA-8E': {'ports': 8, 'type': 'E'},
                  'PA-8T': {'ports': 8, 'type': 'S'},
                  'PA-A1': {'ports': 1, 'type': 'A'},
                  'PA-FE-TX': {'ports': 1, 'type': 'F'},
                  'PA-GE': {'ports': 1, 'type': 'G'},
                  'PA-POS-OC3': {'ports': 1, 'type': 'P'},
                  'C7200-IO-2FE': {'ports': 2, 'type': 'F'},
                  'C7200-IO-GE-E': {'ports': 1, 'type': 'G'},
                  'WIC-1ENET': {'ports': 1, 'type': 'E'},
                  'WIC-1T': {'ports': 1, 'type': 'S'},
                  'WIC-2T': {'ports': 2, 'type': 'S'}}

# Port Type Matrix
PORT_TYPES = {'G': 'GigabitEthernet',
              'F': 'FastEthernet',
              'E': 'Ethernet',
              'S': 'Serial',
              'A': 'ATM',
              'P': 'POS'}

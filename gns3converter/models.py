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
Convenience module for building a model matrix arranged by:
    * Model
    * Chassis (if applicable)
and containing:
    * 'ports' = number of ports
    * 'type' = type of ports
"""
MODEL_MATRIX = {}

for platform in ('c1700', 'c2600', 'c2691', 'c3725', 'c3745',
                 'c3600', 'c7200'):
    MODEL_MATRIX[platform] = {}

# 1700s have one FE on the motherboard
for chassis in ('1720', '1721', '1750', '1751', '1760'):
    MODEL_MATRIX['c1700'][chassis] = {'ports': 1, 'type': 'F'}

# 2600s have one or more interfaces on the motherboard
for chassis in ('2620', '2610XM', '2620XM', '2650XM'):
    MODEL_MATRIX['c2600'][chassis] = {'ports': 1, 'type': 'F'}

for chassis in ('2621', '2611XM', '2621XM', '2651XM'):
    MODEL_MATRIX['c2600'][chassis] = {'ports': 2, 'type': 'F'}

MODEL_MATRIX['c2600']['2610'] = {'ports': 1, 'type': 'E'}
MODEL_MATRIX['c2600']['2611'] = {'ports': 2, 'type': 'E'}

# 2691s have two FEs on the motherboard
MODEL_MATRIX['c2691'][''] = {'ports': 2, 'type': 'F'}

# 3620s and 3640s have no ports on the motherboard
for chassis in ('3620', '3640'):
    MODEL_MATRIX['c3600'][chassis] = {'ports': 0}

# 3660s have 2 FEs on the motherboard
MODEL_MATRIX['c3600']['3660'] = {'ports': 2, 'type': 'F'}

# 3700s have 2 FEs on the motherboard
for platform in ('c3725', 'c3745'):
    MODEL_MATRIX[platform][''] = {'ports': 2, 'type': 'F'}

# 7206s have no ports on the motherboard
MODEL_MATRIX['c7200'][''] = {'ports': 0}

MODEL_TRANSFORM = {'2691': 'c2691',
                   '3725': 'c3725',
                   '3745': 'c3745',
                   '7200': 'c7200'}
for chassis in ('1720', '1721', '1750', '1751', '1760'):
    MODEL_TRANSFORM[chassis] = 'c1700'
for chassis in ('2620', '2621', '2610XM', '2611XM', '2620XM',
                '2621XM', '2650XM', '2651XM'):
    MODEL_TRANSFORM[chassis] = 'c2600'
for chassis in ('3620', '3640', '3660'):
    MODEL_TRANSFORM[chassis] = 'c3600'

EXTRA_CONF = ('VBoxDevice', 'QemuDevice', '5520', '525', 'O-series',
              'IDS-4215')

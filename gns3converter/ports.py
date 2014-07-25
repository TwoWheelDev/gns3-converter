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
                  'C7200-IO-GE-E': {'ports': 1, 'type': 'G'}}

# Port Type Matrix
PORT_TYPES = {'G': 'GigabitEthernet',
              'F': 'FastEthernet',
              'E': 'Ethernet',
              'S': 'Serial',
              'A': 'ATM',
              'P': 'POS'}



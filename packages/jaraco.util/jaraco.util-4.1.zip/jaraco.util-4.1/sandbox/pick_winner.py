from __future__ import print_function

import random
import operator
from collections import namedtuple

from jaraco.util.dictlib import RangeMap

Entrant = namedtuple('Entrant', 'id volume')
entrants = [
	Entrant(1, 1),
	Entrant(2, 5),
	Entrant(3, 3),
	Entrant(4, 1),
	# ...
]

def calculate_accumulated_volumes(entrants):
	# make acc_volume there so we have total
	global acc_volume
	acc_volume = 0
	for entrant in entrants:
		acc_volume += entrant.volume
		yield acc_volume


# create a map where a volume between 0 and total_volume produces gives
#  a weighted selection of Entrants.

weighted_entrants = RangeMap(zip(calculate_accumulated_volumes(entrants), entrants),
	key_match_comparator=operator.lt)

# test our bounds
assert weighted_entrants[0] == Entrant(1,1)
assert weighted_entrants[0.99999] == Entrant(1,1)
assert weighted_entrants[1] == Entrant(2,5)
assert weighted_entrants[6] == Entrant(3,3)
try:
	weighted_entrants[acc_volume]
except KeyError:
	pass
else:
	raise ValueError("Expected exception")


# now pick an entrant
for x in range(3):
	index = random.uniform(0, acc_volume)
	pick = weighted_entrants[index]
	print('picked', pick, '(%s)' % index)

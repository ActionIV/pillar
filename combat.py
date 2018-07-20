import random

def random_target(party):
	roll = random.randint(1,range(len(party)))
	return party_order[roll][0]

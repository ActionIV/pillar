import random

def random_target(party):
	roll = random.randint(1,(len(party)-1))
	return party[roll][0]
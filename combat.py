import random

def random_target(party):
	roll = random.randint(1,(len(party)-1))
	return party[roll]

def battle_status(survivors):
	players = 0
	enemies = 0
	for count in range(len(survivors)):
		if survivors[count].role == "Enemy" and survivors[count].isDead() == False:
			enemies += 1
		elif (survivors[count].role == "Player" or "NPC") and (survivors[count].isDead() == False):
			players += 1

	if enemies == 0:
		print("Right on!")
		return False
	elif players == 0:
		print("Odin beckons...")
		return False
	else:
		return True
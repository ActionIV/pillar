import random

def randomTarget(party_size):
	roll = random.randint(1,party_size)
	return roll-1

def calculateDamage(stat, multiplier, defense):
	atk_power = stat * multiplier + random.randint(1, stat)
	return atk_power - defense

def battleStatus(survivors):
	players = 0
	enemies = 0
	for count in range(len(survivors)):
		if (survivors[count].role == "Enemy") and (survivors[count].isDead() == False):
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

def afterTurn(attacker):
	attacker.add_action(attacker.command)
	attacker.targets.clear()
	return attacker
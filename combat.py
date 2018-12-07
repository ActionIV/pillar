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

def frontOfGroup(combatants, att, foe):
	attacker = combatants[att]
	priority = 100
	defender = 0

	for tar in range(len(combatants)):
		if (combatants[tar].name == attacker.targets[foe]) and (int(combatants[tar].position) < priority) and (combatants[tar].isDead() == False):
			priority = combatants[tar].position
			defender = tar
	return defender

def groupAttack(combatants, name, damage):
	body_count = 0
	for who in range(len(combatants)):
		if combatants[who].name == name:
			combatants[who].current_HP -= damage
			if combatants[who].current_HP <= 0:
				combatants[who].current_HP = 0
				combatants[who].lives -= 1
				body_count += 1
	if body_count > 0:
		print("Defeated %d." % body_count)
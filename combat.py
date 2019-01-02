import random

def randomTarget(party_size):
	roll = random.randint(1,party_size)
	return roll-1

def calculateDamage(stat, multiplier):
	atk_power = stat * multiplier + random.randint(1, stat)
	return atk_power

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
	if damage < 0:
		damage = 0
		print("No damage.")
	else:
		print("%d damage to %s group." % (damage, name))
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

def rollDamage(command, attacker):
	stat = command.stat
	multiplier = command.multiplier
	if stat == "Str":
		damage = calculateDamage(attacker.current_Str, multiplier)
	elif stat == "Agl":
		damage = calculateDamage(attacker.current_Agl, multiplier)
	elif stat == "Mana":
		# Need to check resistances
		damage = calculateDamage(attacker.current_Mana, multiplier)
	elif stat == "Set":
		# Need to add race_bonus eventually
		# What is the random component to damage here?
		if command.rand_dmg > 0:
			damage = command.min_dmg + random.randint(1,command.rand_dmg)
		else:
			damage = command.min_dmg
	else:
		damage = 0
	return damage

def determineDefense(defender, attack_type, damage):
	if attack_type in ("Melee", "Ranged"):
		defense = defender.current_Def
		if defender.isCursed() == True:
			defense = round(defense / 2)
		defense = defender.current_Def * 5
		return defense
	elif attack_type == "Magic":
		# Still need to add resistance checks (traits, equipment, MAGI)
		return damage * defender.current_Mana / 200

def affectStat(target, stat, amount):
	if stat == "STR":
		target.current_Str += amount
	elif stat == "AGL":
		target.current_Agl += amount
	elif stat == "MANA":
		target.current_Mana += amount
	elif stat == "DEF":
		target.current_Def += amount
	return target
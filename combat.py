import random

# def randomTarget(party_size):
# 	roll = random.randint(1,party_size)
# 	return roll-1

def randomTarget(target_list, combatants):
	target = ""
	while target == "":
		roll = random.randint(1,len(target_list))-1
		random_who = target_list[roll][2]
		if combatants[random_who].isTargetable():
			target = target_list[roll][0]
			return target
		else:
			continue

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

def endOfTurn(attacker):
	if attacker.isParalyzed() == True:
		roll = random.randint(1,100)
		if roll <= 15:
			print("%s was released from paralysis." % attacker.name)
			attacker.paralyzed = "n"
		else:
			print("%s is paralyzed." % attacker.name)
	if attacker.isAsleep() == True:
		roll = random.randint(1,100)
		if roll <= 30:
			print("%s woke up." % attacker.name)
			attacker.asleep = "n"
		else:
			print("%s is asleep." % attacker.name)
	if attacker.isPoisoned() == True:
		roll = random.randint(1,100)
		if roll <= 20:
			print("%s's poison was neutralized." % attacker.name)
			attacker.poisoned = "n"
		else:
			print("%s is poisoned." % attacker.name, end = " ")
			poison_dmg = attacker.HP * 0.1
			attacker.current_HP -= poison_dmg
			print("%d damage." % poison_dmg, end = " ")
			if attacker.current_HP <= 0:
				attacker.current_HP = 0
				attacker.lives -= 1
				if attacker.isDead():
					print("%s succumbed to the poison." % attacker.name)
				else:
					print("")
	if attacker.isConfused() == True:
		roll = random.randint(1,100)
		if roll <= 10:
			print("%s regained sanity." % attacker.name)
			attacker.confused = "n"
		else:
			print("%s is confused." % attacker.name)

	if attacker.role == "Enemy":
		attacker.command = 'nan'

	return attacker

def frontOfGroup(combatants, att, foe):
	attacker = combatants[att]
	priority = 100
	defender = 100

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
		body_count = 0
		for who in range(len(combatants)):
			if combatants[who].name == name and combatants[who].isDead() == False and combatants[who].isStoned() == False:
				combatants[who].current_HP -= damage
				if combatants[who].current_HP <= 0:
					combatants[who].current_HP = 0
					combatants[who].lives -= 1
					body_count += 1
		print("%d damage to %s group." % (damage, name), end = " ")
		if body_count > 0:
			print("Defeated %d." % body_count)
		else:
			print("")

def rollHeal(command, healer, ally):
	if command.att_type == "Magic":
		heal = (healer.current_Mana + ally.current_Mana) * command.multiplier + random.randint(1, healer.current_Mana)
	else:
		heal = command.min_dmg
	if ally.isDead():
		print("No effect.")
		return
	elif (ally.current_HP + heal) > ally.HP:
		heal = ally.HP - ally.current_HP
		ally.current_HP = ally.HP
	else:
		ally.current_HP += heal
	print("%s recovers %d HP." % (ally.name, heal))

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
	print("%s increases by %d." % (stat, amount))
	return target

def inflictCondition(command, attacker, defender):
	hit_chance = attacker.current_Mana - (defender.current_Mana * 2) + 50
	roll = random.randint(1,100)
	if hit_chance < roll:
		applyCondition(command.status, defender)
	else:
		print("Resisted.")

def applyCondition(status, defender):
	if status == "Stone":
		defender.stoned = "y"
		defender.blinded = "n"
		defender.poisoned = "n"
		defender.confused = "n"
		defender.paralyzed = "n"
		defender.asleep = "n"
		defender.cursed = "n"
		print("Turned to stone.")
	elif status == "Curse":
		defender.cursed = "y"
		print("Cursed.")
	elif status == "Blind":
		defender.blinded = "y"
		print("Blinded.")
	elif status == "Sleep":
		defender.asleep = "y"
		print("Put to sleep.")
	elif status == "Paralyze":
		defender.paralyzed = "y"
		print("Paralyzed.")
	elif status == "Poison":
		defender.poisoned = "y"
		print("Poisoned.")
	elif status == "Confuse":
		defender.confused = "y"
		print("Confused.")
	elif status == "Stun":
		print("Slain.")
		defender.current_HP = 0
		defender.lives -= 1
		defender.blinded = "n"
		defender.poisoned = "n"
		defender.confused = "n"
		defender.paralyzed = "n"
		defender.asleep = "n"
		defender.cursed = "n"

def buildResistances(skills, resist_list, resist_table):
	for count in range(len(skills)):
		if skills[count] == "blank":
			continue
		else:
			result = separateResists(skills[count], resist_table)
			if isinstance(result, list) == True:
				resist_list.extend(result)
			else:
				resist_list.append(result)

	## Dynamic loop to remove all O- skills and replace them with base resistances
	#if not resist_list:
	#	return
	#else:
	#	list(filter("None".__ne__, resist_list))
	#	count = 0
	#	while count < len(resist_list):
	#		if resist_list[count].startswith("O-"):
	#			result = separateResists(skills[count], resist_table)
	#			if isinstance(result, list) == True:
	#				resist_list.extend(result)
	#			else:
	#				resist_list.append(result)
	#		count += 1

# SHOULD THIS EXECUTE IMMEDIATELY AFTER SKILLS ARE ADDED TO THE LIST, OR LEAVE IT AS IS?
def checkResistance(resist_list, element, status, type, barriers):
	total_resists = barriers.copy()
	total_resists.extend(resist_list)
	#total_resists.extend(barriers)

	# If Melee or Ranged attack with no element, the element is Weapon
	if type in ("Melee", "Ranged") and element == "None":
		element = "Weapon"

	# Check the total list for the resistance in question
	for count in range(len(resist_list)):
		if total_resists[count] in (status, element) and total_resists[count] != "None":
			return True
	
	# If no resistance was found
	return False

def separateResists(check, resist_table):
	# Only take the element field if the check is against armor, traits, or MAGI
	element = resist_table.loc[check, "Element"]
	if (resist_table.loc[check, "Type"] in ("Armor", "Trait", "MAGI")) and (element != "None"):
		elements = []
		elements = element.split(', ')
		count = 0
		while count < len(elements):
			if elements[count].startswith("O-"):
				result = separateResists(elements[count], resist_table)
				if isinstance(result, list) == True:
					elements.extend(result)
				else:
					elements.append(result)
			count += 1
		return elements
	else:
		return "None"
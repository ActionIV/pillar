import random

def randomTarget(target_list, combatants):
	target = ""
	while target == "":
		roll = random.randint(0,len(target_list)-1)
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
		if (survivors[count].role == "Enemy") and survivors[count].isTargetable():
			enemies += 1
		elif (survivors[count].role == "Player" or "NPC") and survivors[count].isTargetable():
			players += 1
	# Print if one side has no survivors, otherwise continue on
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
	if attacker.isParalyzed():
		roll = random.randint(1,100)
		if roll <= 15:
			print("%s was released from paralysis." % attacker.name)
			attacker.paralyzed = "n"
		else:
			print("%s is paralyzed." % attacker.name)
	if attacker.isAsleep():
		roll = random.randint(1,100)
		if roll <= 30:
			print("%s woke up." % attacker.name)
			attacker.asleep = "n"
		else:
			print("%s is asleep." % attacker.name)
	if attacker.isPoisoned():
		roll = random.randint(1,100)
		if roll <= 20:
			print("%s's poison was neutralized." % attacker.name)
			attacker.poisoned = "n"
		else:
			print("%s is poisoned." % attacker.name, end = " ")
			poison_dmg = attacker.HP * 0.1
			print("%d damage." % poison_dmg)
			if applyDamage(poison_dmg, attacker) == 1:
				print("%s succumbed to the poison." % attacker.name)

	if attacker.role == "Enemy":
		attacker.command = 'nan'
	return attacker

def frontOfGroup(combatants, att, foe):
	attacker = combatants[att]
	priority = 100
	defender = 100

	for tar in range(len(combatants)):
		if (combatants[tar].name == attacker.targets[foe]) and (int(combatants[tar].position) < priority) and combatants[tar].isTargetable():
			priority = combatants[tar].position
			defender = tar
	return defender

def groupAttack(combatants, name, damage):
	body_count = 0
	for who in range(len(combatants)):
		# Only damage those matching the target name and that are not already dead or stoned
		if combatants[who].name == name and combatants[who].isTargetable():
			body_count += applyDamage(damage, combatants[who])
	# REVISIT TO MAKE PRINTING MORE FLEXIBLE BASED ON RESULTS (deaths, no deaths, single character group, etc)
	print("%d damage to %s group." % (damage, name), end = " ")
	if body_count > 0:
		print("Defeated %d." % body_count)
	else:
		print("")

def counterAttack(avenger, attacker, command, damage_received, barriers):
	print("%s counter-attacks with %s." % (avenger.name, command.name), end = " ")
	if command.stat == "Str":
		if damage_received < avenger.getStrength() * 2:
			counter_dmg = avenger.getStrength() * 2
		else:
			counter_dmg = damage_received
		damage = round(counter_dmg * command.multiplier / 10 + avenger.getStrength())

	# For MANA or Status-based counters
	else:
		if checkResistance(attacker.resists, command.element, command.status, barriers):
			print("%s is strong against %s." % (attacker.name, command.name))
		else:
			if command.stat == "Status":
				inflictCondition(command, avenger, attacker)
			elif command.stat == "Mana":
				counter_dmg = rollDamage(command, avenger)
				defense = determineDefense(attacker, command.att_type, counter_dmg)
				if checkWeakness(command.element, attacker):
					print("Hits weakness.", end = " ")
					defense = 0
				damage = counter_dmg - defense

	if attacker.isPoisoned():
		damage = round(damage/2)

	# No damage on pure Status attacks
	if command.stat == "Status":
		pass
	elif damage <= 0:
		damage = 0
		print("No damage.")
	else:
		print("%d damage to %s." % (damage, attacker.name))
		if applyDamage(damage, attacker) == 1:
			print("%s fell." % attacker.name)

def applyDamage(damage, target):
	target.current_HP -= damage
	if target.current_HP <= 0:
		applyCondition("Stun", target)
		return 1
	else:
		return 0

def rollHeal(command, healer, ally):
	if command.att_type == "Magic":
		heal = (healer.getMana() + ally.getMana()) * command.multiplier + random.randint(1, healer.getMana())
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

def rollHit(attacker_stat, defender_stat):
	difference = defender_stat - (attacker_stat * 2)
	return 97 - difference

def rollDamage(command, attacker):
	stat = command.stat
	multiplier = command.multiplier
	element = command.element
	if stat == "Str":
		#if attacker.isCursed():
		#	damage = calculateDamage(round(attacker.current_Str / 2), multiplier)
		#else:
		#	damage = calculateDamage(attacker.current_Str, multiplier)
		damage = calculateDamage(attacker.getStrength(),multiplier)
	elif stat == "Agl":
		#if attacker.isBlinded():
		#	damage = calculateDamage(round(attacker.current_Agl / 2), multiplier)
		#else:
		#	damage = calculateDamage(attacker.current_Agl, multiplier)
		damage = calculateDamage(attacker.getAgility(), multiplier)
	elif stat == "Mana":
		if attacker.role == "Player" and attacker.magi.startswith(command.element):
			damage = calculateDamage(attacker.getMana() + 5 + attacker.magi_count, multiplier)
		else:
			damage = calculateDamage(attacker.getMana(), multiplier)
	elif stat == "Set":
		# Need to add race_bonus eventually
		if isinstance(command.rand_dmg, int) and command.rand_dmg > 0:
			damage = command.min_dmg + random.randint(1,command.rand_dmg)
		elif command.rand_dmg == "Str":
			damage = command.min_dmg + random.randint(1,attacker.getStrength())
		else:
			damage = command.min_dmg
	else:
		damage = 0
	return damage

def determineDefense(defender, attack_type, damage):
	if attack_type in ("Melee", "Ranged"):
		#defense = defender.current_Def
		#if defender.isCursed():
		#	defense = round(defense / 2)
		#defense = defender.current_Def * 5
		return defender.getDefense() * 5
	elif attack_type == "Magic":
		return round(damage * defender.getMana() / 200)

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

def inflictCondition(command, attacker, target):
	# Originally (target - attacker) * 2 + 50
	hit_chance = target.getMana() - attacker.getMana() + 50
	roll = random.randint(1,100)
	if hit_chance < roll:
		applyCondition(command.status, target)
	else:
		print("%s resisted." % target.name)

def applyCondition(status, target):
	if status == "Stone":
		target.stoned = "y"
		target.blinded = "n"
		target.poisoned = "n"
		target.confused = "n"
		target.paralyzed = "n"
		target.asleep = "n"
		target.cursed = "n"
		print("Turned %s to stone." % target.name)
	elif status == "Curse":
		target.cursed = "y"
		print("Cursed %s." % target.name)
	elif status == "Blind":
		target.blinded = "y"
		print("Blinded %s." % target.name)
	elif status == "Sleep":
		target.asleep = "y"
		print("Put %s to sleep." % target.name)
	elif status == "Paralyze":
		target.paralyzed = "y"
		print("Paralyzed %s." % target.name)
	elif status == "Poison":
		target.poisoned = "y"
		print("Poisoned %s." % target.name)
	elif status == "Confuse":
		target.confused = "y"
		print("Confused %s." % target.name)
	elif status == "Stun":
		target.current_HP = 0
		target.lives -= 1
		target.blinded = "n"
		target.poisoned = "n"
		target.confused = "n"
		target.paralyzed = "n"
		target.asleep = "n"
		target.cursed = "n"

def removeCondition(status, target):
	if status == "Stone":
		target.stoned = "n"
		print("Softened %s." % target.name)
	elif status == "Curse":
		target.cursed = "n"
		print("Released %s from curse." % target.name)
	elif status == "Blind":
		target.blinded = "n"
		print("Restored sight to %s." % target.name)
	elif status == "Sleep":
		target.asleep = "n"
		print("Woke %s." % target.name)
	elif status == "Paralyze":
		target.paralyzed = "n"
		print("Released %s from paralysis." % target.name)
	elif status == "Poison":
		target.poisoned = "n"
		print("Neutralized %s's poison." % target.name)
	elif status == "Confuse":
		target.confused = "n"
		print("Returned %s to sanity." % target.name)
	elif status == "Revive":
		target.current_HP = 1
		target.lives += 1
		print("Revived %s." % target.name)
	elif status == "Full Restore":
		target.stoned = "n"
		target.blinded = "n"
		target.poisoned = "n"
		target.confused = "n"
		target.paralyzed = "n"
		target.asleep = "n"
		target.cursed = "n"
		print("%s was restored." % target.name)

def buildResistances(skills, resist_list, resist_table):
	for count in range(len(skills)):
		# Skip the breakdown if it's a blank slot or if it's a weakness
		if skills[count] == "blank" or skills[count].startswith("X-"):
			continue
		else:
			result = separateResists(skills[count], resist_table)
			if isinstance(result, list) == True:
				resist_list.extend(result)
			else:
				resist_list.append(result)

def checkResistance(resist_list, element, status, barriers):
	total_resists = barriers.copy()
	total_resists.extend(resist_list)

	# Check the total list for the resistance in question
	for count in range(len(total_resists)):
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

# REWRITE TO PASS RESIST_TABLE SO ELEMENT FIELD IS USED FOR WEAKNESS...MAYBE
def checkWeakness(element, target):
	# Check against trait-based weaknesses first
	for each in range(len(target.skills)):
		trait = target.skills[each]
		if trait.startswith("X-"):
			weakness = trait[2:]
			if weakness == element:
				return True
	# Now check species-based weaknesses
	if target.family == element:
		return True
import random
from collections import Counter

# def rollGroupSize(text):
# 	roll_range = text.split("-")
# 	if len(roll_range) > 1:
# 		return random.randint(int(roll_range[0]), int(roll_range[1]))
# 	else:
# 		return 1

def randomTarget(target_list, combatants):
	target = ""
	if not target_list:
		while target == "":
			roll = random.randint(0, len(combatants)-1)
			if combatants[roll].isTargetable():
				return combatants[roll].name
			else:
				pass
	else:
		while target == "":
			roll = random.randint(0,len(target_list)-1)
			random_who = target_list[roll][0]
#			if combatants[random_who].isTargetable():
#				target = target_list[roll][0]
#				return target
			for tar in range(len(combatants)):
				if combatants[tar].name == random_who and combatants[tar].isTargetable():
					target = combatants[tar].name # Substantial rewrite is required to allow for targeting randomly inside enemy groups
					return target
#			else:
#				pass

#####################################
####### END OF TURN FUNCTIONS #######
#####################################

def postBattle(combatants, m_skills, growth_rates, commands, player_table):
	enemies = []
	players = []
	npcs = []
	for each in range(len(combatants)):
		if combatants[each].role == "Enemy":
			enemies.append(combatants[each].name)
		elif combatants[each].role == "Player":
			players.append(combatants[each])
		else:
			npcs.append(combatants[each])

	# GOLD, ITEMS, AND MEAT
	defeated = Counter(enemies)
	defeated.keys()
	highest_ds = 1
	total_gold = 0

	print("REWARDS")
	for key, number in defeated.items():
		drop_roll = random.randint(1,100)
		drop_chance = 20 + number
		enemy_level = 1

		# Drop chances
		for enemy in range(len(combatants)):
			if combatants[enemy].name == key:
				if drop_roll <= drop_chance:
					# Meat drop for monsters
					if combatants[enemy].Type == 2:
						print("%s's meat!" % combatants[enemy].name)
					# Item drops for humans, mutants, and robots
					elif combatants[enemy].Type in (0,1,3):
						drop = ""
						while drop == "":
							item_roll = random.randint(1,len(combatants[enemy].skills))-1
							if combatants[enemy].skills[item_roll] != "blank" and commands.loc[combatants[enemy].skills[item_roll], "Price"] >= 0:
								drop = combatants[enemy].skills[item_roll]
								print("%s dropped %s." % (combatants[enemy].name, drop))
							# Mutants can leave their essence behind if a skill or trait is selected
							elif combatants[enemy].Type == 1:
								drop = combatants[enemy].skills[item_roll]
								print("%s left its essence behind." % combatants[enemy].name)
							# Robots leave parts behind if the selected drop is not equippable
							elif combatants[enemy].Type == 3:
								drop = "Done"
								print("%s dropped %s Parts." % (combatants[enemy].name, combatants[enemy].name))

				# Gold drops no matter what
				enemy_level = combatants[enemy].DS
				if enemy_level > highest_ds:
					highest_ds = enemy_level
				total_gold = total_gold + (33 + (3*(number-1))) * enemy_level * number
				break
	indy_gold = round(total_gold / (len(players) + len(npcs)))
	print("Each party member receives %d GP." % indy_gold)

	# PLAYER TABLE UPDATES
	for pc in range(len(players)):
		# Add gold
		players[pc].gold += indy_gold
		#player_table.loc[players[pc].name, "GOLD"] += indy_gold

		# STAT GROWTHS
		if players[pc].family in ("Human", "Mutant") and players[pc].isTargetable():
			# VARIABLES
			skill_base = growth_rates.loc[players[pc].family, "SKILL"]
			skill_bonus = growth_rates.loc[players[pc].family, "SKILL BONUS"]
			hp_base = growth_rates.loc[players[pc].family, "HP"]
			hp_bonus = growth_rates.loc[players[pc].family, "HP BONUS"]
			str_base = growth_rates.loc[players[pc].family, "STR"]
			str_bonus = growth_rates.loc[players[pc].family, "STR BONUS"]
			agl_base = growth_rates.loc[players[pc].family, "AGL"]
			agl_bonus = growth_rates.loc[players[pc].family, "AGL BONUS"]
			mana_base = growth_rates.loc[players[pc].family, "MANA"]
			mana_bonus = growth_rates.loc[players[pc].family, "MANA BONUS"]
			def_base = growth_rates.loc[players[pc].family, "DEF"]
			def_bonus = growth_rates.loc[players[pc].family, "DEF BONUS"]

			# HP and SKILL EQUIVALENT LEVEL
			# DS level formula could be converted to 26*MHP / (MHP+1300)
			hp_level = equivalentLevel(players[pc].HP, 26, 50)
			
			# HP and SKILL CHANCE
			if players[pc].stats_used.count("God") > 0:
				hp_chance = 200
			else:
				hp_chance = growthChance(hp_base, hp_bonus, highest_ds, hp_level)
			hp_roll = random.randint(1,200)
			if hp_roll <= hp_chance:
				hp_gain = int(players[pc].HP / 50) + random.randint(6,11)
				players[pc].HP = players[pc].HP + hp_gain
				print("%s's Max HP increased by %d." % (players[pc].name, hp_gain))
				#player_table.loc[players[pc].name, "HP"] = players[pc].HP

			# MUTANT SKILLS
			if players[pc].family == "Mutant":
				skill_chance = growthChance(skill_base, skill_bonus, highest_ds, hp_level)
				skill_roll = random.randint(1,200)
				if skill_roll <= skill_chance:
					ds_roll = random.randint(1,highest_ds)
					option_count = m_skills.loc[ds_roll, "Count"]
					option_roll = random.randint(1,option_count)
					gained_skill = m_skills.iloc[ds_roll-1, option_roll]
					for skill in range(4):
						if players[pc].skills[skill] == 'blank':
							print("%s acquired %s." % (players[pc].name, gained_skill))
							players[pc].skills[skill] = gained_skill
							player_table.loc[players[pc].name, "S%d" % skill] = gained_skill
							break
						elif skill == 3 and players[pc].skills[skill] != 'blank':
							print("%s acquired %s. Choose what gets replaced: [%s, %s, %s, %s]" % (players[pc].name, gained_skill,
								players[pc].skills[0], players[pc].skills[1], players[pc].skills[2], players[pc].skills[3],))
							#players[pc].skills[skill] = gained_skill
							#player_table.loc[players[pc].name, "S%d" % skill] = gained_skill

			# OTHER STAT GROWTHS
			# If no action was taken, try to grow the stat for the action that would've been taken
			if not players[pc].stats_used:
				players[pc].stats_used = commands.loc[players[pc].command, "Growth Stat"]
			str_count = players[pc].stats_used.count("Str")
			agl_count = players[pc].stats_used.count("Agl")
			mana_count = players[pc].stats_used.count("Mana")
			def_count = players[pc].stats_used.count("Def")
			if players[pc].stats_used.count("Mix") > 0:
				lowest_stat = ""
				low_value = 0
				if players[pc].natural_str > players[pc].natural_agl:
					lowest_stat = "Agl"
					low_value = players[pc].natural_agl
				else:
					lowest_stat = "Str"
					low_value = players[pc].natural_str
				if low_value > players[pc].natural_mana:
					lowest_stat = "Mana"
				if lowest_stat == "Str":
					str_count += 1
				elif lowest_stat == "Agl":
					agl_count += 1
				else:
					mana_count += 1

			if players[pc].stats_used.count("God") > 0:
				str_count = 200
				agl_count = 200
				mana_count = 200

			if statGrowth(players[pc].natural_str, str_count, str_base, str_bonus, highest_ds):
				players[pc].natural_str += 1
				print("%s's STR increased by 1." % (players[pc].name))
				#player_table.loc[players[pc].name, "Natural STR"] = players[pc].natural_str
			if statGrowth(players[pc].natural_agl, agl_count, agl_base, agl_bonus, highest_ds):
				players[pc].natural_agl += 1
				print("%s's AGL increased by 1." % (players[pc].name))
				#player_table.loc[players[pc].name, "Natural AGL"] = players[pc].natural_agl
			if statGrowth(players[pc].natural_mana, mana_count, mana_base, mana_bonus, highest_ds):
				players[pc].natural_mana += 1
				print("%s's MANA increased by 1." % (players[pc].name))
				#player_table.loc[players[pc].name, "Natural MANA"] = players[pc].natural_mana
			if statGrowth(players[pc].natural_def, def_count, def_base, def_bonus, highest_ds):
				players[pc].natural_def += 1
				print("%s's DEF increased by 1." % (players[pc].name))
				#player_table.loc[players[pc].name, "Natural DEF"] = players[pc].natural_def

		# Set Current HP
		if players[pc].current_HP > 0:
			player_table.loc[players[pc].name, "Current HP"] = players[pc].current_HP
		else:
			player_table.loc[players[pc].name, "Current HP"] = 1
			players[pc].current_HP = 1
			players[pc].lives += 1
		# Status Conditions
		condition = ""
		players[pc].poisoned = "n"
		players[pc].confused = "n"
		players[pc].paralyzed = "n"
		players[pc].asleep = "n"
		if players[pc].isBlinded():
			condition = condition + "BLND"
		if players[pc].isStoned():
			condition = condition + "STON"
		if players[pc].isCursed():
			condition = condition + "CURS"
		if condition == "":
			condition = "GOOD"
		player_table.loc[players[pc].name, "CONDITION"] = condition
	print("")

# Used for all non-HP stats
def statGrowth(stat, stat_count, stat_base, stat_bonus, highest_ds):
	if stat_count > 0:
		stat_level = equivalentLevel(stat, 20, 5)
		stat_chance = growthChance(stat_base, stat_bonus, highest_ds, stat_level) + stat_count-1
		stat_roll = random.randint(1,200)
		if stat_roll <= stat_chance:
			return True

def equivalentLevel(stat, const1, const2):
	level = int(stat / ((stat / const1) + const2))
	return level

def growthChance(base, bonus, enemy_ds, player_ds):
	growthChance = base + bonus * (enemy_ds - player_ds) # REMOVED: Added 1 to the parenthetical equation, giving a bonus for enemies of equal strength
	return growthChance

# DEFECT: If the ability used is not in the skill list, the first slot is decremented (skill_slot = 0)
def afterTurn(attacker, stat_used, table):
	# Checks to see if the skill has been documented and deducted yet this turn. If not, set the flag to say it has
	if attacker.has_used_skill_this_turn == True:
		return attacker
	else:
		attacker.has_used_skill_this_turn = True

	attacker.addAction(attacker.command, stat_used)
	attacker.targets.clear()
	skill_slot = 0
	if attacker.role in ("Player", "NPC"):
		skill_slot = attacker.skillSlot()
		if skill_slot < 8:
			attacker.uses[skill_slot] -= 1
		elif skill_slot == 8:
			table.loc[attacker.name, "MAGI Uses Left"] -= 1
		else:
			print("Skill not found! Decrement manually.")
	return attacker

def endOfTurn(attacker, traits):
	poison_dmg = 0
	heal = 0

	attacker.stopped = "n"  # Always remove Stop at the end of a turn
	attacker.has_used_skill_this_turn = False  # Reset the "acted" flag at end of turn

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
			poison_dmg = int(attacker.HP * 0.1)
			print("%d damage." % poison_dmg)
			if applyDamage(poison_dmg, attacker) == 1:
				print("%s succumbed to the poison." % attacker.name)
	# REGEN
	for skill in range(len(attacker.skills)):
		if attacker.skills[skill] == "blank":
			continue
		else:
			skill_effect = traits.loc[attacker.skills[skill],"Effect"]
			if "Regen" in skill_effect and attacker.isTargetable():
				heal = int(attacker.HP * (traits.loc[attacker.skills[skill], "Percent"] / 100))
				heal = applyHeal(heal, attacker)
				print("%s regenerates %d HP." % (attacker.name, heal))
				break # end loop since Regen should only be applied once

	if attacker.role in ("NPC", "Enemy"):
		attacker.command = "None"
	return attacker

################################
####### ATTACK FUNCTIONS #######
################################

def hitScore(command, attacker, target_stat):
	# Ranged attacks are based on Percent chance unless using a Gun
	hit_score = 0
	if command.att_type == "Ranged" and command.percent != 0:
		# All guns and cannons have Robot Race Bonus and use STR as a calculation
		if command.race_bonus == "Robot":
			# Robots gain double their STR to hit with guns and cannons
			if attacker.family == "Robot":
				hit_score = attacker.getStrength() * 2 + command.percent - target_stat + attacker.hit_bonus
			else:
				hit_score = attacker.getStrength() + command.percent - target_stat + attacker.hit_bonus
		# Bows use 2x AGL and the item's hit chance
		else:
			hit_score = attacker.getAgility() * 2 + command.percent - target_stat + attacker.hit_bonus
	# Spell resist formula
	elif command.att_type == "Magic":
		hit_score = min(95, 100 - (2 * (target_stat - attacker.getMana()) + attacker.hit_bonus))

	# Melee attacks just use AGL
	else:
		hit_score = min(97, 100 - (2 * (target_stat - attacker.getAgility()) + attacker.hit_bonus))

	# Check Humans for masteries
	if attacker.family == "Human" and attacker.role == "Player":
		hit_score += int(attacker.humanBonus(command.symbol))

	if hit_score < 5:
		hit_score = 5

	# CHANGE TO BLIND MECHANICS - Blind now reduces hit by 30% for any non-magic attack
	if attacker.isBlinded() and command.att_type != "Magic":
		return int(hit_score * 0.7)
	else:
		return hit_score

def frontOfGroup(combatants, attacker, foe, command):
	priority = 100
	defender = 100

#	if isinstance(attacker.targets[foe], int):
#		defender = attacker.targets[foe]
#	else:
	if command.effect in "Rear":
		priority = 0
		for tar in range(len(combatants)):
			if (combatants[tar].name == attacker.targets[foe]) and (int(combatants[tar].position) > priority) and combatants[tar].isTargetable():
				priority = combatants[tar].position
				defender = tar
			elif (combatants[tar].name == attacker.targets[foe] and command.targeting in ("Ally", "Allies")):
				if (combatants[tar].isDead() and command.status == ("Revive")) or (combatants[tar].isStoned() and command.status == ("Stone")):
					priority = combatants[tar].position
					defender = tar
	else:
		for tar in range(len(combatants)):
			if (combatants[tar].name == attacker.targets[foe]) and (int(combatants[tar].position) < priority) and combatants[tar].isTargetable():
				priority = combatants[tar].position
				defender = tar
			elif (combatants[tar].name == attacker.targets[foe] and command.targeting in ("Ally", "Allies")):
				if (combatants[tar].isDead() and command.status == ("Revive")) or (combatants[tar].isStoned() and command.status == ("Stone")):
					priority = combatants[tar].position
					defender = tar
	return defender

def counterAttack(avenger, attacker, command, damage_received, barriers):
	print("-%s counter-attacks with %s." % (avenger.name, command.name), end = " ")
	if command.stat == "Str":
		avenger_str = avenger.getStrength()
		if avenger.isPoisoned():
			avenger_str = int(avenger_str/2)
		if damage_received < (avenger_str * 2):
			counter_dmg = avenger_str * 2
		else:
			counter_dmg = damage_received
		damage = int(counter_dmg * command.multiplier / 10 + random.randint(0,avenger_str))
	elif command.stat == "Uses":
		counter_dmg = (command.min_dmg - command.remaining) * command.multiplier
		if damage_received < counter_dmg:
			damage = int(counter_dmg / 2)
		else:
			damage = damage_received

	# For MANA or Status-based counters
	else:
		if checkResistance(attacker, command.element + " " + command.status, barriers):
			print("%s is strong against %s." % (attacker.name, command.name), end = " ")
			return
		else:
			if command.stat == "Status":
				inflictCondition(command, avenger, attacker, True)
			elif command.stat == "Mana":
				counter_dmg = rollDamage(command, avenger)
				command.att_type = "Magic"
				defense = determineDefense(attacker, command, counter_dmg)
				if checkWeakness(command.element, attacker):
					print("Hits weakness.", end = " ")
					defense = 0
				damage = counter_dmg - defense

	# No damage on pure Status attacks
	if command.stat == "Status":
		pass
		# print("")
	elif damage <= 0:
		damage = 0
		print("No damage.", end = " ")
	else:
		print("%d damage." % damage)
		if applyDamage(damage, attacker) == 1:
			print("%s fell." % attacker.name, end = " ")

# NOT PLACED IN COMBAT CODE YET
def mightyBlow(target, crit_chance):
	if target.family != "God":
		crit_roll = random.randint(1,100)
		if crit_roll <= crit_chance:
			target.current_HP = 0
			target.lives -= 1
			print("Mighty blow! %s fell." % target.name)
			return True
		else:
			return False
	else:
		return False

def applyDamage(damage, target):
	target.current_HP -= damage
	# Damage to a sleeping target gives it a chance to wake up
	if target.isAsleep():
		roll = random.randint(1,100)
		if roll <= 30:
			print("%s woke up." % target.name)
			target.asleep = "n"
			target.stopped = "y"

	if target.current_HP <= 0:
		applyCondition("Stun", target, False)
		return 1
	else:
		return 0

def rollDamage(command, attacker):
	stat = command.stat
	multiplier = command.multiplier
	element = command.element

	if stat == "Str":
		damage = calculateDamage(attacker.getStrength(), multiplier)
	# Currently, Blind status will also reduce AGL damage. Leave it or fix it?
	elif stat == "Agl":
		damage = calculateDamage(attacker.getAgility(), multiplier)
		# Blind should not effect DMG, so double it if blinded
		#if attacker.isBlinded():
		#	damage = damage * 2
	elif stat == "Mana":
		# If the MAGI equipped is of the same element as the magic attack, increase the damage
		if attacker.role == "Player" and attacker.magi.startswith(element):
			damage = calculateDamage(attacker.getMana() + 5 + attacker.magi_count, multiplier)
		else:
			damage = calculateDamage(attacker.getMana(), multiplier)
	elif stat == "Phys":
		damage = calculateDamage(attacker.getStrength() + attacker.getAgility(), multiplier)
	elif stat == "Set":
		if isinstance(command.rand_dmg, int) and command.rand_dmg > 0:
			# Robot race bonus to random damage with guns
			if command.race_bonus == attacker.family:
				damage = command.min_dmg + random.randint(0,command.rand_dmg) * 2
			else:
				damage = command.min_dmg + random.randint(0,command.rand_dmg)
		elif command.rand_dmg == "Str":
			damage = command.min_dmg + random.randint(0,attacker.getStrength())
		else:
			damage = command.min_dmg
	# For Martial Arts, mostly. Reducing total uses while changing the starting point for damage calculation should make this more effective early
	# but less powerful late in the weapon's existence
	elif stat == "Uses":
		uses_cap = 30
		mastery_threshold = int(command.uses - uses_cap)
		if command.remaining > mastery_threshold:
	  		damage = (command.min_dmg - command.remaining) * multiplier
		else:
			damage = mastery_threshold * multiplier
			mastery_roll = random.randint(1,100)
			mastery_chance = mastery_threshold - command.uses
			if mastery_roll <= mastery_chance:
				print("Mastery unlocked!")
				damage = int(damage * 1.5)
	else:
		damage = 0

	# Check Humans for masteries. 10% damage multiplier per level (humanBonus/50)
	if attacker.family == "Human" and attacker.role == "Player":
		damage = int(damage * (1+(int(attacker.humanBonus(command.symbol))/50)))
		
	return damage

def calculateDamage(stat, multiplier):
	atk_power = stat * multiplier + random.randint(0, stat)
	return atk_power

def determineDefense(defender, attack, damage):
	if "Pierce" in attack.effect:
		return 0
	# Workaround to avoid having to pass target into rollDamage function just for the HP attacks
	elif attack.stat == "HP":
		return int(defender.HP * attack.percent/100) * -1
	# For melee and non-elemental ranged attacks, use Defense
	elif attack.att_type == "Melee" or (attack.att_type == "Ranged" and attack.element == "None"):
		return defender.getDefense() * 5
	# For magic attacks or elemental ranged attacks (which is a workaround to allow for blockable "magic" attacks), use Mana
	elif attack.att_type == "Magic" or (attack.att_type == "Ranged" and attack.element != "None"):
#		return int((200 - defender.getMana()) * damage / 200)
		return int(damage * defender.getMana() / 200)

def actConfused(attacker, commands, players):
	options = []
	conf_command = 0
	remaining_uses = 100

	for skill in range(len(attacker.skills)):
		if attacker.skills[skill] != "blank" and commands.loc[attacker.skills[skill],"Target Type"] != "None":
			options.append(attacker.skills[skill])

	while conf_command == 0:
		conf_command = 1
		confuse_command_roll = random.randint(0, len(options)-1)

		# Check PC in case ability was expired during combat
		if attacker.role in ("Player", "NPC"):
			remaining_uses = players.loc[attacker.name, "S%d Uses Left" % confuse_command_roll]
			if remaining_uses <= 0:
				conf_command = 0
			else:
				return options[confuse_command_roll]
		else:
			return options[confuse_command_roll]


#######################################
####### BUFF AND HEAL FUNCTIONS #######
#######################################

def rollHeal(command, healer, ally):
	if command.att_type == "Magic":
		heal = (healer.getMana() + ally.getMana()) * command.multiplier + random.randint(0, healer.getMana())
	else:
		heal = command.min_dmg + random.randint(0,command.rand_dmg)
	if ally.isTargetable():
		heal = applyHeal(heal, ally)
		print("%s recovers %d HP." % (ally.name, heal), end = " ")
	else:
		print("No effect.", end = " ")

def applyHeal(heal, target):
	if (target.current_HP + heal) > target.HP:
		heal = target.HP - target.current_HP
		target.current_HP = target.HP
	else:
		target.current_HP += heal
	return heal

def affectStat(target, command, caster_mana):
	# Change stat to use last three chars of Effect string
	split_str = command.effect.split()
	effect = split_str[0]
	stat = split_str[1]
	rand = random.randint(0, command.rand_dmg)
	amount = command.min_dmg + rand
	
	if effect == "Debuff":
		debuff_chance = random.randint(1,100)
		debuff_check = 2 * (caster_mana - target.getMana()) + 70

		if debuff_chance > debuff_check:
			print("Resisted.", end = " ")
			return
		else:
			amount = amount * -1
	if stat == "Str":
		if target.current_Str <= abs(amount) and effect == "Debuff":
			amount = target.current_Str*-1
		target.current_Str += amount
	elif stat == "Agl":
		if target.current_Agl <= abs(amount) and effect == "Debuff":
			amount = target.current_Agl*-1
		target.current_Agl += amount
	elif stat == "Mana":
		if target.current_Mana <= abs(amount) and effect == "Debuff":
			amount = target.current_Mana*-1
		target.current_Mana += amount
	elif stat == "Def":
		if target.current_Def <= abs(amount) and effect == "Debuff":
			amount = target.current_Def*-1
		target.current_Def += amount
	
	if effect == "Debuff":
		print("%s's %s decreases by %d." % (target.name, stat, amount*-1), end = " ")
	else:
		print("%s's %s increases by %d." % (target.name, stat, amount), end = " ")
	return target

################################
####### STATUS FUNCTIONS #######
################################

def inflictCondition(command, attacker, target, output):
	if command.status == "Stop":
		stop_roll = random.randint(1, 100) - attacker.current_Str + target.current_Str
		if stop_roll <= command.percent:
			applyCondition(command.status, target, output)
			return 1
		else:
			if output:
				print("%s resisted %s." % (target.name, command.status), end = " ")
			return 0
	
	# Originally (target - attacker) * 2 + 50
	# Bonus chance to land Status if the attack has no damage component
	if command.stat == "Status":
		base_chance = 65
	else:
		base_chance = 50
	hit_chance = (attacker.getMana() - target.getMana())*2 + base_chance
	roll = random.randint(1,100)
	if roll <= hit_chance:
		applyCondition(command.status, target, output)
		return 1
	else:
		if output:
			print("%s resisted %s." % (target.name, command.status), end = " ")
		return 0

def applyCondition(status, target, output):
	if status == "Stone":
		target.stoned = "y"
	#	target.blinded = "n" # Remove setting Blind to N for Blind to persist?
		target.poisoned = "n"
		target.confused = "n"
		target.paralyzed = "n"
		target.asleep = "n"
	#	target.cursed = "n" # Remove setting Cursed to N for Cursed to persist?
		if output:
			print("Turned %s to stone." % target.name, end = " ")
	elif status == "Curse":
		target.cursed = "y"
		if output:
			print("Cursed %s." % target.name, end = " ")
	elif status == "Blind":
		target.blinded = "y"
		if output:
			print("Blinded %s." % target.name, end = " ")
	elif status == "Sleep":
		target.asleep = "y"
		if output:
			print("Put %s to sleep." % target.name, end = " ")
	elif status == "Paralyze":
		target.paralyzed = "y"
		if output:
			print("Paralyzed %s." % target.name, end = " ")
	elif status == "Poison":
		target.poisoned = "y"
		if output:
			print("Poisoned %s." % target.name, end = " ")
	elif status == "Confuse":
		target.confused = "y"
		if output:
			print("Confused %s." % target.name, end = " ")
	elif status == "Fear":
		target.afraid = "y"
		if output:
			print("Terrified %s." % target.name, end = " ")
	elif status == "Stun":
		target.current_HP = 0
		target.lives -= 1
	#	target.blinded = "n" # Should Blind persist past death?
		target.poisoned = "n"
		target.confused = "n"
		target.paralyzed = "n"
		target.asleep = "n"
	#	target.cursed = "n" # Should Curse persist past death?
		if output:
			print("%s fell." % target.name, end = " ")
	elif status == "Stop":
		#target.command = "None"
		target.stopped = "y"
		print("Stopped %s." % target.name, end = " ")

def removeCondition(status, target):
	if status == "Stone" and target.isStoned():
		target.stoned = "n"
		print("Softened %s." % target.name, end = " ")
	elif status == "Curse" and target.isCursed():
		target.cursed = "n"
		print("Released %s from curse." % target.name, end = " ")
	elif status == "Blind" and target.isBlinded():
		target.blinded = "n"
		print("Restored sight to %s." % target.name, end = " ")
	elif status == "Sleep" and target.isAsleep():
		target.asleep = "n"
		print("Woke %s." % target.name, end = " ")
	elif status == "Paralyze" and target.isParalyzed():
		target.paralyzed = "n"
		print("Released %s from paralysis." % target.name, end = " ")
	elif status == "Poison" and target.isPoisoned():
		target.poisoned = "n"
		print("Neutralized %s's poison." % target.name, end = " ")
	elif status == "Confuse" and target.isConfused():
		target.confused = "n"
		print("Returned %s to sanity." % target.name, end = " ")
	elif status == "Fear" and target.isAfraid():
		target.afraid = "n"
		print("Calmed %s down." % target.name, end = " ")
	elif status == "Revive" and target.isDead():
		target.current_HP = 1
		target.lives += 1
		print("Revived %s." % target.name, end = " ")
	elif status == "Full Restore" and target.characterStatus():
		target.stoned = "n"
		target.blinded = "n"
		target.poisoned = "n"
		target.confused = "n"
		target.paralyzed = "n"
		target.asleep = "n"
		target.cursed = "n"
		target.afraid = "n"
		print("%s was restored." % target.name, end = " ")
	else:
		print("No effect on %s." % target.name, end = " ")

####################################
####### RESISTANCE FUNCTIONS #######
####################################

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

def checkResistance(target, element, barriers):
	total_resists = barriers.copy()
	total_resists.extend(target.resists)

	# Check the total list for the resistance in question
	for count in range(len(total_resists)):
		if total_resists[count] in element and total_resists[count] != "None":
			return True
		elif element == "Light" and target.family != "Undead":
			return True
		elif element == "Death" and target.family == "Undead":
			return True
	
	# If no resistance was found
	return False

def separateResists(check, resist_table):
	# Only take the element field if the check is against armor, traits, or MAGI
	element = resist_table.loc[check, "Element"]
	if (resist_table.loc[check, "Type"] in ("Armor", "Trait", "MAGI", "Shield")) and (element != "None"):
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
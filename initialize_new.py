import pandas
import random
import operator
import openpyxl
from collections import Counter
from classes import Player, Enemy, NPC, Actor, Command
from combat import (randomTarget, battleStatus, afterTurn, frontOfGroup, groupAttack, rollDamage, determineDefense, affectStat, rollHeal,
inflictCondition, checkResistance, endOfTurn, buildResistances, checkWeakness, applyDamage, counterAttack, removeCondition)

path1 = r"FFL2 Data.xlsx"
path2 = r"Battle Log.xlsx"
path3 = r"Battle Results.xlsx"

workbook = pandas.ExcelFile(path1)
log = pandas.ExcelFile(path2)
writer = pandas.ExcelWriter(path3, engine = 'openpyxl')

monsters = workbook.parse("Monster", index_col = 'Index')
commands = workbook.parse("Weapon", index_col = 'Index')
ms_prob = workbook.parse("Move Probability")

# Loop through each sheet of the battle log, appending each to the battles list
battles = []
save_list = []

for count in range(len(log.sheet_names)):
	if count == 0:
		players = log.parse("Players", index_col = 'Index')
	else:
		battles.append(log.parse(count))

# Remove NaN entries from certain sheets and columns
monsters.fillna("blank", inplace = True)
commands["Element"].fillna("None", inplace = True)
commands["Status"].fillna("None", inplace = True)
commands["Effect"].fillna("None", inplace = True)
commands["Target Type"].fillna("None", inplace = True)
players.fillna("blank", inplace = True)
for each in range(len(battles)):
	battles[each]["COMMAND"].fillna('nan', inplace=True)
	battles[each]["CURRENT HP"].fillna(-1, inplace=True)
	battles[each]["CURRENT STR"].fillna(-1, inplace=True)
	battles[each]["CURRENT AGL"].fillna(-1, inplace=True)
	battles[each]["CURRENT MANA"].fillna(-1, inplace=True)
	battles[each]["CURRENT DEF"].fillna(-1, inplace=True)

run_sim = "y"
while run_sim != "n":

	# This is where a function for creating the combatants list from a battle should be. Call would pass an int to say from which Log sheet to pull
	# Might even pass the sheet itself from battles[]. Would return combatants list
	combatants = []
	enemy_groups = []

	for bat in range(len(battles)):
		print("%d. %s" % (bat+1, log.sheet_names[bat+1]))
	i = int(input("Which battle do you want to run? Enter a number: "))

	# Setting to the list index of the number chosen
	print("Executing Battle: %s" % log.sheet_names[i])
	i=i-1

	# Need to track the right spot in combatants, which conflicts with 'count' due to enemy "lives" inflating the list vs the Log
	place = 0

	# Populate the Combatants list
	# I would prefer to be doing label lookups with Pandas loc instead of iloc, but I can't get the indexing right (at load time)
	actor_count = len(battles[i].index)
	for count in range(actor_count):
		# Enemy groups require a for loop to create individual Actors for tracking initiative, deaths, etc.
		if battles[i].iloc[count,1] == "Enemy":
			if pandas.isnull(battles[i].iloc[count,3]):
				for pos in range(int(battles[i].iloc[count,2])):
					combatants.append(Enemy(battles[i].iloc[count,0]))
					combatants[place].position = pos + 1
					combatants[place].lives = 1
					combatants[place].group = count
					enemy_groups.append(tuple((combatants[place].name, 0, 0)))
					copy_row = battles[i].iloc[count]
					battles[i].loc[len(battles[i].index)] = copy_row
					place += 1
				battles[i].drop(battles[i].tail(1).index,inplace=True)
			else:
				combatants.append(Enemy(battles[i].iloc[count,0]))
				combatants[count].position = battles[i].iloc[count,3]
				combatants[count].lives = battles[i].iloc[count,2]
				combatants[count].group = count
				enemy_groups.append(tuple((combatants[count].name, 0, 0)))

		elif battles[i].iloc[count,1] == "Player":
			combatants.append(Player(battles[i].iloc[count,0]))
			combatants[count].position = int(battles[i].iloc[count,3])
			combatants[place].group = count
			place += 1

		else:
			combatants.append(NPC(battles[i].iloc[count,0]))
			combatants[count].position = battles[i].iloc[count,3]
			combatants[place].group = count
			place += 1

	# Create a unique list of enemy groups
	enemy_groups = set(enemy_groups)
	enemy_groups = list(enemy_groups)

	# DATA ASSIGNMENT LOOP
	# Ridiculously big loop to go through combatants list, assign static values
	for count in range(len(combatants)):
		current_com = combatants[count]

		current_com.current_HP = battles[i].iloc[current_com.group, 5]
		current_com.current_Str = battles[i].iloc[current_com.group, 6]
		current_com.current_Agl = battles[i].iloc[current_com.group, 7]
		current_com.current_Mana = battles[i].iloc[current_com.group, 8]
		current_com.current_Def = battles[i].iloc[current_com.group, 9]
		current_com.command = battles[i].iloc[current_com.group, 10]
		current_com.target_type = battles[i].iloc[current_com.group, 11]
		current_com.stoned = battles[i].iloc[current_com.group, 12]
		current_com.cursed = battles[i].iloc[current_com.group, 13]
		current_com.blinded = battles[i].iloc[current_com.group, 14]
		current_com.stunned = battles[i].iloc[current_com.group, 15]
		current_com.asleep = battles[i].iloc[current_com.group, 16]
		current_com.paralyzed = battles[i].iloc[current_com.group, 17]
		current_com.poisoned = battles[i].iloc[current_com.group, 18]
		current_com.confused = battles[i].iloc[current_com.group, 19]
	
		# Lookup the static Enemy data
		if current_com.role == "Enemy":
			current_com.DS = monsters.loc[current_com.name,"DS"]
			current_com.MS = monsters.loc[current_com.name,"MS"]
			current_com.Type = monsters.loc[current_com.name,"Type"]
			current_com.HP = monsters.loc[current_com.name,"HP"]
			current_com.Str = monsters.loc[current_com.name,"Str"]
			current_com.Agl = monsters.loc[current_com.name,"Agl"]
			current_com.Mana = monsters.loc[current_com.name,"Mana"]
			current_com.Def = monsters.loc[current_com.name,"Def"]
			current_com.family = monsters.loc[current_com.name,"Family"]
	
			#There should be a better way to do this...but here's the lazy way
			current_com.skills.append(monsters.loc[current_com.name,"S0"])
			current_com.skills.append(monsters.loc[current_com.name,"S1"])
			current_com.skills.append(monsters.loc[current_com.name,"S2"])
			current_com.skills.append(monsters.loc[current_com.name,"S3"])
			current_com.skills.append(monsters.loc[current_com.name,"S4"])
			current_com.skills.append(monsters.loc[current_com.name,"S5"])
			current_com.skills.append(monsters.loc[current_com.name,"S6"])
			current_com.skills.append(monsters.loc[current_com.name,"S7"])

		# Lookup the static player data
		elif current_com.role == "Player":
			current_com.Class = players.loc[current_com.name,"CLASS"]
			current_com.family = monsters.loc[current_com.Class,"Family"]
			current_com.HP = players.loc[current_com.name,"HP"]
			current_com.Str = players.loc[current_com.name,"STR"]
			current_com.Agl = players.loc[current_com.name,"AGL"]
			current_com.Mana = players.loc[current_com.name,"MANA"]
			current_com.Def = players.loc[current_com.name,"DEF"]
		
			#There should be a better way to do this...but here's the lazy way
			current_com.skills.append(players.loc[current_com.name,"S0"])
			current_com.skills.append(players.loc[current_com.name,"S1"])
			current_com.skills.append(players.loc[current_com.name,"S2"])
			current_com.skills.append(players.loc[current_com.name,"S3"])
			current_com.skills.append(players.loc[current_com.name,"S4"])
			current_com.skills.append(players.loc[current_com.name,"S5"])
			current_com.skills.append(players.loc[current_com.name,"S6"])
			current_com.skills.append(players.loc[current_com.name,"S7"])

		# Should be NPC code, but no separate sheet for that yet
		else:
			break

		# Determine resists based on active inventory
		buildResistances(current_com.skills, current_com.resists, commands)

	rd = 0
	another_round = "y"
	# EXECUTE COMBAT ROUND
	while another_round == "y":
		rd += 1
		print("~~~ Round %d ~~~" % (rd))
		# SET CURRENT STATS (in Round 1 only), ROLL INITIATIVE, AND SORT
		if rd == 1:
			for count in range(len(combatants)):
				if combatants[count].current_HP == -1:
					combatants[count].current_HP = combatants[count].HP
				else:
					combatants[count].current_HP = combatants[count].current_HP
				combatants[count].current_Str = combatants[count].Str if combatants[count].current_Str == -1 else combatants[count].current_Str
				combatants[count].current_Agl = combatants[count].Agl if combatants[count].current_Agl == -1 else combatants[count].current_Agl
				combatants[count].current_Mana = combatants[count].Mana if combatants[count].current_Mana == -1 else combatants[count].current_Mana
				combatants[count].current_Def = combatants[count].Def if combatants[count].current_Def == -1 else combatants[count].current_Def

			# SURPRISE CHECK FOR ROUND 1

		# INITIATIVE
		for count in range(len(combatants)):
			variable = (1+(random.randint(1,25)/100))
			combatants[count].initiative = float(combatants[count].current_Agl) * variable

		# Sort actors based on initiative score
		combatants = sorted(combatants, key = operator.attrgetter("initiative"), reverse=True)

		# Create party formation
		party_order = []
		for count in range(len(combatants)):
			if combatants[count].role in ("Player", "NPC"):
				party_order.append(tuple((combatants[count].name, combatants[count].position, count)))
		party_order = sorted(party_order, key = operator.itemgetter(1), reverse=False)

		# Create barrier lists anew each round
		enemy_barriers = []
		player_barriers = []

		# COMMAND SELECTION
		for count in range(len(combatants)):
			attacker = combatants[count]

			# STATUS CHECK
			if not attacker.isActive():
				continue

			# CONFUSION CHECK
			if attacker.isConfused():
				options = []
				for skill in range(len(attacker.skills)):
					if attacker.skills[skill] != "blank" and commands.loc[attacker.skills[skill],"Target Type"] != "None":
						options.append(attacker.skills[skill])
				confuse_command_roll = random.randint(0, len(options)-1)
				attacker.command = options[confuse_command_roll]

			# ENEMY COMMAND SELECTION - uses Move Probability table based on MS
			# Could also be used for random ability selection for players if an appropriate MS were assigned
			# May want to add one for when MS exists, another for completely random if it doesn't (or always pick top command)
			if attacker.command == 'nan':
				row = attacker.MS
				roll = random.randint(0,255)
				for choice in range(7):
					if roll <= ms_prob.iloc[int(row), choice+1]:
						attacker.command = attacker.skills[choice]
						break
					else:
						continue

			##########################
			# May need logic here for commands that trigger immediately at the start of a round (e.g. shield barriers)
			##########################
			if (commands.loc[attacker.command, "Target Type"] == "Block" and commands.loc[attacker.command, "Effect"] != "None"):
				if attacker.role == "Enemy":
					enemy_barriers.append(commands.loc[attacker.command, "Effect"])
				else:
					player_barriers.append(commands.loc[attacker.command, "Effect"])

		# TARGETING AND COMMAND EXECUTION
		for count in range(len(combatants)):
			attacker = combatants[count]

			# STATUS CHECK
			if not attacker.isActive():
				continue

			sel_target = ""

			# CONFUSED TARGETING
			if attacker.isConfused():
				confuse_roll = random.randint(1,90)
				if confuse_roll > 10:
					print("%s is confused." % attacker.name, end = " ")
					attacker.target_type = commands.loc[attacker.command, "Target Type"]
					confuse_targets = party_order + enemy_groups
					if attacker.target_type in ("Single", "Group", "Ally"):
						sel_target = randomTarget(confuse_targets, combatants)
						attacker.add_target(sel_target)
					# Should barriers be applied to the enemies if the confusion targets the other side? If so, need to change barrier logic
					elif attacker.target_type == "Block":
						print("%s is defending with %s." % (attacker.name, attacker.command), end = " ")
						if commands.loc[attacker.command, "Effect"] != "None":
							print("A barrier covered the party.")
						else:
							print("")
						combatants[count] = afterTurn(attacker)
						continue
					elif attacker.target_type in ("Counter", "Reflect"):
						print("%s is waiting for the attack." % attacker.name)
						combatants[count] = afterTurn(attacker)
						continue
					elif attacker.target_type == "All":
						for each in range(len(enemy_groups)):
							attacker.targets.append(enemy_groups[each][0])
						for each in range(len(party_order)):
							attacker.targets.append(party_order[each][0])
					elif attacker.target_type == "Self":
						attacker.add_target(attacker.name)
					elif attacker.target_type in ("All Enemies", "Allies"):
						sel_target = randomTarget(confuse_targets, combatants)
						which_side = ""
						for who in range(len(combatants)):
							if combatants[who].name == sel_target:
								which_side = combatants[who].role
								break
						if which_side in ("Player, NPC"):
							for each in range(len(party_order)):
								attacker.targets.append(party_order[each][0])
						else:
							for each in range(len(enemy_groups)):
								attacker.targets.append(enemy_groups[each][0])
				else:
					print("%s regained sanity." % attacker.name)
					attacker.command = "None"
					attacker.confused = "n"
					continue
				
			# Find an actual target based on Target Type, where applicable (i.e. not the "All" abilities)
			elif attacker.role != "Player":

				# Based on the Command, assign the Target Type to the Target line
				attacker.target_type = commands.loc[attacker.command, "Target Type"]

				if attacker.target_type == "Single":
					for choice in range(len(party_order)):
						roll = random.randint(1,100)
						if roll < 51 and combatants[party_order[choice][2]].isTargetable():
							sel_target = party_order[choice][0]
					# If a target isn't selected via the weighted method...
					if sel_target == "":
						sel_target = randomTarget(party_order, combatants)
					attacker.add_target(sel_target)

				# Blocking effects happen at start of turn. This is an announcement of the ability's usage on the character's turn
				elif attacker.target_type == "Group":
					sel_target = randomTarget(party_order, combatants)
					attacker.add_target(sel_target)

				elif attacker.target_type == "Block":
					print("%s is defending with %s." % (attacker.name, attacker.command), end = " ")
					if commands.loc[attacker.command, "Effect"] != "None":
						print("A barrier covered the enemies.")
					else:
						print("")
					combatants[count] = afterTurn(attacker)
					continue
				# Counter and reflect effects happen at start of turn. This is an announcement of the ability's usage on the character's turn
				elif attacker.target_type in ("Counter", "Reflect"):
					print("%s is waiting for the attack." % attacker.name)
					combatants[count] = afterTurn(attacker)
					continue
				elif attacker.target_type == "All Enemies":
					for each in range(len(party_order)):
						attacker.add_target(party_order[each][0])
				# Enemy healers will always target the ally that has taken the most damage
				elif attacker.target_type == "Ally":
					target_name = ""
					damage_to_lead = 0
					for each in range(len(combatants)):
						if combatants[each].role == attacker.role:
							damage_taken = combatants[each].HP - combatants[each].current_HP
							if damage_taken > damage_to_lead:
								damage_to_lead = damage_taken
								target_name = combatants[each].name
					attacker.targets.append(target_name)
				elif attacker.target_type == "Allies":
					for each in range(len(enemy_groups)):
						attacker.targets.append(enemy_groups[each][0])
				elif attacker.target_type == "All":
					for each in range(len(enemy_groups)):
						attacker.targets.append(enemy_groups[each][0])
					for each in range(len(party_order)):
						attacker.targets.append(party_order[each][0])
				elif attacker.target_type == "Self":
					attacker.add_target(attacker.name)
				else:
					print("Invalid target!")
					break

			# PC TARGET SETTING
			else:
				temp_target = commands.loc[attacker.command, "Target Type"]
				if temp_target in ("Single", "Group", "Ally"):
					attacker.add_target(attacker.target_type)
				elif temp_target == "Self":
					attacker.add_target(attacker.name)
				elif temp_target == "Block":
					print("%s is defending with %s." % (attacker.name, attacker.command), end = " ")
					if commands.loc[attacker.command, "Effect"] != "None":
						print("A barrier covered the party.")
					else:
						print("")
					combatants[count] = afterTurn(attacker)
					continue
				# May need logic to set a counter/reflect flag at beginning of a round so not every attack or spell is countered
				elif temp_target in ("Counter", "Reflect"):
					print("%s is waiting for the attack." % attacker.name)
					combatants[count] = afterTurn(attacker)
					continue
				elif temp_target == "All Enemies":
					for each in range(len(enemy_groups)):
						attacker.targets.append(enemy_groups[each][0])
				elif temp_target == "Allies":
					for each in range(len(party_order)):
						attacker.targets.append(party_order[each][0])
				elif temp_target == "All":
					for each in range(len(enemy_groups)):
						attacker.targets.append(enemy_groups[each][0])
					for each in range(len(party_order)):
						attacker.targets.append(party_order[each][0])
				else:
					print("Invalid target!")
					break

			# Construct the command class for this instance
			command = Command(attacker.command, commands)

			# Cycle through targets for attacks
			for foe in range(len(attacker.targets)):
				# Select the front-most member of a group with the same name (i.e. attack the front-most enemy of a group)
				# FUNCTION ONLY CALLED ONCE. MOVE IT BACK?
				defender = frontOfGroup(combatants, count, foe)

				# Defender == 100 means that group is gone. Go to the next foe
				if defender == 100:
					if foe == 0 and command.targeting == "All Enemies":
						print("%s attacks all enemies with %s." % (attacker.name, attacker.command))
					elif command.targeting not in ("All Enemies", "Allies", "All"):
						print("%s attacks with %s. Ineffective." % (attacker.name, command.name))
					continue

				# Combat parameters
				barriers = []
				target = combatants[defender]
				if target.command != "None":
					def_target_type = commands.loc[target.command, "Target Type"]
					def_command_effect = commands.loc[target.command, "Effect"]
				blocked = False
				blockable = False
				dmg_reduction = False
				critical_hit = False

				if command.targeting == "Single":
					# HIT LOGIC
					# Need:  Target Agility, Target Blind status, Speed Magi, Target command (does item provide a block)
					# Need:  Attacker Agility
					# Calc:  Defender score - 2x Attacker.AGL, then 97 - the result
					print("%s attacks %s with %s." % (attacker.name, target.name, attacker.command), end = " ")
					attacker_hit = attacker.current_Agl
					defender_score = target.current_Agl

					# Account for blindness
					if attacker.isBlinded():
						attacker_hit = round(attacker_hit / 2)
					if target.isBlinded():
						defender_score = round(defender_score / 2)

					# Need MAGI logic here

					# Blockable logic
					if command.att_type in ("Melee", "Ranged"):
						blockable = True
					if (def_target_type == "Block" or def_command_effect == "Block") and blockable:
						block_roll = random.randint(1,100)
						if block_roll <= (commands.loc[target.command, "Percent"] + defender_score):
							blocked = True

					# Reflect - change target into the attacker
					if (def_command_effect == "Reflect" or def_target_type == "Reflect") and command.att_type == "Magic":
						print("%s reflected the attack." % target.command)
						# Makes the attacker into the target of its own spell
						target = attacker

					# Nullify - end the attack since it was nullified on target
					if (def_command_effect == "Nullify" or def_target_type == "Nullify") and command.att_type == "Magic":
						print("%s repulsed the attack." % target.command)
						continue

					# Check for barriers and their effects
					if target.role == "Enemy":
						buildResistances(enemy_barriers, barriers, commands)
					else:
						buildResistances(player_barriers, barriers, commands)
					
					# Check total resists
					if checkResistance(target.resists, command.element, command.status, barriers):
						# Elemental resistance was found, but it's a melee attack so it can't be resisted
						if command.element != "None" and command.att_type in ("Melee", "Ranged"):
							dmg_reduction = True
						else:
							print("%s is strong against %s." % (attacker.targets[foe], command.name))
							continue
					else:
						# Check for elemental / species weakness
						if command.element != "None":
							if checkWeakness(command.element, target):
								print("Hits weakness.", end = " ")
								crit_roll = random.randint(1,100)
								if crit_roll <= 30:
									target.current_HP = 0
									target.lives -= 1
									print("Mighty blow! %s fell." % target.name)
									continue
								else:
									critical_hit = True

					difference = defender_score - attacker_hit*2
					hit_chance = 97 - difference

					hit_roll = random.randint(1,100)
					if hit_roll > hit_chance:
						print("Missed!")
					# Melee attacks get blocked fully (even status-based ones)
					elif (blocked == True and command.att_type == "Melee"):
						print("%s defended against %s with %s." % (target.name, attacker.command, target.command))
					# Should ALL Stone effects be blocked by a shield? Doesn't make sense with things like StoneGas...

					# DAMAGE ASSIGNMENT
					else:
						if command.status != "None":
							inflictCondition(command, attacker, target)
						offense = rollDamage(command, attacker)
						defense = determineDefense(target, command.att_type, offense)
						damage = offense - defense
						# Ranged attacks get blocked for 50% damage
						if blocked == True:
							damage = round(damage/2)
						# If weapon resistance is found against a non-magical attack, damage is halved
						if command.att_type in ("Melee", "Ranged") and checkResistance(target.resists, "Weapon", command.status, barriers):
							damage = round(damage/2)
						if critical_hit == True:
							damage = round(damage*1.5)

						# No damage on pure Status attacks
						if command.stat == "Status":
							pass
						elif damage <= 0:
							damage = 0
							print("No damage.")
						else:
							print("%d damage to %s." % (damage, attacker.targets[foe]))
							if applyDamage(damage, target) == 1:
								print("%s fell." % target.name)

						# Counter-attacks if any exist and the target survived
						if target.isActive() and (def_target_type == "Counter" or def_command_effect == "Counter"):
							counter_command = Command(target.command, commands)
							if target.role == "Enemy":
								buildResistances(player_barriers, barriers, commands)
							else:
								buildResistances(enemy_barriers, barriers, commands)
							counterAttack(target, attacker, counter_command, damage, barriers)

				elif command.targeting in ("Group", "All Enemies"):
					if command.targeting == "Group":
						print("%s attacks %s group with %s." % (attacker.name, attacker.targets[foe], attacker.command), end = " ")
					else:
						# Only print the command text the first time through
						# FOR SOME REASON STOPS WORKING ON ALL ENEMY ATTACKS WHEN FIRST TARGET IS STONE
						if foe == 0:
							print("%s attacks all enemies with %s." % (attacker.name, attacker.command))

					# Reflect - change target into the attacker
					if (def_command_effect == "Reflect" or def_target_type == "Reflect") and command.att_type == "Magic":
						print("%s reflected the attack." % target.command)
						target = attacker

					# Nullify - end the attack since it was nullified on target
					if (def_command_effect == "Nullify" or def_target_type == "Nullify") and command.att_type == "Magic":
						print("%s repulsed the attack." % target.command)
						continue

					# Check resistances
					if target.role == "Enemy":
						buildResistances(enemy_barriers, barriers, commands)
					else:
						buildResistances(player_barriers, barriers, commands)
					if checkResistance(target.resists, command.element, command.status, barriers):
						print("%s is strong against %s." % (target.name, command.name))
						continue
					else:
						if command.status != "None":
							for who in range(len(combatants)):
								if combatants[who].name == target.name and combatants[who].isTargetable():
									inflictCondition(command, attacker, combatants[who])
						offense = rollDamage(command, attacker)
						defense = determineDefense(target, command.att_type, offense)

						# Check for elemental / species weakness
						if command.element != "None":
							if checkWeakness(command.element, target):
								print("Hits weakness.", end = " ")
								if command.att_type == "Magic":
									defense = 0
								else:
									critical_hit = True
						
						damage = offense - defense

						if command.att_type in ("Melee", "Ranged") and checkResistance(target.resists, "Weapon", command.status, barriers):
							damage = round(damage/2)
						if critical_hit:
							damage = damage * 1.5

					# No damage on pure Status attacks
					if command.stat == "Status":
						pass
					elif damage <= 0:
						damage = 0
						print("No damage.")
					else:
						# Loop through combatants to deal damage to all members of a group
						# ONLY GETS USED ONCE. MOVE BACK?
						groupAttack(combatants, target.name, damage)

				elif command.targeting == "Ally":
					print("%s uses %s for %s." % (attacker.name, attacker.command, attacker.targets[foe]), end = " ")
					if command.effect == "Heal":
						rollHeal(command, attacker, target)
					elif command.effect == "Buff":
						target = affectStat(target, command.effect, command.min_dmg)
						print("%s increases by %d." % (command.effect, command.min_dmg))
					elif command.status != "None":
						removeCondition(command.status, target)
			
				elif command.targeting == "Self":
					if command.att_type == "Buff":
						attacker = affectStat(attacker, command.effect, command.min_dmg)
						print("%s uses %s." % (attacker.name, attacker.command), end = " ")

				elif command.targeting == "Allies":
					if foe == 0:
						print("%s uses %s." % (attacker.name, attacker.command))
					for who in range(len(combatants)):
						if combatants[who].name == attacker.targets[foe]:
							if command.effect == "Heal":
								rollHeal(command, attacker, combatants[who])
							elif command.effect == "Buff":
								print("%s's" % combatants[who], end = " ")
								combatants[who] == affectStat(combatants[who], command.effect, command.min_dmg)
							elif command.status != "None":
								removeCondition(command.status, combatants[who])

			# Post-action tracking
			combatants[count] = afterTurn(attacker)
			if not battleStatus(combatants):
				another_round = "n"
				break
		for each in range(len(combatants)):
			combatants[each] = endOfTurn(combatants[each])
			# Should only be needed for "Regained sanity" purposes...
			if combatants[each].role == "Player" and combatants[each].command == "None":
				combatants[each].command = battles[i].loc[attacker.name, "COMMAND"]
				combatants[each].target_type = battles[i].loc[attacker.name, "TARGET"]
		if another_round != "n":
			another_round = input("Run another round (y/n)?: ")

	# Print party status line at the end of a simulation
	for each in range(len(party_order)):
		for count in range(len(combatants)):
			if combatants[count].name == party_order[each][0]:
				print("| %s: %d/%d %s" % (combatants[count].name, combatants[count].current_HP, combatants[count].HP, combatants[count].characterStatus()), end = " |")

	# Need only for endline during testing phase
	print("")

	# Print enemy status line at the end of a simulation
	enemy_list = []
	for count in range(len(combatants)):
		if (combatants[count].role == "Enemy" and combatants[count].isActive()):
			enemy_list.append(combatants[count].name)

	remaining_enemies = Counter(enemy_list)
	remaining_enemies.keys()
	for key, number in remaining_enemies.items():
		print("{ %s - %d" % (key, number), end = " }")
	print("")
	
#	for count in range(len(combatants)):
#		print(combatants[count])
#	print(battles[i])

	write_to_excel = input("Save battle? (y/n): ")
	if write_to_excel == "y":
		for count in range(len(combatants)):
			battles[i].iloc[count,0] = combatants[count].name
			battles[i].iloc[count,1] = combatants[count].role
			battles[i].iloc[count,2] = combatants[count].lives
			battles[i].iloc[count,3] = combatants[count].position
			battles[i].iloc[count,4] = combatants[count].initiative
			battles[i].iloc[count,5] = combatants[count].current_HP
			battles[i].iloc[count,6] = combatants[count].current_Str
			battles[i].iloc[count,7] = combatants[count].current_Agl
			battles[i].iloc[count,8] = combatants[count].current_Mana
			battles[i].iloc[count,9] = combatants[count].current_Def
			battles[i].iloc[count,12] = combatants[count].stoned
			battles[i].iloc[count,13] = combatants[count].cursed
			battles[i].iloc[count,14] = combatants[count].blinded
			battles[i].iloc[count,16] = combatants[count].asleep
			battles[i].iloc[count,17] = combatants[count].paralyzed
			battles[i].iloc[count,18] = combatants[count].poisoned
			battles[i].iloc[count,19] = combatants[count].confused
#			battles[i].iloc[count,20] = combatants[count].actions_taken
		save_list.append(tuple((i, log.sheet_names[i+1])))

	run_sim = input("Run another battle (y/n)?: ")

#print(save_list)
for bat in range(len(save_list)):
 	battles[save_list[bat][0]].to_excel(writer, sheet_name = save_list[bat][1])

if len(save_list) > 0:
	writer.save()

char_sheets = input("Print character sheets (y/n)?: ")
if char_sheets == "y":
	for count in range(len(players.index)):
		print("CHARACTER: %s  PLAYER: %s" % (players.iloc[count, 0], players.iloc[count, 1]))
		print("CLASS: %s" % players.iloc[count, 2])
		print("HP: %d / STR: %d / DEF: %d / AGL: %d / MANA: %d" % (players.iloc[count, 3],players.iloc[count, 5],players.iloc[count, 7],players.iloc[count, 9],players.iloc[count, 11]))
		print("[", end = "")
		for skill in range(8):
			if skill < 7:
				print(players.iloc[count,skill+12], end = ", ")
			else:
				print(players.iloc[count,skill+12], end = "]\n")
		# Still need MAGI and Inventory
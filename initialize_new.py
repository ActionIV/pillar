import pandas
import random
import operator
from collections import Counter 
from classes import Player, Enemy, NPC, Actor
from combat import randomTarget, battleStatus, calculateDamage, afterTurn

path1 = r"FFL2 Data.xlsx"
path2 = r"Battle Log.xlsx"

workbook = pandas.ExcelFile(path1)
log = pandas.ExcelFile(path2)

monsters = workbook.parse("Monster", index_col = 'Index')
commands = workbook.parse("Weapon", index_col = 'Index')
ms_prob = workbook.parse("Move Probability")
players = workbook.parse("Players", index_col = 'Index')

# Loop through each sheet of the battle log, appending each to the battles list
battles = []

for count in range(len(log.sheet_names)):
	battles.append(log.parse(count, index_col = 'Index', dtype = str))

# This is where a function for creating the combatants list from a battle should be. Call would pass an int to say from which Log sheet to pull
# Might even pass the sheet itself from battles[]. Would return combatants list
combatants = []
enemy_groups = []

for bat in range(len(battles)):
	print("%d. %s" % (bat+1, log.sheet_names[bat]))
i = int(input("Which battle do you want to run? Enter a number: "))

# Setting to the list index of the number chosen
i=i-1
print("Executing Battle: %s" % log.sheet_names[i])

# Need to track the right spot in combatants, which conflicts with 'count' due to enemy "lives" inflating the list vs the Log
place = 0

# I would prefer to be doing label lookups with Pandas loc instead of iloc, but I can't get the indexing right (at load time)
for count in range(len(battles[i].index)):
	# Enemy groups require a for loop to create individual Actors for tracking initiative, deaths, etc.
	if battles[i].iloc[count,1] == "Enemy":
		for pos in range(int(battles[i].iloc[count,2])):
			combatants.append(Enemy(battles[i].iloc[count,0]))
			combatants[place].position = pos + 1
			combatants[place].lives = 1
			combatants[place].group = count
			enemy_groups.append(tuple((combatants[place].name, combatants[place].group)))
			place += 1

	elif battles[i].iloc[count,1] == "Player":
		combatants.append(Player(battles[i].iloc[count,0]))
		combatants[count].position = battles[i].iloc[count,3]
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

	current_com.current_HP = battles[i].loc[current_com.name, "CURRENT HP"]
	current_com.current_Str = battles[i].loc[current_com.name, "CURRENT STR"]
	current_com.current_Agl = battles[i].loc[current_com.name, "CURRENT AGL"]
	current_com.current_Mana = battles[i].loc[current_com.name, "CURRENT MANA"]
	current_com.current_Def = battles[i].loc[current_com.name, "CURRENT DEF"]
	current_com.command = battles[i].loc[current_com.name, "COMMAND"]
	current_com.target_type = battles[i].loc[current_com.name, "TARGET"]
	current_com.stoned = battles[i].loc[current_com.name, "Stoned"]
	current_com.cursed = battles[i].loc[current_com.name, "Cursed"]
	current_com.blinded = battles[i].loc[current_com.name, "Blinded"]
	current_com.stunned = battles[i].loc[current_com.name, "Stunned"]
	current_com.paralyzed = battles[i].loc[current_com.name, "Paralyzed"]
	current_com.poisoned = battles[i].loc[current_com.name, "Poisoned"]
	current_com.confused = battles[i].loc[current_com.name, "Confused"]
	
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
		current_com.Type = players.loc[current_com.name,"TYPE"]
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

rd = 0
rounds = 1
# EXECUTE COMBAT ROUND - should eventually be a repeatable function based on number of rounds to run
while rd < rounds:
	print("~~~ Round %d ~~~" % (rd+1))
	# SET CURRENT STATS (in Round 1 only), ROLL INITIATIVE, AND SORT
	if rd == 0:
		for count in range(len(combatants)):
			combatants[count].current_HP = combatants[count].HP
			combatants[count].current_Str = combatants[count].Str
			combatants[count].current_Agl = combatants[count].Agl
			combatants[count].current_Mana = combatants[count].Mana
			combatants[count].current_Def = combatants[count].Def

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
		if combatants[count].role == ("Player" or "NPC"):
			party_order.append(tuple((combatants[count].name, combatants[count].position, count)))
	party_order = sorted(party_order, key = operator.itemgetter(1), reverse=True)

	# COMMAND SELECTION
	for count in range(len(combatants)):
		attacker = combatants[count]

		# STATUS CHECK
		if attacker.isDead():
			continue

		# ENEMY COMMAND SELECTION - uses Move Probability table based on MS
		# Could also be used for random ability selection for players if an appropriate MS were assigned
		if attacker.command == 'nan':
			row = attacker.MS
			for choice in range(7):
				roll = random.randint(0,255)
				if roll < ms_prob.iloc[int(row), choice+1]:
					attacker.command = attacker.skills[choice]
					break
				else:
					continue

		##########################
		# May need logic here for commands that trigger immediately at the start of a round (e.g. shield barriers)
		##########################

	# TARGETING AND COMMAND EXECUTION
	for count in range(len(combatants)):
		attacker = combatants[count]

		# STATUS CHECK
		if attacker.isDead():
			continue

		# Find an actual target based on Target Type, where applicable (i.e. not the "All" abilities)
		sel_target = ""
		if attacker.role != "Player":

			# Based on the Command, assign the Target Type to the Target line
			attacker.target_type = commands.loc[attacker.command, "Target Type"]

			if (attacker.target_type == "Single") or (attacker.target_type == "Group"):
				for choice in range(len(party_order)):
					roll = random.randint(1,100)
					if roll < 51 and combatants[party_order[choice][2]].isDead() == False:
						sel_target = party_order[choice][0]

	#				elif roll < 51 and combatants[party_order[choice][2]].isDead() == True:

				while sel_target == "":
					random_roll = randomTarget(len(party_order))
					random_who = party_order[random_roll][2]
					if combatants[random_who].isDead() == False:
						sel_target = party_order[random_roll][0]
						break
					else:
						continue

				attacker.add_target(sel_target)

			# elif attacker.target_type == "Group":
			# 	for choice in range(len(party_order)):
			# 		roll = random.randint(1,100)
			# 		if roll < attacker.current_Mana

			elif (attacker.target_type == "All Enemies"):
				for each in range(len(party_order)):
					attacker.add_target(party_order[each][0])

		# PC TARGET SETTING
		else:
			temp_target = commands.loc[attacker.command, "Target Type"]
			if temp_target == ("Single" or "Group"):
				attacker.add_target(attacker.target_type)
			elif temp_target == "Block":
				print("%s is defending with %s." % (attacker.name, attacker.command))
				combatants[count] = afterTurn(attacker)
				continue
			elif temp_target == "Counter":
				print("%s is waiting for the attack." % attacker.name)
				continue
#			elif temp_target == "Group":
#				for tar in range(len(combatants)):
#					if (combatants[tar].role == "Enemy") and (combatants[tar].name == attacker.target_type):
#				attacker.add_target(attacker.target_type)
			elif temp_target == "All Enemies":
				for each in range(len(enemy_groups)):
					attacker.targets.append(enemy_groups[each][0])

		# SINGLE TARGET SELECTION
		priority = 100
		defender = 0
	############################
	# Indent here. May need to cycle through a count of the target list
	############################
		for foe in range(len(attacker.targets)):
			# Select the front-most member of a group with the same name (i.e. attack the front-most enemy of a group)
			for tar in range(len(combatants)):
				if (combatants[tar].name == attacker.targets[foe]) and (int(combatants[tar].position) < priority) and (combatants[tar].isDead() == False):
					priority = combatants[tar].position
					defender = tar

			if commands.loc[attacker.command, "Target Type"] == "Single":
				# HIT LOGIC
				# Need:  Target Agility, Target Blind status, Speed Magi, Target command (does item provide a block)
				# Need:  Attacker Agility
				# Calc:  Defender score - 2x Attacker.AGL, then 97 - the result
				print("%s attacks %s with %s." % (attacker.name, combatants[defender].name, attacker.command))
				attacker_hit = attacker.current_Agl
				defender_score = combatants[defender].current_Agl
				blocked = False
				blockable = False
				if combatants[defender].isBlinded == True:
					defender_score = round(defender_score / 2)
				# Need MAGI logic here
				def_command_type = commands.loc[combatants[defender].command, "Type"]

				# Blockable logic
				if commands.loc[attacker.command, "Type"] == "Melee" or (commands.loc[attacker.command, "Type"] == "Ranged"):
					blockable = True
				if def_command_type == "Shield" and blockable:
					block_roll = random.randint(1,100)
					if block_roll <= (commands.loc[combatants[defender].command, "Percent"] + defender_score):
						blocked = True

				difference = defender_score - attacker_hit*2
				hit_chance = 97 - difference

				hit_roll = random.randint(1,100)
				if hit_roll > hit_chance:
					print("Missed!")
				# If I choose to make blocking make an attack miss the defender...
				elif blocked == True:
					print("%s defended against %s with %s." % (combatants[defender].name, attacker.command, combatants[defender].command))

				# DAMAGE ASSIGNMENT
				else:		
					weapon_multiplier = commands.loc[attacker.command, "Multiplier"]
					damage_stat = commands.loc[attacker.command, "Damage Stat"]

					defense = combatants[defender].current_Def * 5

					if combatants[defender].isCursed == True:
						defense = round(combatants[defender].current_Def / 2)

					if damage_stat == "Str":
						damage = calculateDamage(attacker.current_Str, weapon_multiplier, defense)
					elif damage_stat == "Agl":
						damage = calculateDamage(attacker.current_Agl, weapon_multiplier, defense)
					elif damage_stat == "Mana":
						damage = calculateDamage(attacker.current_Mana, weapon_multiplier, defense)
					# Need more elif for guns, bows, and other static attacks

					# Else will have to handle special attacks later. For now, make damage zero
					else:
						damage = 0

#					if blocked == True:
#						damage = damage / 2
#						print("%s defended against %s with %s." % (combatants[defender].name, attacker.command, combatants[defender].command))

					if damage < 0:
						damage = 0
					print("%d damage to %s." % (damage, attacker.targets[0]))
					combatants[defender].current_HP -= damage
					if combatants[defender].current_HP <= 0:
						combatants[defender].current_HP = 0
						combatants[defender].lives -= 1
						if combatants[defender].isDead():
							print("%s fell." % combatants[defender].name)

			elif commands.loc[attacker.command, "Target Type"] == "Group":
				print("%s attacks %s group with %s." % (attacker.name, attacker.targets[foe], attacker.command))
				weapon_multiplier = commands.loc[attacker.command, "Multiplier"]
				damage_stat = commands.loc[attacker.command, "Damage Stat"]

				if combatants[defender].isCursed == True:
					defense = round(combatants[defender].current_Def / 2)

				# Determine the driving stat. Need to add "Set" here eventually
				if damage_stat == "Str":
					damage = calculateDamage(attacker.current_Str, weapon_multiplier, defense)
				elif damage_stat == "Agl":
					damage = calculateDamage(attacker.current_Agl, weapon_multiplier, defense)
				elif damage_stat == "Mana":
					# Need to check resistances
					damage = calculateDamage(attacker.current_Mana, weapon_multiplier, 0)
					defense = damage * combatants[defender].current_Mana / 200

				damage = damage - defense
				print("%d damage to %s group." % (damage, attacker.targets[foe]))

				if damage < 0:
					damage = 0

				# Loop through combatants to deal damage to all members of a group. No differentiation (e.g. buffs) between them yet.
				body_count = 0
				for who in range(len(combatants)):
					if combatants[who].name == attacker.targets[foe]:
						combatants[who].current_HP -= damage
						if combatants[who].current_HP <= 0:
							combatants[who].current_HP = 0
							combatants[who].lives -= 1
							body_count += 1
				if body_count > 0:
					print("Defeated %d." % body_count)

			# Need to bring the targets list loop in here. Also, need to make combatants[defender] change for each group
			elif commands.loc[attacker.command, "Target Type"] == "All Enemies": 	
				print("%s attacks all enemies with %s." % (attacker.name, attacker.command))
				weapon_multiplier = commands.loc[attacker.command, "Multiplier"]
				damage_stat = commands.loc[attacker.command, "Damage Stat"]

				if combatants[defender].isCursed == True:
					defense = round(combatants[defender].current_Def / 2)

				# Determine the driving stat. Need to add "Set" here eventually
				if damage_stat == "Str":
					damage = calculateDamage(attacker.current_Str, weapon_multiplier, defense)
				elif damage_stat == "Agl":
					damage = calculateDamage(attacker.current_Agl, weapon_multiplier, defense)
				elif damage_stat == "Mana":
					# Need to check resistances
					damage = calculateDamage(attacker.current_Mana, weapon_multiplier, 0)
					defense = damage * combatants[defender].current_Mana / 200

				damage = damage - defense
				print("%d damage to %s group." % (damage, attacker.targets[foe]))

				if damage < 0:
					damage = 0

				# Loop through combatants to deal damage to all members of a group. No differentiation (e.g. buffs) between them yet.
				body_count = 0
				for who in range(len(combatants)):
					if combatants[who].name == attacker.targets[foe]:
						combatants[who].current_HP -= damage
						if combatants[who].current_HP <= 0:
							combatants[who].current_HP = 0
							combatants[who].lives -= 1
							body_count += 1
				if body_count > 0:
					print("Defeated %d." % body_count)

	############################
	# End indent here, presumably
	############################

		# Post-action tracking
		combatants[count] = afterTurn(attacker)
		if not battleStatus(combatants):
			break

	one_more = input("Run another round (y/n)?: ")
	if one_more == "y":
		rounds += 1
		rd += 1
	else:
		rd += 1

# Print party status line at the end of a simulation
for count in range(len(combatants)):
	if combatants[count].role == ("Player" or "NPC"):
		print("| %s: %d/%d %s" % (combatants[count].name, combatants[count].current_HP, combatants[count].HP, combatants[count].characterStatus()), end = " |")

# Need only for endline during testing phase
print("")

# Print enemy status line at the end of a simulation
enemy_list = []
for count in range(len(combatants)):
	if (combatants[count].role == "Enemy") and (combatants[count].isActive()):
		enemy_list.append(combatants[count].name)

remaining_enemies = Counter(enemy_list)
remaining_enemies.keys()
for key, number in remaining_enemies.items():
	print("{ %s - %d" % (key, number), end = " }")
print("")
	
for count in range(len(combatants)):
	print(combatants[count])
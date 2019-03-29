import pandas
import random
import operator
import openpyxl
from collections import Counter
from classes import Player, Enemy, NPC, Actor, Command
from combat import (randomTarget, battleStatus, afterTurn, frontOfGroup, rollDamage, determineDefense, affectStat, rollHeal, applyCondition,
inflictCondition, checkResistance, endOfTurn, buildResistances, checkWeakness, applyDamage, counterAttack, removeCondition, applyHeal, postBattle)

path1 = r"FFL2 Data.xlsx"
path2 = r"Battle Log.xlsx"
path3 = r"Battle Results.xlsx"

workbook = pandas.ExcelFile(path1)
log = pandas.ExcelFile(path2)
writer = pandas.ExcelWriter(path3, engine = 'openpyxl')

monsters = workbook.parse("Monster", index_col = 'Index')
commands = workbook.parse("Weapon", index_col = 'Index')
ms_prob = workbook.parse("Move Probability")
growth = workbook.parse("Growth Rates", index_col = 'RACE')
m_skills = workbook.parse("Mutant Skills")

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
commands["Hits"].fillna(1, inplace = True)
players.fillna("blank", inplace = True)
for each in range(len(battles)):
	battles[each]["COMMAND"].fillna('nan', inplace=True)
	battles[each]["CURRENT HP"].fillna(-1, inplace=True)
	battles[each]["CURRENT STR"].fillna(-1, inplace=True)
	battles[each]["CURRENT AGL"].fillna(-1, inplace=True)
	battles[each]["CURRENT MANA"].fillna(-1, inplace=True)
	battles[each]["CURRENT DEF"].fillna(-1, inplace=True)
	battles[each]["ACTIONS TAKEN"].fillna("", inplace = True)

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

	active_battle = battles[i].copy()

	# Populate the Combatants list
	# I would prefer to be doing label lookups with Pandas loc instead of iloc, but I can't get the indexing right (at load time)
	actor_count = len(active_battle.index)
	for count in range(actor_count):
		# Enemy groups require a for loop to create individual Actors for tracking initiative, deaths, etc.
		if active_battle.iloc[count,1] == "Enemy":
			if pandas.isnull(active_battle.iloc[count,3]):
				for pos in range(int(active_battle.iloc[count,2])):
					combatants.append(Enemy(active_battle.iloc[count,0]))
					combatants[place].position = pos + 1
					combatants[place].lives = 1
					combatants[place].group = count
					enemy_groups.append(tuple((combatants[place].name, 0, 0)))
					copy_row = active_battle.iloc[count]
					active_battle.loc[len(active_battle.index)] = copy_row
					place += 1
				active_battle.drop(active_battle.tail(1).index,inplace=True)
			else:
				combatants.append(Enemy(active_battle.iloc[count,0]))
				combatants[place].position = active_battle.iloc[count,3]
				combatants[place].lives = active_battle.iloc[count,2]
				combatants[place].group = count
				enemy_groups.append(tuple((combatants[count].name, 0, 0)))
				place += 1

		elif active_battle.iloc[count,1] == "Player":
			combatants.append(Player(active_battle.iloc[count,0]))
			combatants[place].lives = active_battle.iloc[count,2]
			combatants[place].position = int(active_battle.iloc[count,3])
			combatants[place].group = count
			place += 1

		else:
			combatants.append(NPC(active_battle.iloc[count,0]))
			combatants[place].lives = active_battle.iloc[count,2]
			combatants[place].position = active_battle.iloc[count,3]
			combatants[place].group = count
			place += 1

	# Create a unique list of enemy groups
	enemy_groups = set(enemy_groups)
	enemy_groups = list(enemy_groups)

	# DATA ASSIGNMENT LOOP
	# Ridiculously big loop to go through combatants list, assign static values
	for count in range(len(combatants)):
		current_com = combatants[count]

		current_com.current_HP = active_battle.iloc[current_com.group, 5]
		current_com.current_Str = active_battle.iloc[current_com.group, 6]
		current_com.current_Agl = active_battle.iloc[current_com.group, 7]
		current_com.current_Mana = active_battle.iloc[current_com.group, 8]
		current_com.current_Def = active_battle.iloc[current_com.group, 9]
		current_com.command = active_battle.iloc[current_com.group, 10]
		current_com.target_type = active_battle.iloc[current_com.group, 11]
		current_com.stoned = active_battle.iloc[current_com.group, 12]
		current_com.cursed = active_battle.iloc[current_com.group, 13]
		current_com.blinded = active_battle.iloc[current_com.group, 14]
		current_com.asleep = active_battle.iloc[current_com.group, 15]
		current_com.paralyzed = active_battle.iloc[current_com.group, 16]
		current_com.poisoned = active_battle.iloc[current_com.group, 17]
		current_com.confused = active_battle.iloc[current_com.group, 18]
		current_com.add_action(active_battle.iloc[current_com.group, 19])
	
		# Lookup the static Enemy data
		if current_com.role == "Enemy":
			current_com.DS = int(monsters.loc[current_com.name,"DS"])
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
		elif current_com.role in ("Player", "NPC"):
			current_com.Class = players.loc[current_com.name,"CLASS"]
			current_com.family = monsters.loc[current_com.Class,"Family"]
			current_com.HP = players.loc[current_com.name,"HP"]
			current_com.Str = players.loc[current_com.name,"STR"]
			current_com.Agl = players.loc[current_com.name,"AGL"]
			current_com.Mana = players.loc[current_com.name,"MANA"]
			current_com.Def = players.loc[current_com.name,"DEF"]

			# EQUIPPED MAGI
			equipped_magi = players.loc[current_com.name,"EQUIPPED MAGI"]
			if equipped_magi != "blank":
				current_com.magi = equipped_magi[:-2]
				current_com.magi_count = int(equipped_magi[-1:])
			else:
				current_com.magi = "blank"
		
			#There should be a better way to do this...but here's the lazy way
			current_com.skills.append(players.loc[current_com.name,"S0"])
			current_com.skills.append(players.loc[current_com.name,"S1"])
			current_com.skills.append(players.loc[current_com.name,"S2"])
			current_com.skills.append(players.loc[current_com.name,"S3"])
			current_com.skills.append(players.loc[current_com.name,"S4"])
			current_com.skills.append(players.loc[current_com.name,"S5"])
			current_com.skills.append(players.loc[current_com.name,"S6"])
			current_com.skills.append(players.loc[current_com.name,"S7"])
			if current_com.magi != "blank":
				current_com.skills.append(current_com.magi)

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
				# If Current HP is blank in the log, replace it with Max HP from character sheet / monster list
				combatants[count].current_HP = combatants[count].HP if combatants[count].current_HP == -1 else combatants[count].current_HP
				combatants[count].current_Str = combatants[count].Str if combatants[count].current_Str == -1 else combatants[count].current_Str
				combatants[count].current_Agl = combatants[count].Agl if combatants[count].current_Agl == -1 else combatants[count].current_Agl
				combatants[count].current_Mana = combatants[count].Mana if combatants[count].current_Mana == -1 else combatants[count].current_Mana
				combatants[count].current_Def = combatants[count].Def if combatants[count].current_Def == -1 else combatants[count].current_Def

			# SURPRISE CHECK FOR ROUND 1 ACROSS ALL COMBATANTS - One copy of Surprise or Warning is all that is needed
			# ENHANCEMENT:  More Surprise and Warning increases likelihood? Strongly favors enemy in that case
			enemy_surprise = False
			enemy_warning = False
			player_surprise = False
			player_warning = False
			for comb in range(len(combatants)):
				for skill in range(len(combatants[comb].skills)):
					if combatants[comb].role == "Enemy":
						if combatants[comb].skills[skill] == "Surprise":
							enemy_surprise = True
						elif combatants[comb].skills[skill] == "Warning":
							enemy_warning = True
					elif combatants[comb].role in ("Player", "NPC"):
						if combatants[comb].skills[skill] == "Surprise":
							player_surprise = True
						elif combatants[comb].skills[skill] == "Warning":
							player_warning = True
			
			# Warning overrides surprise
			if player_warning:
				enemy_surprise = False
			if enemy_warning:
				player_surprise = False

			p_surprise_roll = random.randint(1,100)
			e_surprise_roll = random.randint(1,100)
			# SURPRISE LOGIC - check rolls
			# If both sides have surprise, lower roll wins
			if player_surprise and enemy_surprise:
				if p_surprise_roll < e_surprise_roll and p_surprise_roll <= 50:
					enemy_surprise = False
					print("Strike First!")
				elif p_surprise_roll > e_surprise_roll and e_surprise_roll <= 25:
					player_surprise = False
					print("Unexpected Attack!")
				# If the rolls are the same, neither side wins a surprise round
				else:
					player_surprise = False
					enemy_surprise = False
			elif player_surprise:
				if p_surprise_roll > 50:
					player_surprise = False
				else:
					print("Strike First!")
			elif enemy_surprise:
				if e_surprise_roll > 25:
					enemy_surprise = False
				else:
					print("Unexpected Attack!")

		# RUN CHECK - Currently lacks a random component for players. Might want to add one
		run_attempt = False
		run_success = False
		party_AGL = 0
		enemies_AGL = 0
		# Check commands to see if players are running (all players run together)
		for runner in range(len(combatants)):
			if combatants[runner].command == "Run":
				run_attempt = True
				break
		if run_attempt:
			if player_surprise:
				run_success = True
			else:
				for runner in range(len(combatants)):
					if combatants[runner].role == "Enemy":
						enemies_AGL += combatants[runner].current_Agl
					else:
						if combatants[runner].isDead():
							party_AGL += 100
						else:
							party_AGL += combatants[runner].current_Agl		
				#enemies_AGL += random.randint(1,50)
				if party_AGL > enemies_AGL:
					run_success = True
			if run_success:
				print("Run!!")
				break
			else:
				print("Failed to run!")
				enemy_surprise = True

		# INITIATIVE
		for count in range(len(combatants)):
			if combatants[count].current_Str >= combatants[count].current_Def:
				base_initiative = combatants[count].current_Agl
			else:
				base_initiative = combatants[count].current_Agl + combatants[count].current_Str - combatants[count].current_Def
			variable = (1+(random.randint(1,25)/100))
			combatants[count].initiative = base_initiative * variable

		# Sort actors based on initiative score
		combatants = sorted(combatants, key = operator.attrgetter("initiative"), reverse=True)

		# Create party formation
		party_order = []
		for count in range(len(combatants)):
			if combatants[count].role in ("Player", "NPC"):
				party_order.append(tuple((combatants[count].name, combatants[count].position, count)))
		party_order = sorted(party_order, key = operator.itemgetter(1), reverse=True)

		# Create barrier lists anew each round
		enemy_barriers = []
		player_barriers = []

		# COMMAND SELECTION
		for count in range(len(combatants)):
			attacker = combatants[count]

			# STATUS CHECK
			if not attacker.isActive():
				continue

			# SURPRISE CHECK
			if enemy_surprise and attacker.role in ("Player", "NPC"):
				attacker.command = "None"
				print("%s did nothing." % attacker.name)
				continue
			elif player_surprise and attacker.role == "Enemy":
				attacker.command = "None"
				print("%s did nothing." % attacker.name)
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
			if attacker.command == 'nan' and attacker.role in ("Enemy","NPC"):
				row = attacker.MS
				roll = random.randint(0,255)
				for choice in range(7):
					if roll <= ms_prob.iloc[int(row), choice+1]:
						attacker.command = attacker.skills[choice]
						break
					else:
						continue

			# Start of round triggers (shield barriers)
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

			# SURPRISE CHECK
			if enemy_surprise and attacker.role in ("Player", "NPC"):
				continue
			elif player_surprise and attacker.role == "Enemy":
				continue

			sel_target = ""

			# CONFUSED TARGETING
			# Should confused targets flip a coin as to which side they attack as opposed to picking from the total pool?
			if attacker.isConfused():
				confuse_roll = random.randint(1,100)
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
							print("A barrier covered...someone?")
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
			elif attacker.role not in ("Player", "NPC"):

				# Whip winding
				if attacker.command == "None":
					continue

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
				defender = frontOfGroup(combatants, count, foe, command)

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
				else:
					def_target_type = "None"
					def_command_effect = "None"
				blocked = False
				blockable = False
				dmg_reduction = False
				critical_hit = False
				damage = 0

				if command.targeting == "Single":
					print("%s attacks %s with %s." % (attacker.name, target.name, attacker.command), end = " ")

					# SETTING HIT CHANCE
					# Ranged attacks are based on Percent chance unless using a Gun
					if command.att_type == "Ranged":
						# All guns and cannons have Robot Race Bonus and use STR as a calculation
						if command.race_bonus == "Robot":
							# Robots gain double their STR to hit with guns and cannons
							if attacker.family == "Robot":
								attacker_hit = attacker.getStrength() * 2 + command.percent
							else:
								attacker_hit = attacker.getStrength() + command.percent
						# Bows use 2x AGL and the item's hit chance
						else:
							attacker_hit = attacker.getAgility() * 2 + command.percent
					# Melee attacks just use AGL
					else:
						attacker_hit = attacker.getAgility() * 2

					defender_score = target.getAgility()

					# Blockable logic
					if command.att_type in ("Melee", "Ranged"):
						blockable = True
					if (def_target_type == "Block" or "Block" in def_command_effect) and blockable:
						block_roll = random.randint(1,100)
						if block_roll <= (commands.loc[target.command, "Percent"] + defender_score):
							blocked = True

					difference = defender_score - attacker_hit
					if command.att_type in ("Melee", "Ranged") and "Never miss" not in command.effect:
						hit_chance = 97 - difference
					# Magic attacks always hit
					else:
						hit_chance = 100
					# DETERMINE HIT
					hit_count = 0
					# For Multi-hit attacks, this will loop more than once
					for hit in range(int(command.hits)):
						hit_roll = random.randint(1,100)
						if hit_roll <= hit_chance:
							hit_count += 1
					if hit_count == 0:
						print("Missed!")
					# Melee attacks get blocked fully (even status-based ones)
					elif (blocked == True and command.att_type == "Melee"):
						print("%s defended against %s with %s." % (target.name, attacker.command, target.command))
					# Should ALL Stone effects be blocked by a shield? Doesn't make sense with things like StoneGas...

					# DAMAGE ASSIGNMENT
					else:
						if hit_count > 1:
							print("%d hits." % hit_count, end = " ")
						if "Cut" in command.effect:
							# Replace the normal attack roll, or just have both?
							cut_roll = random.randint(1,100)
							if cut_roll <= (50 + attacker.current_Str):
								print("Failed to cut.")
								continue
							else:
								cut_check = attacker.getStrength() + command.percent
								# Check for weapon resistance and whether the attack was blocked (then again, a blocked attack wouldn't get here...)
								if checkResistance(target.resists, "Weapon", command.status, barriers):
									cut_check = int(cut_check/2)
								if blocked:
									cut_check = int(cut_check/2)
								if cut_check > target.getDefense() and target.family != "God":
									applyCondition("Stun", target)
									print("%s was cut." % target.name)
									continue
								else:
									print("Too hard to cut.")

						# Reflect - change target into the attacker
						if ("Reflect" in def_command_effect or def_target_type == "Reflect") and command.att_type == "Magic":
							print("%s reflected the attack." % target.command)
							# Makes the attacker into the target of its own spell
							target = attacker

						# Nullify - end the attack since it was nullified on target
						if ("Nullify" in def_command_effect or def_target_type == "Nullify") and command.att_type == "Magic":
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

						if command.status != "None":
							inflictCondition(command, attacker, target)
						# One pass for most attacks, but accumulates damage for multi-hit attacks
						for hit in range(hit_count):
							offense = rollDamage(command, attacker)
							defense = determineDefense(target, command, offense)
							damage += offense - defense
						# Ranged attacks get blocked for 50% damage
						if blocked == True:
							damage = int(damage/2)
						# If weapon resistance is found against a non-magical attack, damage is halved
						if command.att_type in ("Melee", "Ranged") and checkResistance(target.resists, "Weapon", command.status, barriers):
							damage = int(damage/2)
						if critical_hit == True:
							damage = int(damage*1.5)

						# DAMAGE OUTPUT
						# No damage on pure Status attacks
						if command.stat == "Status":
							print("")
						elif damage <= 0:
							damage = 0
							print("No damage.")
						else:
							if any(x in command.effect for x in ["Absorb", "Drain", "Dissolve"]):
								absorb_type = command.effect
								absorb = int(damage * (command.percent / 100))
								reversed = False
								if absorb_type == "Absorb":
									if target.family in ("Golem"):
										print("Cannot absorb from %s." % target.name)
										absorb = 0
									elif target.family in ("God", "Plant"):
										reversed = True
								elif absorb_type == "Drain":
									if target.family == "Undead":
										reversed = True
									elif target.family in ("God", "Golem"):
										print("Cannot drain from %s." % target.name)
										absorb = 0
								elif absorb_type == "Dissolve":
									pass
								if reversed:
									print("Reversed the absorption. %d HP stolen from %s." % (damage, attacker.name), end = " ")
									applyHeal(damage, target)
									if applyDamage(damage, attacker) == 1:
										print("%s fell." % attacker.name)
									else:
										print("")
									continue
								else:
									absorb = applyHeal(absorb, attacker)
									print("Absorbed %d HP." % absorb, end = " ")
							print("%d damage to %s." % (damage, attacker.targets[foe]), end = " ")
							if applyDamage(damage, target) == 1:
								print("%s fell." % target.name)
							elif "WindUp" in command.effect:
								wind_roll = random.randint(1, 100)
								if wind_roll <= command.percent:
									print("Winded the whip.")
									target.command = "None"
								else:
									print("")
							else:
								print("")

						# Counter-attacks if any exist and the target survived
						if target.isActive() and (def_target_type == "Counter" or "Counter" in def_command_effect):
							counter_command = Command(target.command, commands)
							if target.role == "Enemy":
								buildResistances(player_barriers, barriers, commands)
							else:
								buildResistances(enemy_barriers, barriers, commands)
							counterAttack(target, attacker, counter_command, damage, barriers)

				elif command.targeting in ("Group", "All Enemies"):
					if command.targeting == "Group" and target.role == "Enemy":
						print("%s attacks %s group with %s." % (attacker.name, attacker.targets[foe], attacker.command), end = " ")
					elif command.targeting == "Group" and target.role in ("Player", "NPC"):
						print("%s attacks %s with %s." % (attacker.name, attacker.targets[foe], attacker.command), end = " ")
					else:
						# Only print the command text the first time through
						if foe == 0:
							print("%s attacks all enemies with %s." % (attacker.name, attacker.command))

					# Reflect - change target into the attacker
					if ("Reflect" in def_command_effect or def_target_type == "Reflect") and command.att_type == "Magic":
						print("%s reflected the attack." % target.command)
						target = attacker

					# Nullify - end the attack since it was nullified on target
					elif ("Nullify" in def_command_effect or def_target_type == "Nullify") and command.att_type == "Magic":
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
						# Currently, no damage component with Debuff abilities
						if "Debuff" in command.effect:
							target = affectStat(target, command)
							continue
						if command.status != "None":
							for who in range(len(combatants)):
								if combatants[who].name == target.name and combatants[who].isTargetable():
									inflictCondition(command, attacker, combatants[who])
						offense = rollDamage(command, attacker)
						defense = determineDefense(target, command, offense)

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
							damage = int(damage/2)
						if critical_hit:
							damage = damage * 1.5

					# No damage on pure Status attacks
					if command.stat == "Status":
						print("")
					elif damage <= 0:
						damage = 0
						print("No damage.")
					else:
						# Loop through combatants to deal damage to all members of a group
						body_count = 0
						for who in range(len(combatants)):
							# Only damage those matching the target name and that are not already dead or stoned
							if combatants[who].name == target.name and combatants[who].isTargetable():
								body_count += applyDamage(damage, combatants[who])
						# REVISIT TO MAKE PRINTING MORE FLEXIBLE BASED ON RESULTS (deaths, no deaths, single character group, etc)
						print("%d damage to %s group." % (damage, target.name), end = " ")
						if body_count > 0:
							print("Defeated %d." % body_count)
						else:
							print("")

				elif command.targeting == "Ally":
					print("%s uses %s for %s." % (attacker.name, attacker.command, attacker.targets[foe]), end = " ")
					# Reflect - change target into the caster
					if ("Reflect" in def_command_effect or def_target_type == "Reflect") and command.att_type == "Magic":
						print("%s reflected the attack." % target.command, end = " ")
						target = attacker
					# Nullify - end the effect since it was nullified on target
					elif ("Nullify" in def_command_effect or def_target_type == "Nullify") and command.att_type == "Magic":
						print("%s repulsed the attack." % target.command)
						continue
					if command.status != "None":
						removeCondition(command.status, target)
					if "Heal" in command.effect:
						rollHeal(command, attacker, target)
					if "Buff" in command.effect:
						target = affectStat(target, command)
					print("")
			
				elif command.targeting == "Self":
					print("%s uses %s." % (attacker.name, attacker.command), end = " ")
					if "Buff" in command.effect:
						attacker = affectStat(attacker, command)

				elif command.targeting == "Allies":
					if foe == 0:
						print("%s uses %s." % (attacker.name, attacker.command))
					for who in range(len(combatants)):
						if combatants[who].name == attacker.targets[foe]:
							# Reflect - change target into the caster
							if ("Reflect" in def_command_effect or def_target_type == "Reflect") and command.att_type == "Magic":
								print("%s reflected the attack." % target.command, end = " ")
								target = attacker
							# Nullify - end the effect since it was nullified on target
							elif ("Nullify" in def_command_effect or def_target_type == "Nullify") and command.att_type == "Magic":
								print("%s repulsed the attack." % target.command)
								continue
							if command.status != "None":
								removeCondition(command.status, combatants[who])
							if "Heal" in command.effect:
								rollHeal(command, attacker, combatants[who])
							if "Buff" in command.effect:
								print("%s's" % combatants[who], end = " ")
								combatants[who] == affectStat(combatants[who], command)
							print("")

			# Post-action tracking
			if "Sacrifice" in command.effect:
				applyDamage(attacker.HP, attacker)
				print("%s sacrificed their life." % attacker.name)
			combatants[count] = afterTurn(attacker)
			
			# Check survivors
			party_members = 0
			enemies = 0

			for count in range(len(combatants)):
				if combatants[count].role == "Enemy" and combatants[count].isTargetable():
					enemies += 1
				elif combatants[count].role in ("Player", "NPC") and combatants[count].isTargetable():
					party_members += 1
			# Print if one side has no survivors, otherwise continue on
			if party_members == 0:
				print("Odin beckons...")
				another_round = "n"
				break
			elif enemies == 0:
				print("Right on!")
				postBattle(combatants, m_skills, growth)
				another_round = "n"
				break

		# If the battle didn't end, perform end of round operations
		if another_round != "n":
			for each in range(len(combatants)):
				combatants[each] = endOfTurn(combatants[each], commands)
				# Should only be needed for "Regained sanity" purposes...and should go away in Alpha
				# Being used for Surprise rounds...which means the input approach is not a good solution
				if combatants[each].role == "Player" and combatants[each].command == "None":
					combatants[each].command = input("New command for %s: " % combatants[each].name)
					combatants[each].target_type = input("New target for %s: " % combatants[each].name)
	#				pc_row = 0
	#				for pc in range(len(party_order)):
	#					if combatants[each].name == party_order[pc][0]:
	#						pc_row = party_order[pc][2]
	#						break
	#				combatants[each].command = active_battle.iloc[pc_row, 10]
	#				combatants[each].target_type = active_battle.iloc[pc_row, 11]
			# Reset surprise flags
			enemy_surprise = False
			enemy_warning = False
			player_surprise = False
			player_warning = False
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

	write_to_excel = input("Save battle? (y/n): ")
	if write_to_excel == "y":
		for count in range(len(combatants)):
			active_battle.iloc[count,0] = combatants[count].name
			active_battle.iloc[count,1] = combatants[count].role
			active_battle.iloc[count,2] = combatants[count].lives
			active_battle.iloc[count,3] = combatants[count].position
			active_battle.iloc[count,4] = combatants[count].initiative
			active_battle.iloc[count,5] = combatants[count].current_HP
			active_battle.iloc[count,6] = combatants[count].current_Str
			active_battle.iloc[count,7] = combatants[count].current_Agl
			active_battle.iloc[count,8] = combatants[count].current_Mana
			active_battle.iloc[count,9] = combatants[count].current_Def
			active_battle.iloc[count,10] = combatants[count].command
			active_battle.iloc[count,11] = combatants[count].target_type
			active_battle.iloc[count,12] = combatants[count].stoned
			active_battle.iloc[count,13] = combatants[count].cursed
			active_battle.iloc[count,14] = combatants[count].blinded
			active_battle.iloc[count,15] = combatants[count].asleep
			active_battle.iloc[count,16] = combatants[count].paralyzed
			active_battle.iloc[count,17] = combatants[count].poisoned
			active_battle.iloc[count,18] = combatants[count].confused
			active_battle.iloc[count,19] = combatants[count].actions_taken
#			active_battle.at[count,"ACTIONS TAKEN"] = combatants[count].actions_taken
		battles[i] = active_battle.copy()
		save_list.append(tuple((i, log.sheet_names[i+1])))

	run_sim = input("Run another battle (y/n)?: ")

for bat in range(len(save_list)):
 	battles[save_list[bat][0]].to_excel(writer, sheet_name = save_list[bat][1])

if len(save_list) > 0:
	writer.save()

# Print Character Snapshots
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
		print("MAGI: %s" % players.iloc[count, 20])
		print("OTHER MAGI: %s" % players.iloc[count, 21])
		print("INVENTORY: %s" % players.iloc[count,22])
		print("")
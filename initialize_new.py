import pandas
import random
import operator
import openpyxl
import sys
from collections import Counter
from classes import Player, Enemy, NPC, Actor, Command
from combat import (randomTarget, afterTurn, frontOfGroup, rollDamage, determineDefense, affectStat, rollHeal, applyCondition, hitScore, actConfused,
inflictCondition, checkResistance, endOfTurn, buildResistances, checkWeakness, applyDamage, counterAttack, removeCondition, applyHeal, postBattle,
equivalentLevel, mightyBlow)

stdout = sys.stdout

path1 = r"FFL2 Data.xlsx"
path2 = r"Battle Log.xlsm"
path3 = r"Battle Results.xlsx"
text_path = "battles.log"

workbook = pandas.ExcelFile(path1)
log = pandas.ExcelFile(path2)
writer = pandas.ExcelWriter(path3, engine = 'openpyxl')

monsters = workbook.parse("Monster", index_col = 'Index')
commands = workbook.parse("Weapon", index_col = 'Index')
ms_prob = workbook.parse("Move Probability")
growth = workbook.parse("Growth Rates", index_col = 'RACE')
m_skills = workbook.parse("Mutant Skills", index_col = 'DS')
transformations = workbook.parse("Evolve")

# GLOBAL CONSTANTS
player_surprise_chance = 50
enemy_surprise_chance = 25
initiative_var = 25
break_confuse = 10
single_target_odds = 50
remaining_uses_for_enemies_mult = 1.0
blocked_ranged_mult = 0.5
critical_mult = 1.5
counter_protection_mult = 0.75
cut_base = 50
cut_chance = 0.5
crit_chance = 30
weapon_res_mult = 0.5
monster_race_cap = 35

# Loop through each sheet of the battle log, appending each to the battles list
battles = []
save_list = []
save_players = []
player_actions = []

for count in range(len(log.sheet_names)):
	if count == 0:
		players = log.parse("Players", index_col = 'Index')
	elif count == 1:
		pass
	else:
		battles.append(log.parse(count))

# Remove NaN entries from certain sheets and columns
monsters.fillna("blank", inplace = True)
commands["Element"].fillna("None", inplace = True)
commands["Status"].fillna("None", inplace = True)
commands["Effect"].fillna("None", inplace = True)
commands["Target Type"].fillna("None", inplace = True)
commands["Hits"].fillna(1, inplace = True)
commands["Price"].fillna(-1, inplace = True)
players["Current HP"].fillna(-1, inplace = True, downcast = 'infer')
players["S0 Uses Left"].fillna(-1, inplace = True, downcast = 'infer')
players["S1 Uses Left"].fillna(-1, inplace = True, downcast = 'infer')
players["S2 Uses Left"].fillna(-1, inplace = True, downcast = 'infer')
players["S3 Uses Left"].fillna(-1, inplace = True, downcast = 'infer')
players["S4 Uses Left"].fillna(-1, inplace = True, downcast = 'infer')
players["S5 Uses Left"].fillna(-1, inplace = True, downcast = 'infer')
players["S6 Uses Left"].fillna(-1, inplace = True, downcast = 'infer')
players["S7 Uses Left"].fillna(-1, inplace = True, downcast = 'infer')
players["MAGI Uses Left"].fillna(-1, inplace = True, downcast = 'infer')
players.fillna("blank", inplace = True)
for each in range(len(battles)):
	battles[each]["COMMAND"].fillna("None", inplace=True)
	battles[each]["CURRENT HP"].fillna(-1, inplace=True, downcast = 'infer')
	battles[each]["CURRENT STR"].fillna(-1, inplace=True, downcast = 'infer')
	battles[each]["CURRENT AGL"].fillna(-1, inplace=True, downcast = 'infer')
	battles[each]["CURRENT MANA"].fillna(-1, inplace=True, downcast = 'infer')
	battles[each]["CURRENT DEF"].fillna(-1, inplace=True, downcast = 'infer')
	battles[each]["ACTIONS TAKEN"].fillna("", inplace = True)
	battles[each]["STATS USED"].fillna("", inplace = True)

print("1. Run simulator")
print("2. Print character sheets")
print("3. Monster transformation")
operation = int(input("Enter a number: "))

if operation == 1:
	sys.stdout = open(text_path, 'w')
	sys.stdout = stdout
	run_sim = "y"
	while run_sim != "n":

		# This is where a function for creating the combatants list from a battle should be. Call would pass an int to say from which Log sheet to pull
		# Might even pass the sheet itself from battles[]. Would return combatants list
		combatants = []
		enemy_groups = []

		for bat in range(len(battles)):
			print("%d. %s" % (bat+1, log.sheet_names[bat+2]))
		i = int(input("Which battle do you want to run? Enter a number: "))

		# Setting to the list index of the number chosen
		print("Executing Battle: %s" % log.sheet_names[i+1])
		i=i-1

		# Need to track the right spot in combatants, which conflicts with 'count' due to enemy "lives" inflating the list vs the Log
		place = 0

		active_battle = battles[i].copy()

		# Populate the Combatants list
		# I would prefer to be doing label lookups with Pandas loc instead of iloc, but I can't get the indexing right (at load time)
		actor_count = len(active_battle.index)
		seen = set()
		# Seen watches for unique enemy group names to build a unique list in enemy_groups
		for count in range(actor_count):
			# Enemy groups require a for loop to create individual Actors for tracking initiative, deaths, etc.
			if active_battle.iloc[count,1] == "Enemy":
				if pandas.isnull(active_battle.iloc[count,3]):
					for pos in range(int(active_battle.iloc[count,2])):
						combatants.append(Enemy(active_battle.iloc[count,0]))
						combatants[place].position = pos + 1
						combatants[place].lives = 1
						combatants[place].group = count
						#enemy_groups.append(tuple((combatants[place].name, 0, 0)))
						copy_row = active_battle.iloc[count]
						active_battle.loc[len(active_battle.index)] = copy_row
						place += 1
					seen.add(combatants[place-1].name) # -1 because place was incremented at the end of the above for loop, which would exceed range
					enemy_groups.append(tuple((combatants[place-1].name, 0, 0)))
					active_battle.drop(active_battle.tail(1).index,inplace=True)
				else:
					combatants.append(Enemy(active_battle.iloc[count,0]))
					combatants[place].position = active_battle.iloc[count,3]
					combatants[place].lives = active_battle.iloc[count,2]
					combatants[place].group = count
					if combatants[place].name not in seen:
						enemy_groups.append(tuple((combatants[count].name, 0, 0)))
					seen.add(combatants[place].name)
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

		# Create a unique list of enemy groups in order of entry
#		enemy_groups = set(enemy_groups)
#		enemy_groups = list(enemy_groups)
		#seen = set()
		#seen_add = seen.add
		#enemy_groups = [x for x in enemy_groups if not (x in seen or seen_add(x))]

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
			current_com.environment = active_battle.iloc[current_com.group, 19]
			current_com.addAction(active_battle.iloc[current_com.group, 20], active_battle.iloc[current_com.group, 21])
		
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
		
				# SEE AfterTurn LOGIC TO REWRITE TO A LOOP
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
				condition = players.loc[current_com.name, "CONDITION"]
				if "BLND" in condition:
					current_com.blinded = "y"
				if "CURS" in condition:
					current_com.cursed = "y"
				if "STON" in condition:
					current_com.stoned = "y"

				# EQUIPPED MAGI
				equipped_magi = players.loc[current_com.name,"EQUIPPED MAGI"]
				if equipped_magi != "blank":
					current_com.magi = equipped_magi[:-2]
					current_com.magi_count = int(equipped_magi[-1:])
				else:
					current_com.magi = "blank"

				# Grab natural stats for purposes of stat gain in humans and mutants. Do it for all just in case
				current_com.natural_str = players.loc[current_com.name,"Natural STR"]
				current_com.natural_agl = players.loc[current_com.name,"Natural AGL"]
				current_com.natural_mana = players.loc[current_com.name,"Natural MANA"]
				current_com.natural_def = players.loc[current_com.name,"Natural DEF"]
			
				# SEE AfterTurn LOGIC TO REWRITE TO A LOOP
				current_com.skills.append(players.loc[current_com.name,"S0"])
				current_com.skills.append(players.loc[current_com.name,"S1"])
				current_com.skills.append(players.loc[current_com.name,"S2"])
				current_com.skills.append(players.loc[current_com.name,"S3"])
				current_com.skills.append(players.loc[current_com.name,"S4"])
				current_com.skills.append(players.loc[current_com.name,"S5"])
				current_com.skills.append(players.loc[current_com.name,"S6"])
				current_com.skills.append(players.loc[current_com.name,"S7"])
				current_com.uses.append(players.loc[current_com.name,"S0 Uses Left"])
				current_com.uses.append(players.loc[current_com.name,"S1 Uses Left"])
				current_com.uses.append(players.loc[current_com.name,"S2 Uses Left"])
				current_com.uses.append(players.loc[current_com.name,"S3 Uses Left"])
				current_com.uses.append(players.loc[current_com.name,"S4 Uses Left"])
				current_com.uses.append(players.loc[current_com.name,"S5 Uses Left"])
				current_com.uses.append(players.loc[current_com.name,"S6 Uses Left"])
				current_com.uses.append(players.loc[current_com.name,"S7 Uses Left"])
				if current_com.magi != "blank":
					current_com.skills.append(current_com.magi)
					current_com.uses.append(players.loc[current_com.name,"MAGI Uses Left"])

				current_com.gold = players.loc[current_com.name,"GOLD"]
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
			sys.stdout = open(text_path, 'a')
			print("~~~ %s: Round %d ~~~" % (log.sheet_names[i+2], rd))
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
				its_round_one = False

				for actions in range(len(combatants)):
					if combatants[actions].actions_taken == "":
						its_round_one = True
					else:
						its_round_one = False
				if its_round_one:
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
						if p_surprise_roll < e_surprise_roll and p_surprise_roll <= player_surprise_chance:
							enemy_surprise = False
							print("Strike First!")
						elif p_surprise_roll > e_surprise_roll and e_surprise_roll <= enemy_surprise_chance:
							player_surprise = False
							print("Unexpected Attack!")
						# If the rolls are the same, neither side wins a surprise round
						else:
							player_surprise = False
							enemy_surprise = False
					elif player_surprise:
						if p_surprise_roll > player_surprise_chance:
							player_surprise = False
						else:
							print("Strike First!")
					elif enemy_surprise:
						if e_surprise_roll > enemy_surprise_chance:
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

			# INITIATIVE AND EVASION
			for count in range(len(combatants)):
				# Evasion sets the base for initiative
				# If STR >= DEF, then apply no penalty. Monsters use this since they're naturally balanced
				if combatants[count].current_Str >= combatants[count].current_Def or combatants[count].getRace() == "Monster":
					combatants[count].evasion = combatants[count].current_Agl
				# If DEF > STR, apply a penalty equal to the difference
				else:
					combatants[count].evasion = combatants[count].current_Agl + combatants[count].current_Str - combatants[count].current_Def

				# Initiative
				init_boost = 0
				if "Warning" in combatants[count].skills:
					init_boost += 3
				if "Surprise" in combatants[count].skills:
					init_boost += 5
				if "Boots" in combatants[count].skills:
					init_boost += 5
				#if "Quick" in commands.loc[combatants[count].command, "Effect"]:
				#	init_boost += 20
				variable = 1+(random.randint(1, initiative_var)/100)
				combatants[count].initiative = combatants[count].evasion * variable + init_boost

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

				# SURPRISE CHECK
				if enemy_surprise and attacker.role in ("Player", "NPC"):
					attacker.stopped = "y"
					#attacker.command = "None"
					print("%s did nothing." % attacker.name)
					continue
				elif player_surprise and attacker.role == "Enemy":
					attacker.stopped = "y"
					#attacker.command = "None"
					print("%s did nothing." % attacker.name)
					continue

				# CONFUSION CHECK - for those confused at the start of a round
				if attacker.isConfused():
					attacker.command = actConfused(attacker, commands, players)
					# options = []
					# conf_command = 0
					# remaining_uses = 100
					# while conf_command == 0:
					# 	conf_command = 1
					# 	for skill in range(len(attacker.skills)):
					# 		if attacker.skills[skill] != "blank" and commands.loc[attacker.skills[skill],"Target Type"] != "None":
					# 			options.append(attacker.skills[skill])
					# 	confuse_command_roll = random.randint(0, len(options)-1)
					# 	attacker.command = options[confuse_command_roll]

					# 	# Check PC in case ability was expired during combat
					# 	if attacker.role in ("Player", "NPC"):
					# 		remaining_uses = players.loc[attacker.name, "S%d Uses Left" % confuse_command_roll]
					# 		if remaining_uses <= 0:
					# 			conf_command = 0

				# ENEMY COMMAND SELECTION - uses Move Probability table based on MS
				# Could also be used for random ability selection for players if an appropriate MS were assigned
				# May want to add one for when MS exists, another for completely random if it doesn't (or always pick top command)
				if attacker.command == "None" and attacker.role in ("Enemy","NPC"):
					row = attacker.MS
					roll = random.randint(0,255)
					for choice in range(7):
						if roll <= ms_prob.iloc[int(row), choice+1]:
							attacker.command = attacker.skills[choice]
							break
						else:
							continue

				# COMMAND CHECK - does the command exist?
				try:
					commands.loc[attacker.command]
				except KeyError:
					sys.stdout = stdout
					attacker.command = input("Invalid command. Enter a new one: ")
					sys.stdout = open(text_path, 'a')

				# Start of round triggers (shield barriers)
				if (commands.loc[attacker.command, "Target Type"] == "Block" and commands.loc[attacker.command, "Effect"] != "None"):
					if commands.loc[attacker.command, "Effect"] in ("Nullify", "Reflect"):
						pass
					elif attacker.role == "Enemy":
						enemy_barriers.append(commands.loc[attacker.command, "Effect"])
					else:
						player_barriers.append(commands.loc[attacker.command, "Effect"])

			# TARGETING AND COMMAND EXECUTION
			for count in range(len(combatants)):
				attacker = combatants[count]

				# STATUS CHECK
				if not attacker.isActive():
					if attacker.isStopped():
						print("%s is stopped." % attacker.name)
					continue

				# SURPRISE CHECK
				if enemy_surprise and attacker.role in ("Player", "NPC"):
					continue
				elif player_surprise and attacker.role == "Enemy":
					continue

				sel_target = ""

				# CONFUSION CHECK - for those that became confused during a round
				if attacker.isConfused():
					attacker.command = actConfused(attacker, commands, players)

				# CONFUSED TARGETING
				# Should confused targets flip a coin as to which side they attack as opposed to picking from the total pool?
				if attacker.isConfused():
					confuse_roll = random.randint(1,100)
					if confuse_roll > break_confuse:
						print("%s is confused." % attacker.name, end = " ")
						attacker.target_type = commands.loc[attacker.command, "Target Type"]
						confuse_targets = []
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
							combatants[count] = afterTurn(attacker, commands.loc[attacker.command, "Growth Stat"], players)
							continue
						elif attacker.target_type in ("Counter", "Reflect"):
							print("%s is waiting for the attack." % attacker.name)
							combatants[count] = afterTurn(attacker, commands.loc[attacker.command, "Growth Stat"], players)
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
						attacker.stopped = "y"
						#attacker.command = "None"
						attacker.confused = "n"
						continue
					
				# Find an actual target based on Target Type, where applicable (i.e. not the "All" abilities)
				elif attacker.role not in ("Player", "NPC"):

					# Whip winding
					if attacker.command == "None":
						continue

					if attacker.command == "Wait":
						print("%s waits." % attacker.name)
						continue

					# Based on the Command, assign the Target Type to the Target line
					attacker.target_type = commands.loc[attacker.command, "Target Type"]

					if attacker.target_type == "Single":
						for choice in range(len(party_order)):
							roll = random.randint(1,100)
							# Increase a player's chance to be targeted if using a shield
							if commands.loc[combatants[party_order[choice][2]].command, "Type"] == "Shield":
								target_odds = single_target_odds + commands.loc[combatants[party_order[choice][2]].command, "Percent"] / 5
							else:
								target_odds = single_target_odds
							# If the PC party is larger than 5, reduce the target chances by 5% for each one over 5
							if len(party_order) > 5:
								target_odds -= (len(party_order)-5)*5
							if roll <= target_odds and combatants[party_order[choice][2]].isTargetable():
								sel_target = party_order[choice][0]
								break
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
						if commands.loc[attacker.command, "Effect"] != "None" and commands.loc[attacker.command, "Effect"] not in ("Nullify", "Reflect"):
							print("A barrier covered the enemies.")
						else:
							print("")
						combatants[count] = afterTurn(attacker, commands.loc[attacker.command, "Growth Stat"], players)
						continue
					# Counter and reflect effects happen at start of turn. This is an announcement of the ability's usage on the character's turn
					elif attacker.target_type in ("Counter", "Reflect"):
						print("%s is waiting for the attack." % attacker.name)
						combatants[count] = afterTurn(attacker, commands.loc[attacker.command, "Growth Stat"], players)
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
					# ################## REMOVE IF HAVING ISSUES #####################
					# # If the target doesn't exist
					# if attacker.target_type != "":
					# 	try:
					# 		monsters.loc[attacker.target_type]
					# 	except KeyError:
					# 		sys.stdout = stdout
					# 		attacker.target_type = input("Invalid target. Enter a new one: ")
					# 		sys.stdout = open("battles.log", 'a')
					# ################## REMOVE IF HAVING ISSUES #####################

					temp_target = commands.loc[attacker.command, "Target Type"]
					if temp_target in ("Single", "Group", "Ally"):
						attacker.add_target(attacker.target_type)
					elif temp_target == "Self":
						attacker.add_target(attacker.name)
					elif temp_target == "Block":
						print("%s is defending with %s." % (attacker.name, attacker.command), end = " ")
						if commands.loc[attacker.command, "Effect"] != "None" and commands.loc[attacker.command, "Effect"] not in ("Nullify", "Reflect"):
							print("A barrier covered the party.")
						else:
							print("")
						combatants[count] = afterTurn(attacker, commands.loc[attacker.command, "Growth Stat"], players)
						continue
					# May need logic to set a counter/reflect flag at beginning of a round so not every attack or spell is countered
					elif temp_target in ("Counter", "Reflect"):
						print("%s is waiting for the attack." % attacker.name)
						combatants[count] = afterTurn(attacker, commands.loc[attacker.command, "Growth Stat"], players)
						continue
					elif temp_target in ("All Enemies", "Sweep"):
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
						continue

				# Logic for finding remaining uses on a command for Players and NPCs
				skill_slot = 0
				remaining_uses = 100
				if attacker.role in ("Player", "NPC"):
					skill_slot = attacker.skillSlot()
					if skill_slot < 8:
						remaining_uses = players.loc[attacker.name, "S%d Uses Left" % skill_slot]
					else:
						remaining_uses = players.loc[attacker.name, "MAGI Uses Left"]
				else:
					remaining_uses = int(commands.loc[attacker.command, "#Uses"] * (remaining_uses_for_enemies_mult + random.uniform(-.05,.05)))

				# Construct the command class for this instance
				command = Command(attacker.command, commands, remaining_uses)

				# Human Spirit Chance - Low chance, but unlocks new ability
				if attacker.role == "Player" and attacker.Class == "Human" and not attacker.isConfused():
					biggest_foe = 1
					human_spirit = equivalentLevel(attacker.HP, 26, 50)  # Get DS equivalent for human PC
					for tar in range(len(attacker.targets)):
						biggest_foe = int(monsters.loc[attacker.targets[tar], "DS"])
					spirit_diff = biggest_foe - human_spirit
					# Reward melee attacks against greater opponents with 5 bonus points
					if command.att_type == "Melee" and spirit_diff > 1:
						spirit_diff += 5
					spirit_chance = random.randint(1,200)
					# If command has a spirit flare ability, use it
					# NEED TO REMAP IF RACE_BONUS == "ROBOT"
					# attacker.command STILL HAS OLD NAME IN IT. CHANGE OR LEAVE IT?
					if spirit_chance < spirit_diff and command.human_spirit != "":
						print("The human spirit shines bright!", end = " ")
						command = Command(command.human_spirit, commands, remaining_uses)

				# Cycle through targets for attacks
				for foe in range(len(attacker.targets)):
					# Select the front-most member of a group with the same name (i.e. attack the front-most enemy of a group)
					# FUNCTION ONLY CALLED ONCE. MOVE IT BACK?
					defender = frontOfGroup(combatants, attacker, foe, command)

					# Defender == 100 means that group is gone. Go to the next foe
					if defender == 100:
						if foe == 0 and command.targeting == "All Enemies":
							print("%s attacks all enemies with %s." % (attacker.name, attacker.command), end = " ")
							if command.remaining <= 3:
								print("**%d uses left!**", command.remaining)
							else:
								print("")
						elif foe == 0 and command.targeting == "Allies":
							print("%s uses %s." % (attacker.name, attacker.command), end = " ")
							if command.remaining <= 3:
								print("**%d uses left!**" % command.remaining)
							else:
								print("")
						elif foe == 0 and command.targeting == "Sweep":
							print("%s attacks the front line with %s." % (attacker.name, attacker.command), end = " ")
						elif command.targeting not in ("All Enemies", "Allies", "All"):
							attacker.command = "None"  # Is there a way to remove this?
							print("%s did nothing." % attacker.name)
						continue

					# Combat parameters
					barriers = []
					target = combatants[defender]
					tar_position = target.position
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

					if command.targeting in ("Single", "Sweep"):
						if command.targeting == "Single":
							print("%s attacks %s with %s." % (attacker.name, target.name, attacker.command), end = " ")
						if foe == 0 and command.targeting == "Sweep":
							print("%s attacks the front line with %s." % (attacker.name, attacker.command))
						if command.remaining <= 3:
							print("**%d uses left!**" % command.remaining, end = " ")

						# Blockable logic
						if "Never miss" not in command.effect:
							blockable = True
						if (def_target_type == "Block" or "Block" in def_command_effect) and blockable and target.isActive():
							block_roll = random.randint(1,100)
							if block_roll <= (commands.loc[target.command, "Percent"] + target.getAgility()):
								blocked = True

						# SETTING HIT CHANCE
						if "Never miss" not in command.effect:
							hit_chance = hitScore(command, attacker, target.evasion)
						# Magic attacks always hit, as does a weapon with the Never miss property
						else:
							hit_chance = 100
						# DETERMINE HIT
						hit_count = 0
						# For Multi-hit attacks, this will loop more than once
						for hit in range(int(command.hits)):
							hit_roll = random.randint(1,100)
							if hit_roll <= hit_chance:
								hit_count += 1
								hit_chance -= 2*hit_count   # Modification: hit chance drops after a successful hit? Should this happen differently based on command?
						if hit_count == 0:
							if command.targeting == "Single":
								print("Missed!")
							else:
								print("--Missed %s!" % target.name)
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
								if cut_roll > (cut_base + attacker.current_Str):
									print("Missed!")
									continue
								else:
									cut_check = attacker.getStrength() + command.percent
									# Check for weapon resistance and whether the attack was blocked (then again, a blocked attack wouldn't get here...)
									if checkResistance(target, "Weapon", barriers):
										cut_check = int(cut_check * cut_chance)
									if blocked:
										cut_check = int(cut_check * cut_chance)
									if cut_check > target.getDefense() and target.family != "God":
										applyCondition("Stun", target, False)
										print("%s was cut." % target.name)
										continue
									else:
										print("Too hard to cut.")
										continue

							# Reflect - change target into the attacker
							if ("Reflect" in def_command_effect or def_target_type == "Reflect") and command.att_type == "Magic":
								print("%s reflected the spell with %s." % (target.name, target.command), end = " ")
								# Makes the attacker into the target of its own spell
								target = attacker

							# Nullify - end the attack since it was nullified on target
							if ("Nullify" in def_command_effect or def_target_type == "Nullify") and command.att_type == "Magic":
								print("%s repulsed the spell with %s." % (target.name, target.command))
								continue

							# Check for barriers and their effects
							if target.role == "Enemy":
								buildResistances(enemy_barriers, barriers, commands)
							else:
								buildResistances(player_barriers, barriers, commands)
							
							# Check total resists against Element
							if checkResistance(target, command.element, barriers):
								# Elemental resistance was found, but it's a melee attack so it can't be resisted
								if command.element != "None" and command.att_type in ("Melee", "Ranged"):
									dmg_reduction = True
								else:
									print("%s is strong against %s." % (attacker.targets[foe], command.name), end = " ")
									# if command.status != "None" and command.stat != "Status":
									# 	pass
									# else:
									continue
							else:
								# Check for elemental / species weakness
								if command.element != "None":
									if checkWeakness(command.element, target):
										print("Hits weakness.", end = " ")
										if command.att_type != "Magic" and mightyBlow(target, crit_chance):
											continue
										else:
											critical_hit = True
							
							# Check total resists against Status
							if checkResistance(target, command.status, barriers):
								print("%s is strong against %s." % (attacker.targets[foe], command.name), end = " ")
								if command.stat != "Status":
									pass
								else:
									continue

							if "Critical" in command.effect:
								if mightyBlow(target, crit_chance):
									continue
								else:
									critical_hit = True

							if command.status != "None":
								inflictCondition(command, attacker, target, True)
							# One pass for most attacks, but accumulates damage for multi-hit attacks
							for hit in range(hit_count):
								offense = rollDamage(command, attacker)
								defense = determineDefense(target, command, offense)
								damage += offense - defense
							# Ranged attacks get blocked for 50% damage
							if blocked == True:
								damage = int(damage * blocked_ranged_mult)
							# If weapon resistance is found against a non-magical attack, damage is halved
							if command.att_type in ("Melee", "Ranged") and checkResistance(target, "Weapon", barriers) and "Pierce" not in command.effect:
								damage = int(damage * weapon_res_mult)
							if critical_hit == True:
								if command.att_type in ("Melee", "Ranged"):
									damage = int(damage * critical_mult)
								# Reset damage for a single-target magic critical
								else:
									damage = offense + 5 * command.multiplier # Add 5 mana to magic attack against weakness
							if def_target_type == "Counter":
								damage = int(damage * counter_protection_mult)

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
								if command.targeting == "Single":
									print("%d damage." % damage, end = " ")
								else:
									print("--%d damage to %s." % (damage, target.name), end = " ")
								if applyDamage(damage, target) == 1:
									print("%s fell." % target.name)
								# elif "Stop" in command.effect:
								# 	stop_roll = random.randint(1, 100)
								# 	if stop_roll <= command.percent:
								# 		print("Stopped.")
								# 		target.command = "None"
								# 		target.
								# 	else:
								# 		print("")
								else:
									print("")

							# Counter-attacks if any exist and the target survived
							if target.isActive() and (def_target_type == "Counter" or "Counter" in def_command_effect):
								r_uses = 0
								skill_slot = 0
								if target.role in ("Player", "NPC"):
									skill_slot = target.skillSlot()
									r_uses = players.loc[target.name, "S%d Uses Left" % skill_slot]
								else:
									r_uses = int(commands.loc[target.command, "#Uses"] * remaining_uses_for_enemies_mult)
								counter_command = Command(target.command, commands, r_uses)
								if target.role == "Enemy":
									buildResistances(player_barriers, barriers, commands)
								else:
									buildResistances(enemy_barriers, barriers, commands)
								counterAttack(target, attacker, counter_command, damage / counter_protection_mult, barriers)
								print("")

					elif command.targeting in ("Group", "All Enemies"):
						if command.targeting == "Group" and target.role == "Enemy":
							print("%s attacks %s group with %s." % (attacker.name, attacker.targets[foe], attacker.command), end = " ")
							if command.remaining <= 3:
								print("**%d uses left!**" % command.remaining, end = " ")
						elif command.targeting == "Group" and target.role in ("Player", "NPC"):
							print("%s attacks %s with %s." % (attacker.name, attacker.targets[foe], attacker.command), end = " ")
						else:
							# Only print the command text the first time through
							if foe == 0:
								print("%s attacks all enemies with %s." % (attacker.name, attacker.command), end = " ")
								if command.remaining <= 3:
									print("**%d uses left!**" % command.remaining)
								else:
									print("")
							print("--", end = "")

						group_hits = 0
						group_misses = 0
						inflicted = 0
						nullify_count = 0
						block_count = 0

						# Iterate through every enemy in a Group to allow for misses or nullifies to be tallied
						for each in range(len(combatants)):
							if combatants[each].name == target.name and combatants[each].isTargetable():
								iter_target = combatants[each]
								if iter_target.command != "None":
									foe_target_type = commands.loc[iter_target.command, "Target Type"]
									foe_command_effect = commands.loc[iter_target.command, "Effect"]
								else:
									foe_target_type = "None"
									foe_command_effect = "None"

								# Blockable logic - attack must be Melee or Ranged and not have the "Never miss" property
								if command.att_type in ("Melee", "Ranged") and "Never miss" not in command.effect:
									blockable = True
								if (foe_target_type == "Block" or "Block" in foe_command_effect) and blockable and iter_target.isActive():
									block_roll = random.randint(1,100)
									if block_roll <= (commands.loc[iter_target.command, "Percent"] + iter_target.getAgility()):
										blocked = True

								# SETTING HIT CHANCE
								if command.att_type in ("Melee", "Ranged") and "Never miss" not in command.effect:
									hit_chance = hitScore(command, attacker, iter_target.evasion)
								# Magic attacks always hit, as does a weapon with the Never miss property
								else:
									hit_chance = 100
								# DETERMINE HIT
								hit_roll = random.randint(1,100)
								if hit_roll <= hit_chance:
									group_hits += 1

								# Melee attacks get blocked fully (even status-based ones)
								# Added Ranged to the list for Group and All Enemy attacks
								if (blocked == True and command.att_type in ("Melee", "Ranged")):
									group_misses += 1
									block_count += 1

								# Nullify - end the attack since it was nullified on target
								if ("Nullify" in foe_command_effect or foe_target_type == "Nullify") and command.att_type == "Magic":
									group_misses += 1
									nullify_count += 1
								
								group_hits = group_hits - group_misses

						# Reflect - change target into the attacker
						# Cannot be used by monsters that can appear in groups due to group issues. Would require calling all combat code below
						# inside the Reflect check
						if ("Reflect" in def_command_effect or def_target_type == "Reflect") and command.att_type == "Magic":
							print("%s reflected the spell with %s." % (target.name, target.command), end = " ")
							target = attacker

						# Check resistances
						if target.role == "Enemy":
							buildResistances(enemy_barriers, barriers, commands)
						else:
							buildResistances(player_barriers, barriers, commands)
						if checkResistance(target, command.element + " " + command.status, barriers):
							print("%s is strong against %s." % (target.name, command.name), end = " ")
							continue
						else:
							# Currently, no damage component with Debuff abilities. No resistance either...add it?
							if "Debuff" in command.effect:
								target = affectStat(target, command)
								print("") # REMOVE THIS ONCE STAT GETS CHANGED IN affectStat FUNCTION
								continue
							if command.status != "None":
								for who in range(len(combatants)):
									if combatants[who].name == target.name and combatants[who].isTargetable():
										if target.role in ("Player", "NPC"):
											inflictCondition(command, attacker, combatants[who], True)
										else:
											inflicted += inflictCondition(command, attacker, combatants[who], False)
							offense = rollDamage(command, attacker)
							defense = determineDefense(target, command, offense)

							# Check for elemental / species weakness
							if command.element != "None":
								if checkWeakness(command.element, target):
									print("Hits weakness.", end = " ")
									if command.att_type == "Magic":
										offense = offense + 5 * command.multiplier # Add 5 mana to magic attack against weakness
										defense = 0
									else:
										critical_hit = True
							
							# No multi-hit ranged attacks
							damage = offense - defense

							# Ranged attacks get blocked for 50% damage
							# Bug:  blocked will only be true if the last enemy in a group blocked the attack.
							# Temp fix:  add blocked ranged group attacks to the miss count.
							# if blocked == True:
							# 	damage = int(damage/2)

							# If weapon resistance is found against a non-magical attack, damage is halved
							if command.att_type in ("Melee", "Ranged") and checkResistance(target, "Weapon", barriers) and "Pierce" not in command.effect:
								damage = int(damage * weapon_res_mult)
							if critical_hit == True:
								damage = int(damage * critical_mult)

						# No damage on pure Status attacks
						if inflicted > 0:
							print("%d %ss were afflicted with %s." % (inflicted, target.name, command.status), end = " ")
						if command.stat == "Status":
							print("")
							continue
						if damage <= 0:
							damage = 0
							print("No damage.")
						else:
							# Loop through combatants to deal damage to all members of a group
							num_hits = 0
							body_count = 0
							if group_hits > 0:
								who = 0
								while num_hits < group_hits and who < len(combatants):
									if combatants[who].name == target.name and combatants[who].isTargetable() and combatants[who].position == tar_position:
										body_count += applyDamage(damage, combatants[who])
										num_hits += 1
										tar_position += 1
										who = 0
									else:
										who += 1

								# REVISIT TO MAKE PRINTING MORE FLEXIBLE BASED ON RESULTS (deaths, no deaths, single character group, etc)
								if target.role == "Enemy":
									if group_hits > 1:
										print("%d damage to %d %ss." % (damage, group_hits, target.name), end = " ")
									else:
										print("%d damage to %d %s." % (damage, group_hits, target.name), end = " ")
								else:
									print("%d damage to %s." % (damage, target.name) , end = " ")
								# if group_hits > 0:
								# 	print("Hit %d." % group_hits)
								if body_count > 0 and target.role == "Enemy":
									print("Defeated %d." % body_count)
								elif body_count == 1 and target.role in ("Player", "NPC"):
									print("%s fell." % target.name)
								else:
									print("")
							else:
								if block_count > 0:
									print("Blocked by %s." % target.name)
								elif nullify_count > 0:
									print("%s repulsed the spell." % target.name)
								else:
									print("Missed!")

					elif command.targeting == "Ally":
						print("%s uses %s for %s." % (attacker.name, attacker.command, attacker.targets[foe]), end = " ")
						if command.remaining <= 3:
							print("**%d uses left!**" % command.remaining, end = " ")
						# Reflect - change target into the caster
						if ("Reflect" in def_command_effect or def_target_type == "Reflect") and command.att_type == "Magic":
							print("%s reflected the spell with %s." % (target.name, target.command), end = " ")
							target = attacker
						# Nullify - end the effect since it was nullified on target
						elif ("Nullify" in def_command_effect or def_target_type == "Nullify") and command.att_type == "Magic":
							print("%s repulsed the spell with %s." % (target.name, target.command))
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
						if command.remaining <= 3:
							print("**%d uses left!**" % command.remaining, end = " ")
						if "Buff" in command.effect:
							attacker = affectStat(attacker, command)

					elif command.targeting == "Allies":
						if foe == 0:
							print("%s uses %s." % (attacker.name, attacker.command), end = " ")
							if command.remaining <= 3:
								print("**%d uses left!**" % command.remaining, end = " ")
							else:
								print("")

						for who in range(len(combatants)):
							if combatants[who].name == attacker.targets[foe]:
								print("--", end = "")
								# Reflect - change target into the caster
								if ("Reflect" in def_command_effect or def_target_type == "Reflect") and command.att_type == "Magic":
									print("%s reflected the spell with %s." % (target.name, target.command), end = " ")
									target = attacker
								# Nullify - end the effect since it was nullified on target
								elif ("Nullify" in def_command_effect or def_target_type == "Nullify") and command.att_type == "Magic":
									print("%s repulsed the spell with %s." % (target.name, target.command), end = " ")
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
				# If attacker did nothing due to no surviving target, count no action as having been taken
				if attacker.command != "None":
					combatants[count] = afterTurn(attacker, commands.loc[attacker.command, "Growth Stat"], players)
				
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
					print("")
					postBattle(combatants, m_skills, growth, commands, players)
					another_round = "n"
					break

			# If the battle didn't end, perform end of round operations
			if another_round != "n":
				for each in range(len(combatants)):
					combatants[each] = endOfTurn(combatants[each], commands)

				# Reset surprise flags
				enemy_surprise = False
				enemy_warning = False
				player_surprise = False
				player_warning = False

				# Provide options to GM at the end of a round
				post_round = "n"
				sys.stdout = stdout
				while post_round != "y":
					# GM SUMMARY - Print block to show status between rounds to determine if battle should continue
					for each in range(len(party_order)):
						pos = party_order[each][2]
						print("| %s: %d/%d %s" % (combatants[pos].name, combatants[pos].current_HP, combatants[pos].HP, combatants[pos].characterStatus()), end = " |")
					print("")
					# Print enemy status line at the end of a simulation - TURN INTO A FUNCTION
					enemy_list = []
					for enemy in range(len(enemy_groups)):
						for count in range(len(combatants)):
							if combatants[count].role == "Enemy" and combatants[count].isTargetable() and combatants[count].name == enemy_groups[enemy][0]:
								enemy_list.append(combatants[count].name)
					remaining_enemies = Counter(enemy_list)
					remaining_enemies.keys()

					for key, number in remaining_enemies.items():
						print("{ %s - %d" % (key, number), end = " }")
					# END SUMMARY BLOCK
					print("")
					print("----------------------------------------")
					print("1. Run another round")
					print("2. Change commands/targets")
					print("3. End this battle")
					print("----------------------------------------")
					while True:
						mid_bat = int(input("Enter a number: "))
						try:
							mid_bat = int(mid_bat)
						except ValueError:
							mid_bat = input("Invalid entry.", end = " ")
							continue
						break
					if mid_bat == 1:
						post_round = "y"
					elif mid_bat == 2:
						for each in range(len(party_order)):
							pos = party_order[each][2]
							if combatants[pos].isActive():
								print("%d. %s: %s" % (each+1, party_order[each][0], combatants[pos].skills))
							else:
								print("%d. %s: %s" % (each+1, party_order[each][0], combatants[pos].characterStatus()))
						while True:
							which_pc = input("Which character? Enter a number: ")
							#which_pc -= 1
							try:
								which_pc = int(which_pc)
							except ValueError:
								which_pc = input("Invalid entry. Try again: ")
								continue
							else:
								which_pc -= 1
							break

						which_command = input("Enter the command: ")
						which_target = input("Enter the target: ")
						change = party_order[which_pc][2]
						combatants[change].command = which_command
						combatants[change].target_type = which_target
					else:
						another_round = "n"
						break

		# Print party status line at the end of a simulation
		sys.stdout = open(text_path, 'a')
		print("")
		for each in range(len(party_order)):
			pos = party_order[each][2]
			print("| %s: %d/%d %s" % (combatants[pos].name, combatants[pos].current_HP, combatants[pos].HP, combatants[pos].characterStatus()), end = " [")
			# Print skill counts at the end of a battle
			for skill in range(len(combatants[pos].skills)):
		 		if combatants[pos].uses[skill] < 1:
		 			pass
		 		else:
		 			print("%s-%d" % (combatants[pos].skills[skill], combatants[pos].uses[skill]), end = ", ")
			print("]")
		#print("")

		# Print enemy status line at the end of a simulation
		enemy_list = []
		for enemy in range(len(enemy_groups)):
			for count in range(len(combatants)):
				if combatants[count].role == "Enemy" and combatants[count].isTargetable() and combatants[count].name == enemy_groups[enemy][0]:
					enemy_list.append(combatants[count].name)

		remaining_enemies = Counter(enemy_list)
		remaining_enemies.keys()
		for key, number in remaining_enemies.items():
			print("{ %s - %d" % (key, number), end = " }")
		print("")
		print("")

		sys.stdout = stdout
		print("Battle ended.")
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
				active_battle.iloc[count,19] = combatants[count].environment
				active_battle.iloc[count,20] = combatants[count].actions_taken
				active_battle.iloc[count,21] = combatants[count].stats_used
				if combatants[count].role in ("Player", "NPC"):
					# Logic to set uses in Players table equal to those tracked during combat
					for slot in range(len(combatants[count].skills)):
						players.loc[combatants[count].name, "S%d Uses Left" % slot] = combatants[count].uses[slot]
					# Update all adjustable stats
					players.loc[combatants[count].name, "HP"] = combatants[count].HP
					players.loc[combatants[count].name, "Current HP"] = combatants[count].current_HP
					players.loc[combatants[count].name, "Natural STR"] = combatants[count].natural_str
					players.loc[combatants[count].name, "Natural AGL"] = combatants[count].natural_agl
					players.loc[combatants[count].name, "Natural MANA"] = combatants[count].natural_mana
					players.loc[combatants[count].name, "Natural DEF"] = combatants[count].natural_def
					players.loc[combatants[count].name, "GOLD"] = combatants[count].gold
					save_players.append(combatants[count].name)
			battles[i] = active_battle.copy()
			save_list.append(tuple((i, log.sheet_names[i+2])))

		# print("1. Run another battle")
		# print("2. Reload a battle")
		# print("3. Exit")
		# next_bat = input("Enter a number: ")
		# if next_bat == 2:
		# 	for bat in range(len(battles)):
		# 		print("%d. %s" % (bat+1, log.sheet_names[bat+1]))
		# 	reload_bat = int(input("Which battle do you want to reload? Enter a number: "))
		# 	reload_bat -= 1
		# 	battles.remove(reload_bat)
		# 	battles.append(log.parse(reload_bat))

		run_sim = input("Run another battle (y/n)?: ")
		# elif next_bat == 3:
		# 	run_sim = "n"
		# else:
		# 	run_sim = "y"

	# Write all battles that were run to the Battle Results file
	for bat in range(len(save_list)):
		battles[save_list[bat][0]].to_excel(writer, sheet_name = save_list[bat][1])

	# Write the PCs and NPCs that acted to the Battle Results file "Players" tab
	if len(save_list) > 0:
		# SEE SAVED LINK IN PYTHON FOLDER ON HOW TO WRITE DIRECTLY TO A SPECIFIED COLUMN IN A SHEET
		players.to_excel(writer, sheet_name = "Player Updates")
		#players.to_excel(writer, sheet_name = "Players")
		writer.save()

elif operation == 2:
	# Print Character Snapshots
	# char_sheets = input("Print character sheets (y/n)?: ")
	for count in range(len(players.index)):
		if players.iloc[count,0] == "blank" or players.iloc[count,2] == "NPC":
			pass
		else:
			print("%s || %s" % (players.iloc[count, 0], players.iloc[count, 2]))
			print("CLASS: %s" % players.iloc[count, 3])
			print("HP: %d | STR: %d | DEF: %d | AGL: %d | MANA: %d" % (players.iloc[count, 5],players.iloc[count, 7],
			players.iloc[count, 9],players.iloc[count, 11],players.iloc[count, 13]))
			print("[", end = "")
			skill = 14
			while skill < 38:
				if skill < 35:
					if players.iloc[count,skill] == "blank":
						print("EMPTY", end = ", ")
					elif players.iloc[count,skill+1] in (-1, -2):
						print(players.iloc[count,skill], end = ", ")
					else:
						print(players.iloc[count,skill], end = " - ")
						print(players.iloc[count,skill+1], end = ", ")
					skill += 3
				else:
					if players.iloc[count,skill] == "blank":
						print("EMPTY", end = "]\n")
					elif players.iloc[count,skill+1] in (-1, -2):
						print(players.iloc[count,skill], end = "]\n")
					else:
						print(players.iloc[count,skill], end = " - ")
						print(players.iloc[count,skill+1], end = "]\n")
					break
			print("MAGI: %s" % players.iloc[count, 38])
			print("OTHER MAGI: %s" % players.iloc[count, 41])
			print("INVENTORY: %s" % players.iloc[count,42])
			print("GOLD: %d" % players.iloc[count,43])
			print("")
elif operation == 3:
	more = "y"
	while more != "n":
		not_monsters = ["Human", "Mutant", "Robot"]
		monster_players = players[players["CLASS"].isin(not_monsters) == False]
		mp = monster_players.loc[players["PLAYER"].isin(["NPC"]) == False]
		print(mp["CLASS"])
		who = input("Transform which character?: ")
		meat = input("Meat from which monster?: ")
		current_monster = mp.loc[who, "CLASS"]

		meat_type = ""
		meat_class = 0
		meat_add = 0
		meat_subtract = 0
		current_ds = 0
		current_class = 0
		current_type = ""
		new_monster = ""
		type_diff = 0
		variant = False
		variation = ""

		for row in range(transformations.shape[0]):
			for col in range(transformations.shape[1]):
				if transformations.iloc[row,col] == meat:
					meat_ds = transformations.iloc[row,col+1]
					meat_class = transformations.loc[row,"FAMILY"]
					meat_type = transformations.loc[row,"MEAT TYPE"]
					meat_add = transformations.loc[row,"ADD"]
					meat_subtract = transformations.loc[row,"SUBTRACT"]
				elif transformations.iloc[row,col] == current_monster:
					current_ds = transformations.iloc[row,col+1]
					current_class = transformations.loc[row,"FAMILY"]
					current_type = transformations.loc[row,"MEAT TYPE"]

		if current_type in ("A", "B") and meat_type == "C":
			type_diff = 1
		elif current_type in ("B", "C") and meat_type == "A":
			type_diff = -1

		next_class = int(current_class + meat_add + type_diff)
		if next_class > monster_race_cap:
			next_class = int(current_class + meat_subtract + type_diff)

		max_ds = max(current_ds, meat_ds)

		family_tree = []
		col = 4
		while col < transformations.shape[1]:
			if not pandas.isnull(transformations.iloc[next_class,col]):
				family_tree.append(tuple((transformations.iloc[next_class,col], transformations.iloc[next_class,col+1])))
			col += 2

		for member in range(len(family_tree)):
			if member == 0 and max_ds <= family_tree[member][1]:
				new_monster = family_tree[member][0]
				break
			elif max_ds < family_tree[member][1]:
				new_monster = family_tree[member-1][0]
				break
			else:
				new_monster = family_tree[member][0]

		new_HP = monsters.loc[new_monster, "HP"]
		new_Str = monsters.loc[new_monster, "Str"]
		new_Agl = monsters.loc[new_monster, "Agl"]
		new_Mana = monsters.loc[new_monster, "Mana"]
		new_Def = monsters.loc[new_monster, "Def"]
		ds_diff = current_ds - monsters.loc[new_monster, "DS"]
		stat_increase = 0

		if monsters.loc[new_monster, "DS"] <= current_ds and current_ds < 11 and random.randint(1,2) == 2:
			variant = True
			variant_roll = random.randint(1,11)
			if variant_roll < 6:
				variation = "Increased stats."
				stat_increase = 1 + max((5*ds_diff)/100,0.1)
				new_HP = int(new_HP * stat_increase)
				new_Str = max(new_Str + 1, int(new_Str * stat_increase))
				new_Agl = max(new_Agl + 1, int(new_Agl * stat_increase))
				new_Mana = max(new_Mana + 1, int(new_Mana * stat_increase))
				new_Def = max(new_Def + 1, int(new_Def * stat_increase))
			elif variant_roll < 11:
				variation = "Evolved skill."
			else:
				variation = "Increased stats and evolved skill."
				stat_increase = 1 + max((5*ds_diff)/100,0.1)
				new_HP = int(new_HP * stat_increase)
				new_Str = int(new_Str * stat_increase)
				new_Agl = int(new_Agl * stat_increase)
				new_Mana = int(new_Mana * stat_increase)
				new_Def = int(new_Def * stat_increase)
		
		print("%s changed from %s to %s." % (who, current_monster, new_monster), end = " ")
		if variant == True:
			print("VARIANT: %s" % variation)
		else:
			print('\n')
		print("HP: %d | STR: %d | AGL: %d | MANA: %d | DEF: %d" % (new_HP, new_Str, new_Agl, new_Mana, new_Def))
		print("[", end = "")
		for skill in range(8):
			if skill < 7:
				print(monsters.loc[new_monster, "S%d" % skill], end = ", ")
			else:
				print(monsters.loc[new_monster, "S%d" % skill], end = "]\n")

		more = input("Another transformation? (y/n): ")


	#print("Current: %s | Meat Class: %d | Meat Type: %s" % (current_class, meat_class, meat_type))
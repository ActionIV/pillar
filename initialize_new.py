import pandas
import random
import operator
from classes import Player, Enemy, NPC, Actor
from combat import random_target

path1 = r"FFL2 Data.xlsx"
path2 = r"Battle Log.xlsx"

workbook = pandas.ExcelFile(path1)
log = pandas.ExcelFile(path2)

monsters = workbook.parse("Monster", index_col = 'Index', dtype = str)
#monsters = pandas.read_excel(workbook, "Monster", index_col = 0)
commands = workbook.parse("Weapon", index_col = 'Index', dtype = str)
#commands = pandas.read_excel(workbook, 'Weapon')
ms_prob = workbook.parse("Move Probability")
#ms_prob = pandas.read_excel(workbook, 'Move Probability')
players = workbook.parse("Players", index_col = 'Index', dtype = str)

# Loop through each sheet of the battle log, appending each to the battles list
battles = []

for count in range(len(log.sheet_names)):
	battles.append(log.parse(count, index_col = 'Index', dtype = str))

# This is where a function for creating the combatants list from a battle should be. Call would pass an int to say from which Log sheet to pull
# Might even pass the sheet itself from battles[]. Would return combatants list
combatants = []	

print(log.sheet_names)
i = int(input("Which battle do you want to run? Enter a number: "))
print("Running a round for Battle", i)

# Setting to the list index of the number chosen
i=i-1

# Need to track the right spot in combatants, which conflicts with 'count' due to enemy "lives" inflating the list vs the Log
place = 0
party_order = []

# I would prefer to be doing label lookups with Pandas loc instead of iloc, but I can't get the indexing right (at load time)
for count in range(len(battles[i].index)):
	# Enemy groups require a for loop to create individual Actors for tracking initiative, deaths, etc.
	if battles[i].iloc[count,1] == "Enemy":
		for pos in range(int(battles[i].iloc[count,2])):
			combatants.append(Enemy(battles[i].iloc[count,0]))
			combatants[place].position = pos + 1
			combatants[place].lives = 1
			place += 1

	elif battles[i].iloc[count,1] == "Player":
		combatants.append(Player(battles[i].iloc[count,0]))
		combatants[count].position = battles[i].iloc[count,3]
		party_order.append(tuple((combatants[count].name, combatants[count].position)))
		place += 1

	else:
		combatants.append(NPC(battles[i].iloc[count,0]))
		combatants[count].position = battles[i].iloc[count,3]
		party_order.append(tuple((combatants[count].name, combatants[count].position)))
		place += 1

party_order.sort(key = operator.itemgetter(1))

# DATA ASSIGNMENT LOOP
# Ridiculously big loop to go through combatants list, assign static values, retrieve dynamnic combat info, determine initiative, and assign commands
for count in range(len(combatants)):
	current_com = combatants[count]

	current_com.current_HP = battles[i].loc[current_com.name, "CURRENT HP"]
	current_com.current_Str = battles[i].loc[current_com.name, "CURRENT STR"]
	current_com.current_Agl = battles[i].loc[current_com.name, "CURRENT AGL"]
	current_com.current_Mana = battles[i].loc[current_com.name, "CURRENT MANA"]
	current_com.current_Def = battles[i].loc[current_com.name, "CURRENT DEF"]
	current_com.command = battles[i].loc[current_com.name, "COMMAND"]
	current_com.target_type = battles[i].loc[current_com.name, "TARGET"]
	current_com.status = battles[i].loc[current_com.name, "STATUS"]
	
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

# BEGIN COMBAT ROUND - should eventually be a repeatable function based on number of rounds to run
for count in range(len(combatants)):
	# INITIATIVE
	# Should use current_AGL, but just use Agl for now. Also want to make it more variable at some point
	combatants[count].initiative = float(combatants[count].Agl) * (1+(random.randint(1,25)/100))

	# Sort actors based on initiative score
	combatants = sorted(combatants, key = operator.attrgetter("initiative"))

	# STATUS CHECK

	# ENEMY COMMAND SELECTION - uses Move Probability table based on MS
	# Could also be used for random ability selection for players if an appropriate MS were assigned
	if combatants[count].command == 'nan':
		row = combatants[count].MS
		for choice in range(7):
			roll = random.randint(0,255)
			if roll < ms_prob.iloc[int(row), choice+1]:
				combatants[count].command = combatants[count].skills[choice]
				break
			else:
				continue
	# Based on the Command, assign the Target Type to the Target line
	if combatants[count].role != "Player":
		combatants[count].target_type = commands.loc[combatants[count].command, "Target Type"]

	# Convert the Target Type to an actual target where applicable (i.e. not the "All" abilities)
	# Should this go in the combat code instead of setup?
	sel_target = ""
	if combatants[count].target_type == "Single":
		for choice in range(len(party_order)):
			roll = random.randint(1,100)
			if roll < 51:
				sel_target = party_order[choice][0]
			else:
				continue

		if not sel_target:
			sel_target = random_target(party_order)

		combatants[count].add_target(sel_target)

	# elif combatants[count].target_type == "Group":
	# 	for choice in range(len(party_order)):
	# 		roll = random.randint(1,100)
	# 		if roll < combatants[count].current_Mana

for count in range(len(combatants)):
	print(combatants[count])
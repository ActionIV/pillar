import random

class Actor(object):
	def __init__(self, name):
		self.name = name
		self.actions_taken = ""
		self.stats_used = ""
		self.targets = []
		self.resists = []
		
	def getName(self):
		return self.name

	def __str__(self):
		return "%s = %s, commands = %s, target = %s" % (self.name, self.role, self.actions_taken, self.target_type)

	def addAction(self, command, stat_used):
		if not self.actions_taken:
			self.actions_taken = command
		else:
			self.actions_taken = self.actions_taken + ", " + command
		if self.role != "Enemy":
			if not self.stats_used:
				self.stats_used = stat_used
			else:
				self.stats_used = self.stats_used + ", " + stat_used
		else:
			if stat_used in ("Nemesis"):
				self.stats_used = stat_used

	def add_target(self, target):
		self.targets.append(target)

	def isStoned(self):
		return True if self.stoned == "y" else False
	def isCursed(self):
		return True if self.cursed == "y" else False
	def isBlinded(self):
		return True if self.blinded == "y" else False
	def isStunned(self):
		return True if self.stunned == "y" else False
	def isAsleep(self):
		return True if self.asleep == "y" else False
	def isParalyzed(self):
		return True if self.paralyzed == "y" else False
	def isPoisoned(self):
		return True if self.poisoned == "y" else False
	def isConfused(self):
		return True if self.confused == "y" else False
	def isStopped(self):
		return True if self.stopped == "y" else False

	# Decrement lives upon death. Shouldn't need a dead flag that way
	def isDead(self):
		if self.lives == 0:
			return True
		else:
			return False

	def isTargetable(self):
		if self.isDead() or self.isStoned() or self.isSomethingElse():
			return False
		else:
			return True

	def isActive(self):
		if (self.isDead() or self.isStoned() or self.isParalyzed() or self.isAsleep() or self.isStopped()):
			return False
		else:
			return True

	def isBlocking(self):
		block_roll = random.randint(1,100)
		if self.blocking <= block_roll:
			return True
		else:
			return False
	
	# This should be used for unending environment effects or second actions for bosses
	def isSomethingElse(self):
		return True if self.environment == "y" else False

	def characterStatus(self):
		status = []
		if self.isDead():
			return "STUN"
		if self.isStoned():
			status.append("STON")
		if self.isCursed():
			status.append("CURS")
		if self.isBlinded():
			status.append("BLND")
		if self.isAsleep():
			status.append("SLEP")
		if self.isParalyzed():
			status.append("PARA")
		if self.isPoisoned():
			status.append("POIS")
		if self.isConfused():
			status.append("CONF")
		
		condition = ",".join(status)
		return condition

	role = ""
	lives = 1
	position = 0
	group = 0
	initiative = 0
	current_HP = 0
	current_Str = 0
	current_Agl = 0
	current_Mana = 0
	current_Def = 0
	command = ""
	target_type = ""
	stoned = "n"
	cursed = "n"
	blinded = "n"
	asleep = "n"
	stunned = "n"
	paralyzed = "n"
	poisoned = "n"
	confused = "n"
	stopped = "n"
	environment = "n"
	df_index = 0
	natural_str = 0
	natural_agl = 0
	natural_mana = 0
	natural_def = 0
	evasion = 0
	blocking = 0
	has_used_skill_this_turn = False # Could turn this into a count to allow for retributive "shield" attacks based on number of hits taken in a round
		
class Enemy(Actor):
	def __init__(self, name):
		Actor.__init__(self, name)
		self.skills = []
	
	def getRole(self):
	 	return self.role

	def getRace(self):
		if self.Type == 0:
			return "Human"
		elif self.Type == 1:
			return "Mutant"
		elif self.Type == 2:
			return "Monster"
		elif self.Type == 3:
			return "Robot"

	def getStrength(self):
		strength = self.current_Str
		if self.isCursed():
			# Undead gain a 20% boost from being Cursed
			if self.family == "Undead":
				strength = int(strength * 1.2)
			else:
				strength = int(strength/2)
		return strength

	def getAgility(self):
		agility = self.current_Agl
		if self.isParalyzed() or self.isAsleep():
			return 0
		if self.isBlinded():
			agility = int(agility/2)
		return agility

	def getMana(self):
		return self.current_Mana

	def getDefense(self):
		defense = self.current_Def
		if self.isCursed():
			# Undead gain a 20% boost from being Cursed
			if self.family == "Undead":
				defense = int(defense * 1.2)
			else:
				defense = int(defense/2)
		return defense

	def getEvasion(self, commands):
		evasion = self.current_Agl
		if "Evasive" in commands.loc[self.command, "Effect"]:
			evasion += commands.loc[self.command, "Percent"]
		return evasion

	role = "Enemy"
	MS = 0
	DS = 0
	Type = 0
	HP = 0
	Str = 0
	Agl = 0
	Mana = 0
	Def = 0
	family = ""
	enemy_group_num = 0
		
class Player(Actor):
	role = "Player"
	Class = ""
	DS = 0
	family = ""
	HP = 0
	Str = 0
	Agl = 0
	Mana = 0
	Def = 0
	magi = ""
	magi_count = 0
	gold = 0

	def __init__(self, name):
		Actor.__init__(self, name)
		self.skills = []
		self.uses = []
	
	def getRole(self):
	 	return self.role

	def getRace(self):
		if self.Class in ("Human", "Mutant", "Robot"):
			return self.Class
		else:
			return "Monster"

	def getStrength(self):
		strength = self.current_Str
		if self.isCursed():
			strength = int(strength/2)
		if self.magi == "Power Magi":
			strength += (5+self.magi_count)
		return strength

	def getAgility(self):
		agility = self.current_Agl
		if self.isParalyzed() or self.isAsleep():
			return 0
		if self.isBlinded():
			agility = int(agility/2)
		if self.magi == "Speed Magi":
			agility += (5+self.magi_count)
		return agility

	def getMana(self):
		mana = self.current_Mana
		if self.magi == "Mana Magi":
			mana += (5+self.magi_count)
		return mana

	def getDefense(self):
		defense = self.current_Def
		if self.isCursed():
			defense = int(defense/2)
		if self.magi == "Defense Magi":
			defense += (5+self.magi_count)
		return defense

	def getEvasion(self, commands):
		# Penalize defense above the natural defense stat (which monsters ignore anyway)
		defense_difference = self.current_Def - self.natural_def
		evasion = self.current_Agl

		if self.magi == "Speed Magi":
			evasion += (5+self.magi_count)

		if "Evasive" in commands.loc[self.command, "Effect"]:
			evasion += commands.loc[self.command, "Percent"]

		# If STR >= DEF, then apply no penalty. Monsters use this since they're naturally balanced
		if self.getStrength() >= defense_difference or self.getRace() == "Monster":
			return evasion
		# If DEF > STR, apply a penalty equal to the difference
		else:
			return max(0, evasion + self.getStrength() - defense_difference)

	def skillSlot(self):
		for slot in range(len(self.skills)):
			if self.command == self.skills[slot]:
				return slot

class NPC(Actor):
	role = "NPC"
	MS = 0
	DS = 0
	family = ""
	HP = 0
	Str = 0
	Agl = 0
	Mana = 0
	Def = 0

	def __init__(self, name):
		Actor.__init__(self, name)
		self.skills = []
		self.uses = []
	
	def getRole(self):
	 	return self.role

	def getRace(self):
		if self.family in ("Human", "Mutant", "Robot"):
			return self.family
		else:
			return "Monster"

	def getStrength(self):
		strength = self.current_Str
		if self.isCursed():
			strength = int(strength/2)
		return strength

	def getAgility(self):
		agility = self.current_Agl
		if self.isParalyzed() or self.isAsleep():
			return 0
		if self.isBlinded():
			agility = int(agility/2)
		return agility

	def getMana(self):
		return self.current_Mana

	def getDefense(self):
		defense = self.current_Def
		if self.isCursed():
			defense = int(defense/2)
		return defense

	def getEvasion(self, commands):
		# Penalize defense above the natural defense stat (which monsters ignore anyway)
		defense_difference = self.current_Def - self.natural_def
		evasion = self.current_Agl
	#	if self.magi == "Speed Magi":
	#		evasion += (5+self.magi_count)

		if "Evasive" in commands.loc[self.command, "Effect"]:
			evasion += commands.loc[self.command, "Percent"]

		# If STR >= DEF, then apply no penalty. Monsters use this since they're naturally balanced
		if self.getStrength() >= defense_difference or self.getRace() == "Monster":
			return evasion
		# If DEF > STR, apply a penalty equal to the difference
		else:
			return max(0, evasion + self.getStrength() - defense_difference)

	def skillSlot(self):
		for slot in range(len(self.skills)):
			if self.command == self.skills[slot]:
				return slot

class Command:
	stat = ""
	uses = 0
	remaining = 0
	multiplier = 0
	att_type = ""
	targeting = ""
	element = ""
	min_dmg = 0
	rand_dmg = 0
	status = ""
	effect = ""
	hits = 1
	percent = 0
	race_bonus = ""

	def __init__(self, name, commands, remaining_uses):
		self.name = name
		self.uses = commands.loc[name, "#Uses"]
		self.remaining = remaining_uses
		self.growth = commands.loc[name,"Growth Stat"]
		self.stat = commands.loc[name,"Damage Stat"]
		self.multiplier = commands.loc[name,"Multiplier"]
		self.att_type = commands.loc[name,"Type"]
		self.targeting = commands.loc[name,"Target Type"]
		self.element = commands.loc[name,"Element"]
		self.min_dmg = commands.loc[name,"Min DMG"]
		self.rand_dmg = commands.loc[name,"Rand DMG"]
		self.status = commands.loc[name, "Status"]
		self.effect = commands.loc[name,"Effect"]
		self.hits = commands.loc[name,"Hits"]
		self.percent = commands.loc[name,"Percent"]
		self.race_bonus = commands.loc[name,"Race Bonus"]
		self.human_spirit = commands.loc[name, "Human Spirit"]
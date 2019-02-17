class Actor(object):
	def __init__(self, name):
		self.name = name
		self.actions_taken = []
		self.targets = []
		self.resists = []
		
	def getName(self):
		return self.name

	def __str__(self):
		return "%s = %s, commands = %s, target = %s" % (self.name, self.role, self.actions_taken, self.target_type)

	def add_action(self, command):
		self.actions_taken.append(command)

	def add_target(self, target):
		self.targets.append(target)

	def isStoned(self):
		return True if self.stoned == "y" else False
		# 	return True
		# else:
		# 	return False
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

	# Decrement lives upon death. Shouldn't need a dead flag that way
	def isDead(self):
		if self.lives == 0:
			return True
		else:
			return False

	def isTargetable(self):
		if self.isDead() or self.isStoned():
			return False
		else:
			return True

	def isActive(self):
		if (self.isDead() or self.isStoned() or self.isParalyzed() or self.isAsleep()):
			return False
		else:
			return True

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
		if not status:
			return "GOOD"
		
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
		
class Enemy(Actor):
	def __init__(self, name):
		Actor.__init__(self, name)
		self.skills = []
	
	def getRole(self):
	 	return self.role

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

	def __init__(self, name):
		Actor.__init__(self, name)
		self.skills = []
	
	def getRole(self):
	 	return self.role

class NPC:
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
	
	def getRole(self):
	 	return self.role

class Command:
	stat = ""
	multiplier = 0
	att_type = ""
	targeting = ""
	element = ""
	min_dmg = 0
	rand_dmg = 0
	status = ""
	effect = ""
	percent = 0

	def __init__(self, name):
		self.name = name
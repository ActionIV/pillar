class Actor(object):
	names = []
	def __init__(self, name):
		self.name = name
		self.actions_taken = []
		self.targets = []
		Actor.names.append(name)
		
	def getName(self):
		return self.name

	def __str__(self):
		return "%s = %s, command = %s, target = %s, hit = %s" % (self.name, self.role, self.command, self.target_type, self.targets)

	def add_action(self, command):
		self.actions_taken.append(command)

	def add_target(self, target):
		self.targets.append(target)

	def isStoned(self):
		if self.stoned == "y":
			return True
		else:
			return False
		
	def isCursed(self):
		if self.cursed == "y":
			return True
		else:
			return False
		
	def isBlinded(self):
		if self.blinded == "y":
			return True
		else:
			return False

	def isStunned(self):
		if self.stunned == "y":
			return True
		else:
			return False

	def isParalyzed(self):
		if self.paralyzed == "y":
			return True
		else:
			return False

	def isPoisoned(self):
		if self.poisoned == "y":
			return True
		else:
			return False

	def isConfused(self):
		if self.confused == "y":
			return True
		else:
			return False

	# Decrement lives upon death. Shouldn't need a dead flag that way
	def isDead(self):
		if self.lives == 0:
			return True
		else:
			return False

	role = ""
	lives = 1
	position = 0
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
		
class Player(Actor):
	role = "Player"
	Class = ""
	DS = 0
	Type = 0
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

class NPC:
	role = "NPC"
	MS = 0
	DS = 0
	Type = 0
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





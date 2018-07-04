class Actor(object):
	names = []
	def __init__(self, name):
		self.name = name
		self.actions_taken = []
		Actor.names.append(name)
		
	def getName(self):
		return self.name

	def __str__(self):
		return "%s is a %s, its command is %s, and its target is %s" % (self.name, self.role, self.command, self.target)

	def add_action(self, command):
		self.actions_taken.append(command)

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
	target = ""
	status = ""
		
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





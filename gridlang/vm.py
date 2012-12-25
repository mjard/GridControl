from opcodes import OPCODES

class GridLangVM(object):
	def __init__(self):
		self.data = []
		self.exe = []
		self.reg = {}
		self.pos = 0
		self.steps = 0
		self.debug = False
	
	def trace(self, *args):
		if self.debug:
			print " >> ",
			for arg in args:
				print arg,
			print ""
	
	def freeze_vm(self):
		"""Return a copy of all pertinent data structures necessary
		to store the executable state of this vm"""
		ret = {
			'data': list(self.data),
			'exe': list(self.exe),
			'reg': dict(self.reg),
			'pos': self.pos,
			'steps': self.steps,
		}
		return ret

	def thaw_vm(self, data):
		"""Reload a previously frozen state of a vm"""
		self.data = list(data['data'])
		self.exe = list(data['exe'])
		self.reg = dict(data['reg'])
		self.pos = data['pos']
		self.steps = data['steps']

	def set_code(self, code):
		"""Attach opcodes to this vm"""
		self.code = code
	
	###### VM data access methods ########
	# These methods are used in OPCODE run method to access data, use these
	# methods because exception handling is a good idea
	def pop(self, n = 1):
		"""Pop n items off of stack"""
		i = len(self.data) - n
		if i < 0:
			raise Exception("Stack empty")
		self.data, ret = self.data[:i], self.data[i:]
		if n == 1:
			ret = ret[0]
		self.trace("Pop", n, ret, self.data)
		return ret

	def append(self, *args):
		"""Push items onto stack"""
		self.data.extend(args)
		self.trace("Appending", args, self.data)
	
	def eval(self, i):
		"""If i is not a scalar resolve it out of the registry"""
		if type(i) in (int, float):
			return i
		else:
			return self.get(i)

	def store(self, key, val):
		"""Store value in the registry under key"""
		self.reg[key] = val
		self.trace("Storing", key, val, self.reg)
	
	def get(self, key):
		"""Get an item out of the registry"""
		return self.reg.get(key)


	###### VM Execution methods ##############
	def __run_step(self):
		p = self.pos
		newp = self.pos + 1
		line = self.code[p]
		cmd_s = line[0]
		args = line[1:]

		try:
			cmd = (CMD for CMD in OPCODES if CMD.match(cmd_s)).next()
		except StopIteration as e:
			raise Exception("UNKNOWN OPCODE {0}".format(cmd_s))
		if cmd is None:
			raise Exception("WTF")

		self.trace("Executing", cmd, args)
		cmd.run(args, self)

		# if command does not involve jumping go to next line
		if cmd.jump == False:
			self.exe.append(["JUMP", newp])

		while 1:
			try:
				ecmd = self.exe.pop()
			except IndexError:
				break
			# assume we're just JUMP-ing now
			self.pos = ecmd[1]

		if self.pos >= len(self.code):
			# ran off the bottom of the code
			return False
	
	def __run_forever(self):
		while 1:
			if self.__run_step() == False:
				break

	def __run_steps(self, n):
		self.steps = self.steps + n
		while 1:
			if self.__run_step() == False:
				return True
			self.steps = self.steps - 1
			if self.steps < 0:
				self.trace("Freezing")
				return False
	
	def run(self, steps = None):
		if steps is None:
			return self.__run_forever()
		else:
			return self.__run_steps(steps)

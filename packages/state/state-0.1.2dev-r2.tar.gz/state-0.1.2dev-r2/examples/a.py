# -*- coding:utf-8 -*-
import message
from state import stateful, curr, switch, behavior, State

class Switch(object):
	Turn = 'state.examples.Switch.Trun'
	def turn(self):
		message.pub(Switch.Turn, self)

	def __str__(self):
		return type(self).__name__

@stateful
class Lamp(object):
	class Off(State):
		default = True
		@behavior
		def __begin__(self):
			print '%s begin Off state.' % self

		@behavior
		def __end__(self):
			print '%s end Off state.' % self

		@behavior
		def _on_turn(self, s):
			switch(self, Lamp.On)

	class On(State):
		@behavior
		def __begin__(self):
			print '%s begin On state.' % self

		@behavior
		def __end__(self):
			print '%s end On state.' % self

		@behavior
		def _on_turn(self, s):
			switch(self, Lamp.Off)

	def bind(self, s):
		self._switch = s
		message.sub(Switch.Turn, self.on_turn)

	def on_turn(self, s):
		self._on_turn(s)

s = Switch()
l = Lamp()
l.bind(s)
print 'press'
s.turn()
print 'press'
s.turn()
#s.hello()
#print s.__name__
#s.bye()


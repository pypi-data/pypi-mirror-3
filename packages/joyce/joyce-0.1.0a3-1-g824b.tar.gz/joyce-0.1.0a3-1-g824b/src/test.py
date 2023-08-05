from mirte.core import Module
import time
from joyce.base import JoyceChannel

class Test(Module):
	def run(self):
		self.server.on_new_channel.register(self.on_new_channel)
		c = self.client.create_channel()
		c.on_message.register(self.on_message)
		c.on_stream.register(self.on_stream)
		self.last_time = 0
		c.send_message('wee')
		#for i in xrange(5):
		#	c.send_message('wee')
	def on_message(self, channel, d):
		print 'client: >>'
		#print 'streaming'
		#with open('/etc/passwd') as f:
		#	channel.send_stream(f)
		#print 'stream sent'
	def on_new_channel(self, channel):
		print "Server new channel: ", channel
		channel.on_message.register(self.on_message_s)
		channel.on_stream.register(self.on_stream_s)
		channel.send_message(100)
		self.threadPool.execute(self._wee, channel)
	
	def _wee(self, channel):
		print 'server: streaming'
		with open('/etc/passwd') as f:
			channel.send_stream(f)
		print 'stream sent'
	def on_message_s(self, channel, d):
		print 'server: >>'
		channel.send_message('wee')
		print 'server: <<'
		#c, l = d
		#if c > 100:
		#	import sys
		#	return
		#channel.send_message([c+1, l])
		#if c % 1000 ==  1:
		#	now = time.time()
		#	if self.last_time != 0:
		#		print now - self.last_time
		#	self.last_time = now
	def on_stream(self, channel, stream):
		print 'stream!'
		print stream.read()
		stream.close()
		print 'stream recvd'
	def on_stream_s(self, channel, stream):
		print 'stream s!'
		print stream.read()
		stream.close()
		print 'stream s recvd'
	def stop(self):
		pass

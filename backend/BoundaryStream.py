'''This is the Module for a boundary byte stream wrapper

protocol:

calling write(b'This is my data.')
b'boundary\\n\\nThis is my data.boundary'
is written

'''

import os


def readNotImplemented(*args):
	raise NotImplementedError('read is not implemented')
def writeNotImplemented(*args):
	raise NotImplementedError('write is not implemented')

class BoundaryStream(object):
	'''BoundaryStream is a wrappper aroung read, write or a stream

It enables packetwise reading and writing.

'''
	
	BOUNDARY_BOUNDARY= b'\n\n'

	def __init__(self, read= None, write= None, stream= None):
		'''initialize the class with read, write or a stream

read must accept a number of bytes that shall be read.
read(int)

write must accept bytes.
All bytes shall be written an no bytes lost! important
write(b'...')

the stream has one of write or read as attributes
stream.read or stream.write
which have to fulfill the requirements
'''
		
		self.stream= stream
		if read is None:
			if stream is None:
				self._read= readNotImplemented
			else:
				self._read= stream.read
		else:
			self._read= read
		if write is None:
			if stream is None:
				self._write= writeNotImplemented
			else:
				self._write= stream.write
		else:
			self._write= write
		
			

	def read(self):
		'''read a packet from the stream

the return value is bytes'''
		BOUNDARY_BOUNDARY= self.BOUNDARY_BOUNDARY
		boundary= self.readBoundary(self._read, BOUNDARY_BOUNDARY)
		if not boundary:
			# short boundary mode
			boundary= BOUNDARY_BOUNDARY
##		print ('read boundary {0}'.format(boundary))
		return self.readBoundary(self._read, boundary)

	@staticmethod
	def readBoundary(read, boundary):
		'''internal, do not use

read bytes from read until boundary appears
'''
		# fix: can be optimized
		s= read(1)
		len_boundary= -len(boundary)
		while s[len_boundary:] != boundary:
			c= read(1)
			if not c:
				raise ValueError('read retuned empty string')
			s+= c
		return s[:len_boundary]

	def write(self, p):
		'''write these bytes as packet
'''
		BOUNDARY_BOUNDARY= self.BOUNDARY_BOUNDARY
		if BOUNDARY_BOUNDARY not in p:
			# send empty boundary for short boundary mode ending on BOUNDARY_BOUNDARY
			return self._write(BOUNDARY_BOUNDARY + p + BOUNDARY_BOUNDARY)
		rand= os.urandom
		BOUNDARY_BOUNDARY_0= BOUNDARY_BOUNDARY[0]
		boundary= rand(0)
		i= 0
		while i != -1:
			b= rand(2)
			while BOUNDARY_BOUNDARY_0 in b:
				b= rand(2)
			boundary+= b
			i= p.find(boundary, i)
##		print ('write boundary {0}'.format(boundary))
		return self._write(boundary + BOUNDARY_BOUNDARY + p + boundary)
			

if __name__ == '__main__':
	# test the coder
	import io
	s= io.BytesIO()
	b= BoundaryStream(stream= s)
	def test(x):
		i= s.tell()
		b.write(x)
		s.seek(i)
		y= b.read()
		assert x == y, '"{0}" != "{1}"'.format(x, y)

	test(b'')
	test(b'123567890')
	test(bytes(range(256)))
	for i in range(100):
		test(os.urandom(200 * i))
		
	
	


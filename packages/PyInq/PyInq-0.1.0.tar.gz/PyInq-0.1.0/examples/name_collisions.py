from pyinq.tags import *

@Test
def atest():
	print "main atest"

@TestClass
class Class1(object):
	@Test
	def atest():
		print "Class1 atest"
	
	@Test
	def btest():
		print "Class2 btest"

@Test
def btest():
	print "main test"

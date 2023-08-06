from pyinq.tags import *


@TestClass
class SuiteTest(object):
	@Test(suite="suite3")
	def atest():
		print "suite 3 test 1, in SuiteTest"
	
	@Test(suite="suite1")
	def btest():
		print "suite 1 test 1, in SuiteTest"

@TestClass
class SuiteTest2(object):
	@Test(suite="suite1")
	def ctest():
		print "suite 1 test 2 in SuiteTest2"

@Before
def before():
	print "before"

@After
def after():
	print "after"


@Test(suite="suite1")
def test1():
	print "suite 1 test 1"

@Test(suite="suite2")
def test2():
	print "suite 2 test 1"

@Test
def test4():
	print "no suite test 1"

@Test(suite="suite1")
def test3():
	print "suite 1 test 2"


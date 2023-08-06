from pyinq.tags import *
from pyinq.asserts import *

@TestClass
@Skip
class Test1(object):
	@BeforeClass
	def init():
		eval_true(False)

	@Test
	def test1():
		assert False
	
@Skip
@TestClass
class Test2:
	@BeforeClass
	def init():
		eval_true(False)
	
	@Test
	def test2():
		assert False

@Skip
@TestClass
class Test3(object):
	@Test(suite="suite1")
	def test5():
		assert_true(False)
	
	@Test(suite="suite1")
	def test3():
		assert_true(False)

@Skip
@TestClass
class Test4(object):
	@Test(suite="suite1")
	def test4():
		assert_true(False)

from pyinq.tags import *

@TestClass(suite="suite1")
class Class1(object):
	@Test
	def test1():
		assert True
	
	@Test
	def test2():
		assert True

@TestClass(suite="suite2")
class Class2(object):
	@Test(suite="suite1")
	def test3():
		assert True
	
	@Test(suite="suite2")
	def test4():
		assert True

@TestClass
class Class3(object):
	@Test
	def test5():
		assert True
	
	@Test
	def test6():
		assert True

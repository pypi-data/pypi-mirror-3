from pyinq.tags import *

@TestClass
class Class(object):
	@Skip
	@Test
	def test1():
		assert False
	
	@Test
	@Skip
	def test2():
		assert False
	
	@Test
	def test3():
		assert True
	
	@SkipIf(True)
	@Test
	def test4():
		assert False
	
	@Test
	@SkipIf(True)
	def test5():
		assert False
	
	@SkipIf(False)
	@Test
	def test6():
		assert True
	
	@Test
	@SkipIf(False)
	def test7():
		assert True
	
	@SkipUnless(True)
	@Test
	def test8():
		assert True
	
	@Test
	@SkipUnless(True)
	def test9():
		assert True
	
	@SkipUnless(False)
	@Test
	def test10():
		assert False
	
	@Test
	@SkipUnless(False)
	def test11():
		assert False

@Skip
@Test
def test1():
	assert False

@Test
@Skip
def test2():
	assert False

@Test
def test3():
	assert True

@SkipIf(True)
@Test
def test4():
	assert False

@Test
@SkipIf(True)
def test5():
	assert False

@SkipIf(False)
@Test
def test6():
	assert True

@Test
@SkipIf(False)
def test7():
	assert True

@SkipUnless(True)
@Test
def test8():
	assert True

@Test
@SkipUnless(True)
def test9():
	assert True

@SkipUnless(False)
@Test
def test10():
	assert False

@Test
@SkipUnless(False)
def test11():
	assert False


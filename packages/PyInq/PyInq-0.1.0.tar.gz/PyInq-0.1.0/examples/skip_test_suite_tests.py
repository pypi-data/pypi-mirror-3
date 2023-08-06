from pyinq.tags import *
from pyinq.asserts import *


@TestClass(suite="suite2")
class Class1:
	@Test
	def test3():
		assert_true(True)

	@Skip
	@Test(suite="suite1")
	def test():
		assert_true(False)
	
	@Test(suite="suite3")
	@Skip
	def test2():
		assert_true(False)

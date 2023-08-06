from pyinq.asserts import *
from pyinq.tags import *

@TestClass
class Class1:
	def __init__(self):
		self.num = 4

	@Test
	def test1():
		assert_equal(this.num,4)
		this.num += 1
	
	@Test
	def test2():
		assert_equal(this.num,4)
		this.num += 1

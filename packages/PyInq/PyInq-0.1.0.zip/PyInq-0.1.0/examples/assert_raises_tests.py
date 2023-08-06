from pyinq.tags import *
from pyinq.asserts import *

@Test
def test():
	assert_raises(ValueError,parse,"hjhwr")
	eval_true(True)

@Test
def test2():
	assert_raises(WindowsError,parse,"hjhwr")
	eval_true(True)

@Test
def test3():
	assert_raises(ValueError,parse,"4")
	eval_true(True)

@Test
def test4():
	eval_raises(ValueError,parse,"hjhwr")
	eval_true(True)

@Test
def test5():
	eval_raises(WindowsError,parse,"hjhwr")
	eval_true(True)

@Test
def test6():
	eval_raises(ValueError,parse,"9")
	eval_true(True)

def parse(val):
	int(val)

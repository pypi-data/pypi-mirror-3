from pyinq.tags import *
from pyinq.asserts import *
import mod

@Test(expected=ValueError)
def test():
	mod.parse("hjhwr")

@Test(expected=WindowsError)
def test2():
	mod.parse("hjhwr")

@Test(expected=ValueError)
def test3():
	parse("4")

def parse(val):
	int(val)

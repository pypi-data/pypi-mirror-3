from pyinq.tags import *
from pyinq.asserts import *

@BeforeSuite
@Skip
def setup7():
	eval_true(False)

@Skip
@BeforeSuite
def setup8():
	eval_true(False)

@BeforeModule
@Skip
def setup5():
	eval_true(False)

@Skip
@BeforeModule
def setup6():
	eval_true(False)

@BeforeClass
@Skip
def setup3():
	eval_true(False)

@Skip
@BeforeClass
def setup4():
	eval_true(False)

@Before
@Skip
def setup1():
	eval_true(False)

@Skip
@Before
def setup2():
	eval_true(False)

@Test
def test1():
	assert True

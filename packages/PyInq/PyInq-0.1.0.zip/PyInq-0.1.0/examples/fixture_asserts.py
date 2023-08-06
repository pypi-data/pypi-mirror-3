from pyinq.tags import *
from pyinq.asserts import *

@BeforeClass
def setupClass():
	assert_true(False)

@Before
def setup():
	assert_true(False)

@Test
def test():
	print "TEST"
	assert_true(False)

@After
def teardown():
	assert_true("AFTER")

@AfterClass
def teardownClass():
	assert_true(True)

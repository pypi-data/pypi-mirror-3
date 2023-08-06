from pyinq.tags import *

@BeforeModule
def setupModule():
	print "set up module"

@AfterModule
def teardownModule():
	print "tear down module"

@BeforeSuite
def setupGlobalSuite():
	print "setting up global suite"

@BeforeSuite(suite="suite1")
def setupSuite1():
	print "setup suite 1"

@AfterSuite(suite="suite1")
def teardownSuite1():
	print "tear down suite 1"

@TestClass
class Class1:
	@BeforeClass
	def setup():
		print "setup Class1" 
	
	@BeforeSuite(suite="suite4")
	def setupSuite4():
		print "setup suite 4"

	@Test(suite="suite1")
	def test1():
		print "test1 in Class1"
	
	@Test(suite="suite2")
	def test2():
		print "test2 in Class1"
	
	@Test(suite="suite3")
	def test3():
		print "test3 in Class1"
	
	@Test
	def test4():
		print "test4 in Class1"
	
	@Test(suite="suite4")
	def suite_fixture_test1():
		print "test1 in suite4"

	@AfterClass
	def teardown():
		print "teardown Class1"

@TestClass
class Class2:
	@Before
	def setup():
		print "setup test in Class2" 

	@Test(suite="suite1")
	def test5():
		print "test5 in Class2"
	
	@Test(suite="suite2")
	def test6():
		print "test6 in Class2"
	
	@Test(suite="suite3")
	def test7():
		print "test7 in Class2"

	@Test
	def test8():
		print "test8 in Class2"

	@Test(suite="suite4")
	def suite_fixture_test2():
		print "test2 in suite4"

	@After
	def teardown():
		print "teardown test in Class2"

@AfterSuite(suite="suite2")
def teardownSuite2():
	print "tear down suite 2"

@AfterSuite
def teardownGlobalSuite():
	print "tearing down global suite"

from code.hello_es import *

class Test_Hello_ES:
	
	def setUp(self):
		self.Hello_Es_Object = Model()
		
	def test_canary(self):
		assert 1 == 1
	
	def test_object_created(self):
		assert self.Hello_Es_Object.__class__.__name__ == 'Model'
	
	def test_get_message(self):
		self.Hello_Es_Object.get_message()
		assert self.Hello_Es_Object.get_message() == False
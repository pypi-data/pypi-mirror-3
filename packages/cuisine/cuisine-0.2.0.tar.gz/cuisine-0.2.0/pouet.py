call = 0
def d(prefix):
	print prefix
	def wrapper(function):
		def wrapper_(*args,**kwargs):
			global call
			print function, "CALL", call
			call += 1
			return function(*args, **kwargs)
		return wrapper_
	return wrapper

def e(f):
	def wrapper(*args,**kwargs):
		global call
		print call
		call += 1
		return f(*args, **kwargs)
	return wrapper
@e
def pouet():
	print "Hello"

pouet()
pouet()
pouet()

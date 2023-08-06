# Binary to decimal converter
# It can take up to 10 binary numbers

class Converter(object):
	def __init__(self, number):
		self.number = number
	
	def convert(self):
		self.number = raw_input("> ")
		while True:
			x = Converter(self.number)
			if	len(self.number) == 1:
				number_string = str(self.number)
				convert = "%d * 2**0" % (int(number_string[0]))
				print eval(convert)
				return x.convert()
			elif len(self.number) == 2:
				number_string = str(self.number)
				convert = "%d * 2**1 + %d * 2**0" % (int(number_string[0]), int(number_string[1]))
				print eval(convert)
				return x.convert()
			elif len(self.number) == 3:
				number_string = str(self.number)
				convert = "%d * 2**2 + %d * 2**1 + %d * 2**0" % (int(number_string[0]), int(number_string[1]), int(number_string[2]))
				print eval(convert)
				return x.convert()
			elif len(self.number) == 4:
				number_string = str(self.number)
				convert = "%d * 2**3 + %d * 2**2 + %d * 2**1 + %d * 2**0" % (int(number_string[0]), int(number_string[1]), int(number_string[2]), int(number_string[3]))
				print eval(convert)
				return x.convert()
			elif len(self.number) == 5:
				number_string = str(self.number)
				convert = "%d * 2**4 + %d * 2**3 + %d * 2**2 + %d * 2**1 + %d * 2**0" % (int(number_string[0]), int(number_string[1]), int(number_string[2]), 
				int(number_string[3]),int(number_string[4]))
				print eval(convert)
				return x.convert()
			elif len(self.number) == 6:
				number_string = str(self.number)
				convert = "%d * 2**5 + %d * 2**4 + %d * 2**3 + %d * 2**2 + %d * 2**1 + %d * 2**0" % (int(number_string[0]), int(number_string[1]), int(number_string[2]), 
				int(number_string[3]),int(number_string[4]),int(number_string[5]))
				print eval(convert)
				return x.convert()
			elif len(self.number) == 7:
				number_string = str(self.number)
				convert = "%d * 2**6 + %d * 2**5 + %d * 2**4 + %d * 2**3 + %d * 2**2 + %d * 2**1 + %d * 2**0" % (int(number_string[0]), int(number_string[1]), int(number_string[2]), 
				int(number_string[3]),int(number_string[4]),int(number_string[5]),int(number_string[6]))
				print eval(convert)
				return x.convert()
			elif len(self.number) == 8:
				number_string = str(self.number)
				convert = "%d * 2**7 + %d * 2**6 + %d * 2**5 + %d * 2**4 + %d * 2**3 + %d * 2**2 + %d * 2**1 + %d * 2**0" % (int(number_string[0]), int(number_string[1]), int(number_string[2]), 
				int(number_string[3]),int(number_string[4]),int(number_string[5]),int(number_string[6]),int(number_string[7]))
				print eval(convert)
				return x.convert()
			elif len(self.number) == 9:
				number_string = str(self.number)
				convert = "%d * 2**8 + %d * 2**7 + %d * 2**6 + %d * 2**5 + %d * 2**4 + %d * 2**3 + %d * 2**2 + %d * 2**1 + %d * 2**0" % (int(number_string[0]), int(number_string[1]), int(number_string[2]), 
				int(number_string[3]),int(number_string[4]),int(number_string[5]),int(number_string[6]),int(number_string[7]),int(number_string[8]))
				print eval(convert)
				return x.convert()
			elif len(self.number) == 10:
				number_string = str(self.number)
				convert = "%d * 2**9 + %d * 2**8 + %d * 2**7 + %d * 2**6 + %d * 2**5 + %d * 2**4 + %d * 2**3 + %d * 2**2 + %d * 2**1 + %d * 2**0" % (int(number_string[0]), int(number_string[1]), int(number_string[2]), 
				int(number_string[3]),int(number_string[4]),int(number_string[5]),int(number_string[6]),int(number_string[7]),int(number_string[8]),int(number_string[9]))
				print eval(convert)
				return x.convert()
			

	

	
	
	
	
print "Welcome to the binary to decimal converter."
print "Enter a binary number up to 10 digits."
print "(Ctrl + Z to quit)"
print "note: Binary system consists only of 0 and 1, don't type anything beyond or it's going to calculate a random number."
null = 0

x = Converter(null)
x.convert()
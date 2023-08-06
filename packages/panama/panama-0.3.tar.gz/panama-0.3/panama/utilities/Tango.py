class Tango(object):
    def __init__(self):
	self.Aluminium6="#2e3436"
	self.Aluminium5="#555753"
	self.Aluminium4="#888a85"
	self.Aluminium3="#babdb6"
	self.Aluminium2="#d3d7cf"
	self.Aluminium1="#eeeeec"

	self.lightPurple="#ad7fa8"
	self.mediumPurple="#75507b"
	self.darkPurple="#5c3566"

	self.lightBlue="#729fcf"
	self.mediumBlue="#3465a4"
	self.darkBlue= "#204a87"

	self.lightGreen="#8ae234"
	self.mediumGreen="#73d216"
	self.darkGreen="#4e9a06"

	self.lightChocolate="#e9b96e"
	self.mediumChocolate="#c17d11"
	self.darkChocolate="#8f5902"

	self.lightRed="#ef2929"
	self.mediumRed="#cc0000"
	self.darkRed="#a40000"

	self.lightOrange="#fcaf3e"
	self.mediumOrange="#f57900"
	self.darkOrange="#ce5c00"

	self.lightButter="#fce94f"
	self.mediumButter="#edd400"
	self.darkButter="#c4a000"

	# self.darkList = [self.darkBlue, self.darkRed, self.darkGreen, self.darkOrange,
	# 		 self.darkButter, self.darkPurple, self.darkChocolate, self.Aluminium6]
	self.darkList = [self.darkBlue, self.darkRed, self.darkGreen, self.darkOrange,
			 self.Aluminium5, self.darkPurple, self.darkChocolate, self.Aluminium6]
	self.mediumList = [self.mediumBlue, self.mediumRed, self.mediumGreen, self.mediumOrange,
			   self.mediumButter, self.mediumPurple, self.mediumChocolate, self.Aluminium5]
	self.lightList = [self.lightBlue, self.lightRed, self.lightGreen, self.lightOrange, self.lightButter,
			  self.lightPurple, self.lightChocolate, self.Aluminium4]


    def nextDark(self):
	self.darkList.append(self.darkList.pop(0))
	return self.darkList[-1]
    def nextMedium(self):
	self.mediumList.append(self.mediumList.pop(0))
	return self.mediumList[-1]
    def nextLight(self):
	self.lightList.append(self.lightList.pop(0))
	return self.lightList[-1]

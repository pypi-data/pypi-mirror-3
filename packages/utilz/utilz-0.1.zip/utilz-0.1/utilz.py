"""My first Program to print a whle list"""

def printlist (lname):
	for each in lname:
		if isinstance(each,list):
			printlist(each)
		else:
			print(each)

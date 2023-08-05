"""My first Program to print a whle list"""

def printlist (lname,level):
	for each in lname:
		if isinstance(each,list):
			printlist(each)
		else:
                        for tabstop in range(level):
                                print("\t",end="")
			print(each)

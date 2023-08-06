def printlol(listname):
	for everyitem in listname:
		if isinstance(everyitem,list):
			printlol(everyitem)
		else:
			print(everyitem)

			


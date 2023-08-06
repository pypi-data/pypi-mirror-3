def printlistindent(list1,times=0,yes=0):
	for eachitem in list1:
		if isinstance(eachitem,list):
			if(yes == 1):
				printlistindent(eachitem,times+1,yes)
			else:
				printlistindent(eachitem,times,yes)
		else:
			for tab_stop in range(times):
				print("\t", end='')
			print(eachitem)

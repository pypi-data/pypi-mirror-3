def printlisttimes(list1,times):
	for eachitem in list1:
		if isinstance(eachitem,list):
			printlisttimes(eachitem,times+1)
		else:
		     for tab_stop in range(times):
			     print(eachitem)

def printlisttimes(list1,times=0):
	for eachitem in list1:
		if isinstance(eachitem,list):
			printlisttimes(eachitem,times+1)
		else:
		     for tab_stop in range(times):
			     print(eachitem)

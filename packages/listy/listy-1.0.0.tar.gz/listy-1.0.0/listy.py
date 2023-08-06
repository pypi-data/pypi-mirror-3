def print_list(crap):
	for each_item in crap:
		if isinstance(each_item,list):
			print_list(each_item)
		else:
			print(each_item)

def my_print(the_list):
	for each_film in the_list:
		if isinstance(each_film, list):
			my_print(each_film)
		else:
			print(each_film)




# hihimann.py
"""This is the nester.py" module and it provides one function called print_lol()
   which prints lists that may or may not include nested lists."""
   
def print_lol(the_list, level):
	"""This function takes the_list, which is any python list (of nested lists).
	   Each item is printed on the screen on its own line. A second argument called
	   level is used to insert tab-stops when a nested list is encountered."""
	for each_item in the_list:
		if isinstance( each_item, list ):
			print_lol( each_item, level+1 )
		else:
			for tab_stop in range( level ):
				print("\t", end='')
			print( each_item )

			
movies = [ "The Holy Grail", 1975, "Terry Jones & Terry Gilliam", 91,
["Graham Chapman",
["Michael Palin", "John Cleese", "Terry Gilliam", "Eric Idle", "Terry Jones"]]]

print_lol( movies, 0 )

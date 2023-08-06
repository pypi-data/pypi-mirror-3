movies = ["The Holy Grail", 1975, "Terry Jones & Terry Gilliam", 91, ["Graham Chapman", [
'Michael Palin', 'John Cleese', 'Terry Gilliam', 'Eric Idle', 'Terry Jones']]]

"""This is the "loop.py" module, and it provide on function called print_lol() which
prints lists that may or may not include nested lists.
A second argument called "level" is used to insert tab-stops when a nested
		list is encountered"""
def print_lol(the_list, indent=false, level=0):
	for each_item in the_list:
		"""This function take positional argument called "the_list", which is any
		Python list (of, possibly, nested lists). Each data item in the provided list
		is (recursively) printed to the screen on its own line."""
		if isinstance(each_item, list):
			print_lol(each_item, indent, level+1)
		else:
			if indent:
				for tab_stop in range(level):
					print("\t", end='')
			print(each_item)

print_lol(movies)


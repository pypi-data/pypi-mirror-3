""" 주석달기"""
"""주석달기 2
    ""..석 달기 3""
	"""
# 주석달기4
def print_lol(the_list):
	for a in the_list:
		if isinstance(a,list):
			print_lol(a)
		else:
			print(a)
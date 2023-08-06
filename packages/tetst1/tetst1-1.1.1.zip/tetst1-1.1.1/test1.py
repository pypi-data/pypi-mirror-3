""" 주석달기"""
"""주석달기 2
    ""..석 달기 3""
	"""
# 주석달기4
def print_lol(the_list, level):
	for a in the_list:
		if isinstance(a,list):
			print_lol(a,level+1)
		else:
			for tabs in range(level):
				print("\t",end='')
			print(a)

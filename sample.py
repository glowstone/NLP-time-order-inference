



tree = [[1,2,[3]], [4]]

def multi_access(tree, indicies):
	if len(indicies) > 0:
		print "here"
		return multi_access(tree[indicies[0]], indicies[1:])
	else:
		return tree


print multi_access(tree, [0,2])

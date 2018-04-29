import glob
arr = glob.glob("*.txt")
total = 0
num = 0
for ele in arr:
	with open(ele, 'r') as file:
		new_arr = file.readlines()
		size = 0
		for line in new_arr:
			size += len(line.split())
		print(size)
		total += size
		num += 1

print((total + 0.0)/num)
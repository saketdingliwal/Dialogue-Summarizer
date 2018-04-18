import json
import re

corpus = json.load(open('blog_data.json'))

lstno = []
conv = []

def getspe(word):
	term = re.findall("\w*:", word)
	return term[0][:-1]

def getname(sent):
	new_sent = []
	for word in sent.split():
		arr = re.findall("\w*:\w*", word)
		if(len(arr)==1):
			new_sent.append(getspe(word))
			new_sent.append("said")
			new_sent.append("that")
		else:
			new_sent.append(word)
	return " ".join(new_sent)

def getsummary(sent):
	words = sent.split()
	ans = []
	for word in words[3:]:
		if(word=="----------"):
			break
		if(word=="\\n"):
			continue
		if(word=="\\r"):
			continue
		ans.append(word)
	return " ".join(ans)

ite = 0
for ele in corpus:
	full_sent = getname(ele["Dialog"])
	summ_sent = getsummary(ele["Summary"])
	for sent in summ_sent.split('.'):
		if(len(sent.split())==0):
			continue
		full_sent += "\n@highlight\n" + " ".join(sent.split()) + '.'
	conv.append(full_sent)

for i, ele in enumerate(conv):
	print(len(ele.split()))
	filename = "folder/" + str(i) + ".story"
	with open(filename, 'w') as writer:
		print(ele)
		writer.write(ele)
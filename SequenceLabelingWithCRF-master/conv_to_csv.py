import sys
import csv
import nltk
import pickle

def pos_tagged(sent):
	tags = nltk.pos_tag(sent.split())
	ans = ""
	for ele in tags:
		ans += ele[0]
		ans += "/"
		ans += ele[1]
		ans += " "
	return " ".join(ans.split())

def cln_word(word):
	if '/' in word:
		return []
	if '\'' in word:
		if word.lower() in contractions:
			return contractions[word.lower()].split()
	punc = [',', '.', '?', ';', '!']
	if(word[-1] in punc):
		return [word[:-1], word[-1]]
	else:
		return [word]

with open('cont.pickle', 'rb') as handle:
    contractions = pickle.load(handle)

data = []

with open(sys.argv[1], 'r') as file:
	abc = csv.DictReader(file, delimiter=":")
	for row in abc:
		new_sent = []
		for ele in row['pos'].split():
			new_sent.extend(cln_word(ele))
		data.append((row['speaker'], " ".join(new_sent)))

with open(sys.argv[2], 'w', newline='') as file:
	fieldnames = ['speaker', 'pos']
	writer = csv.DictWriter(file, fieldnames=fieldnames)
	writer.writeheader()
	for ele in data:
		writer.writerow({'speaker': ele[0], 'pos': pos_tagged(ele[1])})
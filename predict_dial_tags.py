import sys
from collections import namedtuple
import csv
import glob
import os
import pycrfsuite
import pickle


specialCharacter = "!@#$%^*()_+~}{|:><?;-+"

def get_utterances_from_file(dialog_csv_file, dialog_csv_filename):
    """Returns a list of DialogUtterances from an open file."""
    reader = csv.DictReader(dialog_csv_file)
    path = dialog_csv_filename.split("\\")
    return [_dict_to_dialog_utterance(du_dict, path[-1]) for du_dict in reader]

def get_utterances_from_filename(dialog_csv_filename):
    """Returns a list of DialogUtterances from an unopened filename."""
    with open(dialog_csv_filename, "r") as dialog_csv_file:
        return get_utterances_from_file(dialog_csv_file, dialog_csv_filename)

def get_data(data_dir):
    """Generates lists of utterances from each dialog file.

    To get a list of all dialogs call list(get_data(data_dir)).
    data_dir - a dir with csv files containing dialogs"""
    dialog_filenames = (glob.glob(os.path.join(data_dir, "*.csv")))
    new_dialog_filenames = []
    for i in range(len(dialog_filenames)):
    	new_dialog_filenames.append(os.path.join(data_dir, str(i)+".csv"))

    for dialog_filename in new_dialog_filenames:
        yield get_utterances_from_filename(dialog_filename)

DialogUtterance = namedtuple("DialogUtterance", ("act_tag", "speaker", "pos", "text" ,"fileName"))

PosTag = namedtuple("PosTag", ("token", "pos"))

def _dict_to_dialog_utterance(du_dict, dialog_csv_filename):
    """Private method for converting a dict to a DialogUtterance."""

    # Remove anything with
    for k, v in du_dict.items():
        if len(v.strip()) == 0:
            du_dict[k] = None
    du_dict["act_tag"] = None
    du_dict["text"] = None
    # Extract tokens and POS tags
    if du_dict["pos"]:
        du_dict["pos"] = [
            PosTag(*token_pos_pair.split("/"))
            for token_pos_pair in du_dict["pos"].split()]
    du_dict["fileName"] = dialog_csv_filename
    return DialogUtterance(**du_dict)

def createFeatureList(files):
    xTrain = []
    fileNames = []
    for utterances in files:
        file = []
        first = True
        speaker = ''
        previous_label = ''
        for dialogUtterance in utterances:
            fileName = dialogUtterance.fileName
            feature = []
            if first:
                feature.append('1')
                feature.append('0')
                speaker = dialogUtterance.speaker
                first = False
            else:
                feature.append('0')
                if dialogUtterance.speaker == speaker:
                    feature.append('0')
                else:
                    feature.append('1')
                    speaker = dialogUtterance.speaker
            specialCharcterFlag = '0'
            if dialogUtterance.pos:
                for posTag in dialogUtterance.pos:
                    feature.append("TOKEN_"+posTag.token)
                    feature.append(posTag.token)
                    if posTag.token in specialCharacter:
                        specialCharcterFlag = '1'
                for posTag in dialogUtterance.pos:
                    feature.append("POS_"+posTag.pos)
            file.append(feature)
        xTrain.append(file)
        fileNames.append(fileName)
    return xTrain,fileNames



# print ('Argument count : ', len(sys.argv))
#exit if file name is not provided as command line argument
if len(sys.argv) != 3:
    print ('Please send file name as command line argument')
    exit(0)

testDir = sys.argv[1]
outputDir = sys.argv[2]


# get all utterances
files_test = get_data(testDir)
xTest, filenames_test = createFeatureList(files_test)

tagger = pycrfsuite.Tagger()
tagger.open('baseline_model_new.crfsuite')

yPred = [tagger.tag(xseq) for xseq in xTest]


ignore_tags = ["b","%","fo_o_fw_by_bc","x","fc","bk","h","qy^d","bh","ad","^2","b^m","qo","qh","^h","ar","ng","br","no","fp","qrr","arp_nd","t3","o_co_cc","t1","bd","aap_am","^g","qw^d","fa","ft"]
answer_tags = ["ny","nn","na"]
question_tags = ["qy"]

replaced_by = {}
replaced_by["aa"] = "agreed ."
replaced_by["ba"] = "appreciated ."

i_list = ["i","me"]
i_list_poss = ["my"]
you_list = ["you"]
you_list_poss = ["your"]



opp_speaker = {}
opp_speaker["S1"] = "S2"
opp_speaker["S2"] = "S1"

def frame_ans(question_utter,dialogUtterance):
	article = question_utter.speaker +  " asked"
	if question_utter.pos:
		for posTag in question_utter.pos:
			article += (" " + posTag.token)
	if dialogUtterance.act_tag == "ny" or dialogUtterance.act_tag == "na":
		article += (" "+dialogUtterance.speaker + " agreed .")
	else:
		article += (" "+dialogUtterance.speaker + " disagreed .")
	return article	



files_test = get_data(testDir)
article_list = []
for iterr_i,utterances in enumerate(files_test):
	article = []
	lastspeaker = "X"
	question_utter = None
	for iterr_j,dialogUtterance in enumerate(utterances):
		if yPred[iterr_i][iterr_j] in ignore_tags:
			continue
		if yPred[iterr_i][iterr_j] in replaced_by:
			article.append(dialogUtterance.speaker)
			article.append(replaced_by[yPred[iterr_i][iterr_j]])
			continue
		if yPred[iterr_i][iterr_j] in question_tags:
			question_save = dialogUtterance
			continue
		if yPred[iterr_i][iterr_j] in answer_tags:
			if question_save == None:
				continue
			if not question_save.speaker == dialogUtterance.speaker:
				ans_string = frame_ans(question_save,dialogUtterance)
				article.append(ans_string)
				question_save = None
				continue
		if dialogUtterance.pos:
			for i in range(len(dialogUtterance.pos)):
				posTag = dialogUtterance.pos[i]
				next_pos = None
				new_token = posTag.token
				if not i==0 and ( dialogUtterance.pos[i-1].token.lower() == new_token.lower()) :
					continue
				# if not i == (len(dialogUtterance.pos)-1):
				# 	next_pos = dialogUtterance.pos[i+1]
				# if next_pos and "\'" in next_pos.token:
				# 	word = posTag.token
				# 	word += next_pos.token
				# 	if word.lower() in contractions:
				# 		word = contractions[word.lower()]
				# 		new_token = word
				# 	else:
				# 		word = posTag.token 
				# 		new_token = word
				if posTag.pos=="UH":
					continue
				if new_token.lower() in i_list:
					new_token = dialogUtterance.speaker
				if new_token.lower() in i_list_poss:
					new_token = dialogUtterance.speaker + "'s "
				if new_token.lower() in you_list:
					new_token = opp_speaker[dialogUtterance.speaker]
				if new_token.lower() in you_list_poss:
					new_token = opp_speaker[dialogUtterance.speaker] + "'s "
				article.append(new_token)
		lastspeaker = dialogUtterance.speaker
	article = " ".join(article)
	article_list.append(article)



for i, ele in enumerate(article_list):
	# print(len(ele.split()))
	filename = testDir + str(i) + ".story"
	with open(filename, 'r') as reader:
		data = reader.read()
	filename = outputDir + str(i) + ".story"
	with open(filename, 'w') as writer:
		writer.write(ele)
		writer.write(data)


# print(article_list[0])
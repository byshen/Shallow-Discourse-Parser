import codecs
import json

def read_data(file_name):
	data = []
	with codecs.open(file_name, 'r', encoding = 'utf-8') as f:
		for line in f:
			obj = json.loads(line)
			if obj['Type'] == 'Implicit':
				data.append(obj)

	return data


def wp_mi_clean():
	wpmi = open('word_pairs_mi')
	res = []
	for index, line in enumerate(wpmi):
		tmp = line.strip().split(' ')
		res.append(tmp[0])
	resfile = open('word_pairs_mi.txt', 'w')
	resfile.write('\n'.join(res))
	resfile.close()

def write_first_last_pair():
	relations = read_data('train_pdtb.json')
	punctuation = ['.', ',', '!', '"', '#', '&', '\'', '*', '+', '-', '...', '/', ':', ';', '<', '=', '>', '?', '@', '[', '\\',\
		']', '^', '_', '`', '|', '~', '$', '%', '--', '``', '\'\'']

	dict = {}
	fl_list = []
	for relation in relations:
		if len(relation['Arg1']['Lemma']) >= 3:
			fl_list.append('arg13_' + '_'.join(relation['Arg1']['Lemma'][:3]) )
		if len(relation['Arg2']['Lemma']) >= 3:
			fl_list.append('arg23_' + '_'.join(relation['Arg2']['Lemma'][:3]) )
		fl_list.append('arg11_' + relation['Arg1']['Lemma'][0])
		fl_list.append('arg21_' + relation['Arg2']['Lemma'][0])
		fl_list.append('arg121_' + relation['Arg1']['Lemma'][0] + '_' + relation['Arg2']['Lemma'][0])
		fl_list.append('arg12_' + relation['Arg1']['Lemma'][-1])
		fl_list.append('arg22_' + relation['Arg2']['Lemma'][-1])
		fl_list.append('arg122_' + relation['Arg1']['Lemma'][-1] + '_' + relation['Arg2']['Lemma'][-1])
		
		for flist in fl_list:
			if flist in dict:
				dict[flist] += 1
			else:
				dict[flist] = 1

	wp_file = codecs.open('first_last.txt', 'w', encoding='utf-8')
	
	write_data = [ wp[0] for wp in sorted(dict.items(), key=lambda v:v[1], reverse = True) if wp[1]>19] #key is value of dict_word_pairs]

	wp_file.write(u'\n'.join(write_data))

	wp_file.close()


write_first_last_pair()
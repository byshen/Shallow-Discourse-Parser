# -*- coding: utf-8 -*- 
import config
import json, codecs, pickle, os, time
from nltk.tree import Tree

SENSES = [' ', 'Expansion.List', 'Expansion.Conjunction',
	'Expansion.Instantiation',
	'Contingency.Cause',
	'Temporal.Asynchronous',
	'Comparison.Contrast',
	'Expansion.Restatement',
	'Temporal.Synchrony',
	'Contingency.Pragmatic cause',
	'Comparison.Concession',
	'Expansion.Alternative']

def map_sense_to_number(sense):
	if sense in SENSES:
		return SENSES.index(sense)
	else:
		return -1

def map_number_to_sense(num):
	if num >= len(SENSES):
		return 'Error'
	else:
		return SENSES[num]

"""
Read json file and return the corresponding json object for further process

	:type file_name : string
	:rtype data : list of dict, each element is a json object(in the format of dict)
"""
def read_data(file_name):
	data = []
	with codecs.open(file_name, 'r', encoding = 'utf-8') as f:
		for line in f:
			obj = json.loads(line)
			if obj['Type'] == 'Implicit':
				data.append(obj)

	return data

def load_dict_word_pairs(file_name, length=-1):
	dict_word_pairs = {}
	word_pairs_file = open(file_name)

	for lineno, line in enumerate(word_pairs_file):
		if line == '':
			continue
		if lineno == length:
			break
		dict_word_pairs[line[:-1]] = lineno

	return dict_word_pairs


def write_word_pairs_to_file():
	file_name = config.TRAINSET_PATH
	dict_word_pairs = get_word_pair_from_file_with_count(file_name)
	
	wp_file = codecs.open(config.WORD_PAIRS, 'w', encoding='utf-8')
	
	write_data = [ wp[0] for wp in sorted(dict_word_pairs.items(), key=lambda v:v[1], reverse = True) ] #key is value of dict_word_pairs]

	wp_file.write(u'\n'.join(write_data))

	wp_file.close()


def store_model(model, fname):
	pickle.dump(model, open(fname, 'wb'), -1)#with highest protocol

def get_production_rule_by_parse_tree(parsetree):
	syntax_tree = Tree.fromstring(parsetree)
	convert_str_format = lambda string, strip_char='\'': ''.join( [ ch for ch in '->'.join( [ st.strip() for st in string.split('->')] ) if ch not in strip_char ] )
	production_rule = [ convert_str_format(str(pr)) for pr in syntax_tree.productions() ]
	
	return production_rule

def get_production_rule_from_file_with_count():
	arg1_parsetree_file = codecs.open('dict/arg1_parsetree.txt')
	arg2_parsetree_file = codecs.open('dict/arg2_parsetree.txt')
	#parsetree_file = codecs.open(config.PARSETREE_DICT, 'w')

	arg1_parsetree = arg1_parsetree_file.read().split('\n')
	arg2_parsetree = arg2_parsetree_file.read().split('\n')

	arg1_production_rule_dict = {}
	arg2_production_rule_dict = {}
	both_production_rule_dict = {}
	for index in range(len(arg1_parsetree)):
		arg1_prule = get_production_rule_by_parse_tree(arg1_parsetree[index])[1:]
		arg2_prule = get_production_rule_by_parse_tree(arg2_parsetree[index])[1:]
		both_prule = list(set(arg1_prule) & set(arg2_prule))
		"""print arg1_prule
								print arg2_prule
								print both_prule"""

		for prule in arg1_prule:
			if prule in arg1_production_rule_dict:
				arg1_production_rule_dict[prule] += 1
			else:
				arg1_production_rule_dict[prule] = 1
		for prule in arg2_prule:
			if prule in arg2_production_rule_dict:
				arg2_production_rule_dict[prule] += 1
			else:
				arg2_production_rule_dict[prule] = 1

		for prule in both_prule:
			if prule in both_production_rule_dict:
				both_production_rule_dict[prule] += 1
			else:
				both_production_rule_dict[prule] = 1

	arg1_production_rule = [ 'Arg1_' + pr[0] for pr in sorted(arg1_production_rule_dict.items(), key = lambda it:it[1], reverse = True) ]
	arg2_production_rule = [ 'Arg2_' + pr[0] for pr in sorted(arg2_production_rule_dict.items(), key = lambda it:it[1], reverse = True) ]
	both_production_rule = [ 'Both_' + pr[0] for pr in sorted(both_production_rule_dict.items(), key = lambda it:it[1], reverse = True)]

	#TODO merge all produciton rules
	#production_rule_dict = arg1_production_rule_dict + arg2_production_rule_dict + both_production_rule_dict
	#prodcution_rule = 

	arg1_production_rule_file = open('dict/arg1_production_rules.txt', 'w')
	arg2_production_rule_file = open('dict/arg2_production_rules.txt', 'w')
	both_production_rule_file = open('dict/both_production_rules.txt', 'w')
	#production_rule_file = open('dict/production_rules.txt', 'w')
	arg1_production_rule_file.write('\n'.join(arg1_production_rule))
	arg2_production_rule_file.write('\n'.join(arg2_production_rule))
	both_production_rule_file.write('\n'.join(both_production_rule))

	#production_rule_file.close()
	arg2_production_rule_file.close()
	arg1_production_rule_file.close()
	arg1_parsetree_file.close()
	arg2_parsetree_file.close()
	#parsetree_file.close()



def get_productions():
	arg1_parsetree_file = codecs.open('dict/arg1_parsetree.txt')
	arg1_parsetree = arg1_parsetree_file.read().split('\n')
	convert_str_format = lambda string, strip_char='\'': \
		''.join( [ ch \
			for ch in '->'.join( [ st.strip() \
				for st in string.split('->')] ) \
					if ch not in strip_char ] )

	syntax_tree = Tree.fromstring(arg1_parsetree[0])
	for pr in syntax_tree.productions():
		print convert_str_format(str(pr))

def load_dependency_rule_dict(file_name, length = -1):
	dependency_rule_dict = {}
	with codecs.open(file_name, 'r', encoding = 'utf-8') as file:
		for lineno, line in enumerate(file):
			if lineno == length:
				break
			else:
				dependency_rule_dict[line[:-1]] = lineno
	
	return dependency_rule_dict

def load_first_last_dict(file_name, length = -1):
	first_last_dict = {}
	with codecs.open(file_name, 'r', encoding = 'utf-8') as file:
		for lineno, line in enumerate(file):
			if lineno == length:
				break
			else:
				first_last_dict[line[:-1]] = lineno
	return first_last_dict

def load_prule(file_name, length = -1):
	dict_production_rules = {}
	with codecs.open(file_name, 'r', encoding = 'utf-8') as file:
		for lineno, line in enumerate(file):
			if lineno == length:
				break
			else:
				dict_production_rules[line[:-2]] = lineno
	
	return dict_production_rules


def write_parse_tree_to_file(file_name):
	all_relations = read_data(file_name)
	dict = {}
	arg1_sent = []
	arg2_sent = []
	arg1_sent_file_path = 'tmp/arg1_sentence.txt'
	arg2_sent_file_path = 'tmp/arg2_sentence.txt'
	#arg1_prule_file = 'tmp/arg1_production_rule.txt'
	#arg2_prule_file = 'tmp/arg2_production_rule.txt'
	#both_prule_file = 'tmp/both_'
	for relation in all_relations:
		arg1_sent.append( ' '.join(relation['Arg1']['Lemma']) )
		arg2_sent.append( ' '.join(relation['Arg2']['Lemma']) )

	with codecs.open(arg1_sent_file_path, 'w', encoding = 'utf-8') as file:
		file.write( u'\n'.join(arg1_sent) )

	with codecs.open(arg2_sent_file_path, 'w', encoding = 'utf-8') as file:
		file.write( u'\n'.join(arg2_sent) )

	start = time.time()
	os.system( 'java -jar lib/BerkeleyParser-1.7.jar -gr lib/eng_sm6.gr -inputFile %s -outputFile tmp/arg1_parsetree.txt' 
		% arg1_sent_file_path )
	end = time.time()

	print 'extracting parse tree of all arg1 cost %f' % (end-start)

	start = time.time()
	os.system( 'java -jar lib/BerkeleyParser-1.7.jar -gr lib/eng_sm6.gr -inputFile %s -outputFile tmp/arg2_parsetree.txt'
		% arg2_sent_file_path )
	end = time.time()

	print 'extracting parse tree of all arg2 cost %f' % (end-start)

def get_word_pair_from_file_with_count(fname):
	all_relations = read_data(fname)
	punctuation = ['.', ',', '!', '"', '#', '&', '\'', '*', '+', '-', '...', '/', ':', ';', '<', '=', '>', '?', '@', '[', '\\',\
		']', '^', '_', '`', '|', '~', '$', '%', '--', '``', '\'\'']
	dict = {}
	for relation in all_relations:
		for a1 in relation['Arg1']['Lemma']:
			for a2 in relation['Arg2']['Lemma']:
				if a1 in punctuation or a2 in punctuation or a1[0] in '0123456789' or a2[0] in '0123456789':
					pass
				else:
					#pair = '%s|%s' % (stem_string(a1), stem_string(a2))
					pair = '%s|%s' % (a1, a2)
					if pair in dict:
						dict[pair] += 1
					else:
						dict[pair] = 1

	return dict

def write_dependency_rule_sorted():
	with codecs.open('dict/dependency_rule_by_relation.txt', 'r', encoding = 'utf8', errors = 'ignore') as file:
		dependency_rules = file.read().split('\n')
	
	dependency_rule_dict = {}
	for drule_by_relation in dependency_rules:
		rules = drule_by_relation.split('||')
		for rule in rules:
			if rule in dependency_rule_dict:
				dependency_rule_dict[rule] += 1
			else:
				dependency_rule_dict[rule] = 1
	sorted_drule_list = [item[0] for item in sorted(dependency_rule_dict.items(), key = lambda v : v[1], reverse = True) ]

	with codecs.open(config.DEPENDENCY_RULES, 'w', encoding = 'utf8', errors = 'ignore') as file:
		#file.write( '\n'.join([ '%s:%d'%(rule, dependency_rule_dict[rule]) for rule in sorted_drule_list]) )
		file.write( '\n'.join(sorted_drule_list) )

'''
	each line is dependency rules of a relation
'''
def write_dependency_rule_by_line(file_name):
	from nltk.parse.stanford import StanfordDependencyParser
	jar = 'lib/stanford-parser-full-2015-12-09/stanford-parser.jar'
	models_jar = 'lib/stanford-parser-full-2015-12-09/stanford-parser-3.6.0-models.jar'
	dependency_parser = StanfordDependencyParser(path_to_jar = jar, path_to_models_jar = models_jar, java_options='-mx3000m')

	all_relations = read_data(file_name)

	print( 'len of all relations: %d' % (len(all_relations)) )
	sentences = []
	lineno = 0
	line_interval = []
	for idx, relation in enumerate(all_relations):
		_from = lineno

		lines = []
		sent = []
		if '.' in relation['Arg1']['Lemma']:
			for word in relation['Arg1']['Lemma']:
				if word == '.':
					lines.append(' '.join(sent).encode('utf8').replace('\xc2\xa0', ''))
					sent = []
				else:
					sent.append(word)
			lines.append(' '.join(sent).encode('utf8').replace('\xc2\xa0', ''))
		else:
			lines.append(' '.join(relation['Arg1']['Lemma']).encode('utf8').replace('\xc2\xa0', ''))
		
		_to = _from + len(lines)

		sentences += lines
		lines = []
		sent = []
		if '.' in relation['Arg2']['Lemma']:
			for word in relation['Arg2']['Lemma']:
				if word == '.':
					lines.append(' '.join(sent).encode('utf8').replace('\xc2\xa0', ''))
					sent = []
				else:
					sent.append(word)
			lines.append(' '.join(sent).encode('utf8').replace('\xc2\xa0', ''))
		else:
			lines.append(' '.join(relation['Arg2']['Lemma']).encode('utf8').replace('\xc2\xa0', ''))

		_to += len(lines)
		sentences += lines
		lineno = _to
		line_interval.append( (_from, _to ) )
	pass
	for idx, pair in enumerate(line_interval):
		print( '(%d:%d)' % (pair[0],pair[1]) )
		for i in range(pair[0],pair[1]):
			print( '%d:%s' % (i,sentences[i]) )
	
	print( 'len of sentences: %d' % ( len(sentences) ) )

	line_interval_idx = 0
	count = 0
	'''
		each result is correspoding to a sentence
		a line_interval [from, to)
	'''
	relation_length = len(all_relations)
	all_part = 5
	for part in range(all_part+1):
		_from = part * (relation_length / all_part) # inclusive
		if _from >= relation_length:
			break
		_to = min( (part+1) * (relation_length / all_part) -1, relation_length - 1 ) # inclusive
		print('part %d' % part)
		print('relation %d' % (_to - _from+1))

		to_parse_sentences = sentences[ line_interval[_from][0] : line_interval[_to][1] ]
		print('line of sentences %d' % ( len(to_parse_sentences) ) )

		start = time.time()
		parse_result = dependency_parser.raw_parse_sents(to_parse_sentences)
		end = time.time()
		print( 'cost %f' % (end - start) )

		dep_rule_list = []
		dep_rule_for_one_relation = []
		acutal_result_no = 0
		for result in parse_result:
			acutal_result_no += 1
			for t in result:
				for node in range(len(t.nodes)):
					if t.nodes[node]['word'] == None or t.nodes[node]['deps'].items() == []:
						continue
					else:
						dep_rule_for_one_relation.append( '%s<-%s' % \
							(t.nodes[node]['word'],	' '.join( [ key for key, val in t.nodes[node]['deps'].items() ] )))	
			if count == line_interval[line_interval_idx][1] - 1:
				print '%d: (%d, %d) finished' % (line_interval_idx, line_interval[line_interval_idx][0], line_interval[line_interval_idx][1])
				line_interval_idx += 1
				dep_rule_list.append(dep_rule_for_one_relation)
				dep_rule_for_one_relation = []
			
			count += 1
		print 'actual parse result no : %d' % acutal_result_no
		# last relation
		#print '%d: (%d, %d) finished' % (line_interval_idx, line_interval[line_interval_idx][0], line_interval[line_interval_idx][1])
		#line_interval_idx += 1
		#dep_rule_list.append(dep_rule_for_one_relation)

		write_data = []
		for dep_rules in dep_rule_list:
			write_data.append( '||'.join([rule for rule in dep_rules] ) )

		print('length of  write_data %d' % len(write_data))
		with codecs.open('tmp/dep_rule_%s_part%d.txt'% (file_name, part), 'w', encoding = 'utf-8') as file:
			file.write( u'\n'.join(write_data) )
	pass#for part in range(all_part) end

def predict_correct(classifier, gold):
	results = classifier.classify_many([fs for (fs, l) in gold])

	correct = [l == r for ((fs, l), r) in zip(gold, results)]
	return sum(correct)

def deal_with_rest_data():
	with codecs.open('train_pdtb.json', encoding='utf8',errors='ignore') as file:
		from collections import defaultdict
		stat = defaultdict(int)
		data = []
		for no, line in enumerate(file):
			obj = json.loads(line)
			if obj['Type'] == 'Implicit':
				for s in obj['Sense']:
					if map_sense_to_number(s) > 7:
						data.append(line)
						stat[s] += 1
						break
	print stat
	with codecs.open('rest.json', 'w', encoding='utf8',errors='ignore') as file:
		file.write(''.join(data))

	#write_dependency_rule_by_line('rest.json')
	pass

	
def combine():
	cnt = 0
	trainf = open('dict/dependency_rule_by_relation.txt', 'r')
	devf = open('tmp/dep_rule_dev_pdtb.json.txt', 'r')
	res = open('dict/all_dependency_rule_by_relation.txt', 'w')
	for line in trainf:
		cnt += 1
		res.write(line)
	print cnt
	res.write('\n')
	for line in devf:
		res.write(line)
		cnt += 1
	print cnt
	res.close()

if __name__ == '__main__':
	#analyze_data()
	#deal_with_rest_data()
	"""
	relations = read_data('train_pdtb.json')
	sent_len = []
	for index, relation in enumerate(relations):
		leng = len(relation['Arg1']['Lemma'])
		if leng > 200 : print index
		sent_len.append(len(relation['Arg1']['Lemma']))
		leng = len(relation['Arg2']['Lemma'])
		if leng > 200 : print index
		sent_len.append(len(relation['Arg2']['Lemma']))
	"""
	#get_production_rule_from_file_with_count()
	#__deprecated_get_production_rule_from_file_with_count()
	#strip_prod_rule()
	#analyze_data()
	#write_word_pairs_to_file()
	#relations = read_data('dev_pdtb.json')
	#print(relations)
	#write_parse_tree_to_file('dev_pdtb.json')
	#get_productions()
	combine()
	pass
	
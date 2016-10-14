# -*- coding: utf-8 -*- 
import config
import nltk, codecs, json, pickle, time, sys
from sklearn.svm import SVC
from nltk.classify.scikitlearn import SklearnClassifier
import argparse
import os
from nltk.tree import Tree
MODEL = 'model/train.model'
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
def read_data(file_name):
	data = []
	with codecs.open(file_name, 'r', encoding = 'utf-8') as f:
		for line in f:
			obj = json.loads(line)
			if obj['Type'] == 'Implicit':
				data.append(obj)

	return data


def no2sense(num):
	if num >= len(SENSES):
		return 'Error'
	else:
		return SENSES[num]
def load_wp(file_name, length=-1):
	dict = {}
	wp_file = open(file_name)

	for lineno, line in enumerate(wp_file):
		if line == '':
			continue
		if lineno == length:
			break
		dict[line[:-1]] = lineno

	return dict

def load_prule(file_name, length = -1):
	dict = {}
	file = open(file_name)
	for lineno, line in enumerate(file):
		if lineno == length:
			break
		else:
			dict[line[:-2]] = lineno
	
	return dict

def load_drule(file_name, length = -1):
	dict = {}
	with codecs.open(file_name, 'r', encoding = 'utf-8') as file:
		for lineno, line in enumerate(file):
			if lineno == length:
				break
			else:
				dict[line[:-1]] = lineno
	
	return dict

def load_first_last_dict(file_name, length = -1):
	dict = {}
	with codecs.open(file_name, 'r', encoding = 'utf-8') as file:
		for lineno, line in enumerate(file):
			if lineno == length:
				break
			else:
				dict[line[:-1]] = lineno
	return dict

def get_ptree(file_name):
	all_relations = read_data(file_name)
	dict = {}
	arg1_sent = []
	arg2_sent = []
	arg1_sent_path = config.TEST_ARG1_SENT
	arg2_sent_path = config.TEST_ARG2_SENT
	for relation in all_relations:
		arg1_sent.append( ' '.join(relation['Arg1']['Lemma']) )
		arg2_sent.append( ' '.join(relation['Arg2']['Lemma']) )

	with codecs.open(arg1_sent_path, 'w', encoding = 'utf-8') as file:
		file.write( u'\n'.join(arg1_sent) )

	with codecs.open(arg2_sent_path, 'w', encoding = 'utf-8') as file:
		file.write( u'\n'.join(arg2_sent) )

	start = time.time()
	cmd = 'java -jar lib/BerkeleyParser-1.7.jar -gr lib/eng_sm6.gr -inputFile %s -outputFile %s' % (arg1_sent_path, config.TEST_ARG1_PTREE) 
	print cmd
	os.system(cmd)
	end = time.time()

	print 'generate parse tree of all arg1 %f' % (end-start)

	start = time.time()
	cmd = 'java -jar lib/BerkeleyParser-1.7.jar -gr lib/eng_sm6.gr -inputFile %s -outputFile %s' % (arg2_sent_path, config.TEST_ARG2_PTREE)
	os.system(cmd)
	end = time.time()

	print 'generate parse tree of all arg2 %f' % (end-start)

def word_pairs(relation, dict):
    word_pairs = []
    punctuation = """!"#&'*+,-..../:;<=>?@[\]^_`|~""" + "``" + "''"
    for a1 in relation['Arg1']['Lemma']:
        for a2 in relation['Arg2']['Lemma']:
            if a1 in punctuation or a2 in punctuation:
                pass
            else:
                s = '%s_%s' % (a1, a2) 
                word_pairs.append(s)
                
    wp_dict = {}
    for wp in word_pairs:
        if wp in dict:
            wp_dict['wp(%d)' % dict[wp]] = 1
    return wp_dict

def get_drule(file_name):
    from nltk.parse.stanford import StanfordDependencyParser
    jar = config.STANFORD_PARSER_JAR_PATH
    models_jar = config.STANFORD_PARSER_MODEL_PATH
    dependency_parser = StanfordDependencyParser(path_to_jar = jar, path_to_models_jar = models_jar, java_options='-mx3000m')

    all_relations = read_data(file_name)

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

    start = time.time()
    parse_result = dependency_parser.raw_parse_sents(sentences)
    end = time.time()

    print('extracting dependency rule costs %f s' % (end - start))

    drule_list = []
    drule_one = []
    line_interval_idx = 0
    count = 0
    for result in parse_result:
        for t in result:
            for node in range(len(t.nodes)):
                if t.nodes[node]['word'] == None or t.nodes[node]['deps'].items() == []:
                    continue
                else:
                    drule_one.append( '%s<-%s' % (t.nodes[node]['word'], ' '.join( [ key for key, val in t.nodes[node]['deps'].items() ] ))) 
        if count == line_interval[line_interval_idx][1] - 1:
            line_interval_idx += 1
            drule_list.append(drule_one)
            drule_one = []
        
        count += 1

    write_data = []
    for dep_rules in drule_list:
        write_data.append( '||'.join([rule for rule in dep_rules] ) )

    with codecs.open(config.TEST_DRULE, 'w', encoding = 'utf-8') as file:
        file.write( u'\n'.join(write_data) )

def get_prule_from_ptree(parsetree):
	syntax_tree = Tree.fromstring(parsetree)
	convert_str_format = lambda string, strip_char='\'': ''.join( [ ch for ch in '->'.join( [ st.strip() for st in string.split('->')] ) if ch not in strip_char ] )
	production_rule = [ convert_str_format(str(pr)) for pr in syntax_tree.productions() ]
	
	return production_rule

def production_rules(index, production_rule_dict, parsetree_dict):
    dict_arg1_prule, dict_arg2_prule, dict_both_prule = production_rule_dict
    
    arg1_ptree, arg2_ptree = parsetree_dict

    arg1_prule = get_prule_from_ptree(arg1_ptree[index])[1:]
    arg2_prule = get_prule_from_ptree(arg2_ptree[index])[1:]
    both_prule = list( set(arg1_prule) & set(arg2_prule))

    arg1_production_rule = {}
    arg2_production_rule = {}
    both_production_rule = {}

    for rule in arg1_prule:
        string = 'Arg1_%s' % rule
        if string in dict_arg1_prule:
            arg1_production_rule[ 'Arg1_%d' % dict_arg1_prule[string] ] = 1

    for rule in arg2_prule:
        string = 'Arg2_%s' % rule
        if string in dict_arg2_prule:
            arg2_production_rule[ 'Arg2_%d' % dict_arg2_prule[string] ] = 1

    for rule in both_prule:
        string = 'Both_%s' % rule
        if string in dict_both_prule:
            both_production_rule[ 'Both_%d' % dict_both_prule[string] ] = 1

    ret = {}
    ret.update(arg1_production_rule)
    ret.update(arg2_production_rule)
    ret.update(both_production_rule)

    return ret

def dependency_rules(drule_by_relation, drule_dict):
    drule_list = drule_by_relation.split('||')

    feature = {}
    for rule in drule_list:
        if rule in drule_dict:
            feature[ 'dr(%d)' % drule_dict[rule] ] = 1 

    return feature

def first_last_pairs(relation, dict):
    fl_list = []
    fl_dict = {}
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
    for fl in fl_list:
        if fl in dict:
            fl_dict['fl(%d)' % dict[fl]] = 1
    return fl_dict
def ImplicitTest(file_name, ptree_flag = False, drule_flag = False):
	all_relations = read_data(file_name)
	if ptree_flag or drule_flag:
		print('Get parse tree and dependency rules... \n-----------------------------')
	# prepare production rule
	if ptree_flag:
		get_ptree(file_name)
	if drule_flag:
		get_drule(file_name)

	with codecs.open(config.TEST_DRULE, 'r', encoding = 'utf-8') as file:
		dependency_rule_by_relation = file.read().split('\n')

	# load word pair dict
	dict_word_pairs = load_wp(config.WORD_PAIRS, config.NUM_WP)

	dict_arg1_prule = load_prule(config.ARG1_PRULE, config.NUM_DRULE)
	dict_arg2_prule = load_prule(config.ARG2_PRULE, config.NUM_DRULE)
	dict_both_prule = load_prule(config.BOTH_PRULE, config.NUM_DRULE)

	with codecs.open(config.TEST_ARG1_PTREE, encoding = 'utf-8') as file:
		arg1_ptree = file.read().split('\n')

	with codecs.open(config.TEST_ARG2_PTREE, encoding = 'utf-8') as file:
		arg2_ptree = file.read().split('\n')
	
	# prepare dependency rule
	dict_drule = load_drule(config.DRULE, config.NUM_DRULE)

	dict_flrule = load_first_last_dict(config.FIRST_LAST_RULES, config.NUM_FLRULE)
	
	model = pickle.load(open(MODEL, 'rb'))
	features = []
	correct_no = 0
	pred_label = []
	ext = 0
	start = time.time()
	for index, relation in enumerate(all_relations):
		feat = {}
		feat.update(word_pairs(relation, dict_word_pairs))

		feat.update( production_rules(index, 
							[dict_arg1_prule, dict_arg2_prule, dict_both_prule], 
							[arg1_ptree, arg2_ptree])
					)

		feat.update(dependency_rules(dependency_rule_by_relation[index], dict_drule) )
		
		feat.update(first_last_pairs(relation, dict_flrule))

		pred_label.append( model.classify(feat) )


		if pred_label[index] > 7:
			pred_label[index] = 4
			ext += 1
		for sense in relation['Sense']:
			if sense == no2sense(pred_label[index]):
				correct_no+=1
	pass

	end = time.time()
	print 'external %d' %ext
	print('cost %1.10fs' % (end-start))


	precision = correct_no*1.0 / len(pred_label)
	print 'The precision is %1.5f' % precision

	with codecs.open('predict.json', 'w', encoding = 'utf8', errors = 'ignore') as file:
		write_data = range(len(pred_label))
		for index, plabel in enumerate(pred_label):
			write_data[index] = all_relations[index]
			write_data[index]['Sense'] = [no2sense(plabel)]
		write_data = [json.dumps(wd) for wd in write_data]
		file.write('\n'.join((write_data)))



if __name__ == '__main__':
	generate_drule = generate_prule = False
	argparser = argparse.ArgumentParser(description = "test model with options")
	argparser.add_argument('rule', nargs ='?', help = '''all: generate dependency rules and production rules
		drule: generate dependency rules
		prule: generate production rules
		none: use generated rules\n''')
	argparser.add_argument('file', help = 'test data file required')

	args = argparser.parse_args()

	#print args.rule
	if args.rule == 'all':
		generate_prule = generate_drule = True
	elif args.rule == 'drule':
		generate_drule = True
	elif args.rule == 'prule':
		generate_prule = True
	elif args.rule == 'none':
		pass

	ImplicitTest(args.file, generate_prule, generate_drule)
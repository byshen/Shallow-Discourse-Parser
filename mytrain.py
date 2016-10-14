# -*- coding: utf-8 -*- 
import config
import math
import nltk, codecs
import json, pickle
import time, sys
from nltk.tree import Tree
import numpy as np
from sklearn import metrics
from sklearn.svm import SVC
from nltk.classify.scikitlearn import SklearnClassifier

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


def sense2no(sense):
	if sense in SENSES:
		return SENSES.index(sense)
	else:
		return -1

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

def read_data(file_name):
	data = []
	with codecs.open(file_name, 'r', encoding = 'utf-8') as f:
		for line in f:
			obj = json.loads(line)
			if obj['Type'] == 'Implicit':
				data.append(obj)

	return data



def get_prule_from_ptree(parsetree):
	syntax_tree = Tree.fromstring(parsetree)
	convert_str_format = lambda string, strip_char='\'': ''.join( [ ch for ch in '->'.join( [ st.strip() for st in string.split('->')] ) if ch not in strip_char ] )
	production_rule = [ convert_str_format(str(pr)) for pr in syntax_tree.productions() ]
	
	return production_rule



class ImplicitTrain:
	def __init__(self):
		self.trainData = []
		self.dict_word_pairs = {}
		self.dict_production_rules = {}
	def word_pairs(self, relation, dict):
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
	def production_rules(self, index, parse_dict, parsetree):
	    arg1_production_rule_dict = parse_dict[0]
	    arg2_production_rule_dict = parse_dict[1]
	    both_procution_rule_dict = parse_dict[2] 
	    arg1_parsetree = parsetree[0]
	    arg2_parsetree = parsetree[1]

	    arg1_prule = get_prule_from_ptree( arg1_parsetree[index] )[1:] #ignore '->S'
	    arg2_prule = get_prule_from_ptree( arg2_parsetree[index] )[1:]

	    both_prule = list(set(arg1_prule) & set(arg2_prule))

	    arg1_production_rules = {}
	    for rule in arg1_prule:
	        string = 'Arg1_%s' % rule
	        if string in arg1_production_rule_dict:
	            arg1_production_rules['Arg1_%d' % arg1_production_rule_dict[string] ] = 1
	            
	    arg2_production_rules = {}
	    for rule in arg2_prule:
	        string = 'Arg2_%s' % rule
	        if string in arg2_production_rule_dict:
	            arg2_production_rules['Arg2_%d' % arg2_production_rule_dict[string] ] = 1

	    both_production_rules = {}
	    for rule in both_prule:
	        string = 'Both_%s' % rule
	        if string in arg1_production_rule_dict:
	            both_production_rules['Both_%d' % both_production_rule_dict[string] ] = 1

	    ret = {}
	    ret.update(arg1_production_rules)
	    ret.update(arg2_production_rules)
	    ret.update(both_production_rules)
	    return ret

	def production_rules(self, index, production_rule_dict, parsetree_dict):
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

	def dependency_rules(self, drule_by_relation, drule_dict):
	    drule_list = drule_by_relation.split('||')

	    feature = {}
	    for rule in drule_list:
	        if rule in drule_dict:
	            feature[ 'dr(%d)' % drule_dict[rule] ] = 1 

	    return feature

	def first_last_pairs(self, relation, dict):
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

	def train(self, fname):
		file_name = fname

		self.dict_word_pairs = load_wp(config.WORD_PAIRS, config.NUM_WP)

		dict_arg1_prule = load_prule(config.ARG1_PRULE, config.NUM_PRULE)
		dict_arg2_prule = load_prule(config.ARG2_PRULE, config.NUM_PRULE)
		dict_both_prule = load_prule(config.BOTH_PRULE, config.NUM_PRULE)

		with codecs.open(config.ARG1_PTREE) as file:
			arg1_ptree = file.read().split('\n')

		with codecs.open(config.ARG2_PTREE) as file:
			arg2_ptree = file.read().split('\n')

		dict_drule = load_drule(config.DRULE, config.NUM_DRULE)
		self.trainData = read_data(file_name)
		with codecs.open(config.DEPENDENCY_RELATION, 'r', encoding = 'utf-8', errors = 'ignore') as file:
			dependency_rule_by_relation = file.read().split('\n')
		# First last rules
		dict_flrule = load_first_last_dict(config.FIRST_LAST_RULES, config.NUM_FLRULE)

		feature = []
		start = time.time()
		for index, relation in enumerate(self.trainData):
			tmp_feature = {}
			# wp
			tmp_feature.update(self.word_pairs(relation, self.dict_word_pairs))
			# prule
			tmp_feature.update(self.production_rules(index, [ dict_arg1_prule, dict_arg2_prule, dict_both_prule ], [arg1_ptree, arg2_ptree]))
			# drule
			tmp_feature.update(self.dependency_rules(dependency_rule_by_relation[index], dict_drule))
			# flrule
			tmp_feature.update(self.first_last_pairs(relation, dict_flrule))
			
			for sense in relation['Sense']:
				num_sense = sense2no(sense)
				if num_sense != -1:
					feature.append( (tmp_feature,  num_sense) )
		end=time.time()
		print 'extracting feature finished...'
		start = time.time()

		try:
			model = nltk.MaxentClassifier.train(feature, max_iter = 20)
		except:
			pickle.dump(model, open(config.MODEL, 'wb'), -1)
		end = time.time()
		print('train costs: %f s' %(end-start))

		pickle.dump(model, open(config.MODEL, 'wb'), -1)
		return model
	
if __name__ == '__main__':
	model = ImplicitTrain().train('train_pdtb.json')


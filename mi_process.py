import codecs
import json
import math
import csv
SENSES = ['Expansion.List', 'Expansion.Conjunction',
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

def get_all_wp(fname, length=-1):
	all_pairs = {}
	wp_file = open(fname)

	for lineno, line in enumerate(wp_file):
		if line == '':
			continue
		if lineno == length:
			break
		all_pairs[line[:-1]] = lineno

	return all_pairs

def mycmp(x, y):
	return -cmp(x[2],y[2])

def mi_wps():
	wps = get_all_wp('word_pairs.txt', 10000)
	wps_list = [wp for wp in wps.keys()]
	all_jsons = read_data('train_pdtb.json') 
	
	wp_sense_dict = {}
	sense_dict = {}
	wp_dict = {}
	wp_res_list = []
	hit_wp = 0
	for index, wp in enumerate(wps_list):
		wp_dict[wp] = 0
	for sense in SENSES:
		sense_dict[sense] = 0
	for index, relation in enumerate(all_jsons):
		if index % 100 == 0: 
			print 'index %d' % index
			print hit_wp
			
		for arg1 in relation['Arg1']['Lemma']:
			for arg2 in relation['Arg2']['Lemma']:
				if '%s_%s' % (arg1, arg2) in wps_list:
					wp = '%s_%s' % (arg1, arg2)
					hit_wp +=1
					#print wp
					wp_dict[wp] += 1
					if not wp in wp_sense_dict:
						wp_sense_dict[wp] = {}
					for sense in relation['Sense']:
						sense_dict[sense] += 1
						if not sense in wp_sense_dict[wp]:
							wp_sense_dict[wp][sense] = 0
						wp_sense_dict[wp][sense] += 1
	print 'pre process finished...\n'
	with open('wp_sense_dict.json', 'w') as f:
		f.write(json.dumps(wp_sense_dict))

	total = 0
	for sense in SENSES:
		total+= sense_dict[sense]
	print total
	#print wps_list
	for index, wp in enumerate(wps_list):
		if wp_dict[wp] == 0:
			print wp
			continue
		mi = []

		for sense in wp_sense_dict[wp]:
			n11 = wp_sense_dict[wp][sense]
			n01 = sense_dict[sense] - n11
			n10 = wp_dict[wp] - n11
			n00 = total - n11 - n10 - n01
			n1_ = n11+n10
			n_1 = n11+n01
			n0_ = n01+n00
			n_0 = n10+n00

			mi_value = 0
			if not n11 == 0: mi_value += n11*1.0/(total* math.log(total*n11*1.0/(n1_*n_1), 2))
			if not n01 == 0: mi_value += n01*1.0/(total* math.log(total*n01*1.0/(n0_*n_1), 2))
			if not n10 == 0: mi_value += n10*1.0/(total* math.log(total*n10*1.0/(n1_*n_0), 2))
			if not n00 == 0: mi_value += n00*1.0/(total* math.log(total*n00*1.0/(n0_*n_0), 2))
			mi.append((sense, mi_value))
		if len(mi) == 0: continue
		mi_max = mi[0]
		for i in mi:
			if i[1] > mi_max[1]:
				mi_max = i
		wp_res_list.append((wp, mi_max[0], mi_max[1]))
		print mi_max
	wp_res_list.sort(mycmp)
	print 'process finished...\n'
	wp_mi_file = open('word_pairs, mi', 'w')
	for i, wp_res in enumerate(wp_res_list):
		wp_mi_file.write(str(wp_res_list[i][0]) + ' ' + str(wp_res_list[i][1]) + ' ' + str(wp_res_list[i][2]) + '\n')

	wp_mi_file.close()
'''
def mi_prule():
'''

mi_wps()
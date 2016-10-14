# Shallow Discourse Parser

## Description
A typical text consists of sentences that are glued together in a systematic way to form a coherent discourse. Shallow discourse parsing is the task of parsing a piece of text into a set of discourse relations between two adjacent or non-adjacent discourse units. We call this task shallow discourse parsing because the relations in a text are not connected to one another to form a connected structure in the form of a tree or graph.

More can be found in [CoNLL](http://www.cs.brandeis.edu/~clp/conll16st/index.html) site.

In this project, I extracted features `word pair`, `production rules` and `dependency rules`. And I added `first last pairs` to increase accuracy. After extract the features, I used Mutual Information to decrease dimentions and trained the model with `maxent` classifier in `ntlk`. Final results reached accuracy of 40.7 on the test data set. More results can be found in the Project report.(in Chinese)

## File description

`data/`:		some files for training 

`lib/`:		some open tool libraries for feature extraction

`model/`:	some models saved

`test/`:		directory for save files generated in testing

`cleandata.py`:	some functions for data cleaning

`config.py`:	constants in programs

`mytest.py`:	test program

`mytrain.py`:train program

`preprocess.py`:	some functions for generating train data

`scorer.py`:	standard scorer program

`predict.json`:	the default test output

## Requirements

java -version >= 1.8.0
ntlk 3.0.0
sklearn

## Usage
For train:
	python mytrain.py
The default output is 'train.model'

For test:
usage: mytest.py [-h] [rule] file

test model with options
  rule        	all: 	generate dependency rules and production rules 
		drule:	generate dependency rules 
		prule: 	generate production rules 	
		none:  	use generated rules
  file        test data file required

example:

	python mytest.py all test_pdtb.nosense.json	
The default output is 'predict.json'

If you have any problem running the program, contact ahshenbingyu@163.com


## References

[1] Lin, Z., Kan, M. Y., & Ng, H. T. (2009). Recognizing implicit discourse relations in the Penn Discourse Treebank.

[2] Chen, D., & Manning, C. D. (2014). A Fast and Accurate Dependency Parser using Neural Networks.

[3] Ji, Y., & Eisenstein, J. (2014). One vector is not enough: Entity-augmented distributional semantics for discourse relations.

[4] Ziheng Lin, Hwee Tou Ng, and Min-Yen Kan. (2010). A PDTB-Styled End-to-End Discourse Parser

[5] Pitler, E., Louis, A., & Nenkova, A. (2009). Automatic sense prediction for implicit discourse relations in text

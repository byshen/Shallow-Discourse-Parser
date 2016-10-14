#!/bin/python
import argparse
import json

def evaluate_sense(gold_list, predicted_list):
    predicted_map = {}
    for p in predicted_list:
        predicted_map[p["ID"]] = p
    num_all = 0
    num_right = 0
    for g in gold_list:
        num_all += 1
        cur_id = g["ID"]
        if cur_id in predicted_map:
            p = predicted_map[cur_id]
            if p["Sense"][0] in g["Sense"]:
                num_right += 1
    print("Acc: %f" % (num_right / (num_all+0.)))

def main():
    parser = argparse.ArgumentParser(
        description="Evaluate system's output against the gold standard")
    parser.add_argument('gold', help='Gold standard file')
    parser.add_argument('predicted', help='System output file')
    args = parser.parse_args()
    gold_list = [json.loads(x) for x in open(args.gold)]
    predicted_list = [json.loads(x) for x in open(args.predicted)]
    print ('\n================================================')
    non_explicit_gold_list = [x for x in gold_list if x['Type'] == 'Implicit']
    non_explicit_predicted_list = [x for x in predicted_list if x['Type'] == 'Implicit']
    evaluate_sense(non_explicit_gold_list, non_explicit_predicted_list)

if __name__ == '__main__':
    main()

# json_diff.py
import json
from deepdiff import DeepDiff

def get_json_diff(file1_path, file2_path):
    with open(file1_path, 'r', encoding='utf-8') as f1, open(file2_path, 'r', encoding='utf-8') as f2:
        json1 = json.load(f1)
        json2 = json.load(f2)

    diff = DeepDiff(json1, json2, view='tree')
    if not diff:
        return "No differences found!"

    return diff.pretty()

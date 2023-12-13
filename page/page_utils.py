import os
import json

exp_file = "/home/raspberryunq/db_page_ratones-main/dbs/last_exp.txt"

def read_exp_file():
    if os.path.exists(exp_file):
        with open(exp_file, "r") as f:
            last_exp_data = json.load(f)
    else:
        last_exp_data = {}
    return last_exp_data

def write_exp_file(last_exp_data):
    with open(exp_file, "w") as f:
        json.dump(last_exp_data, f)
    


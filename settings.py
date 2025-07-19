import csv, sys, requests, json, pandas as pd

#Global Variables
def init():
    global version
    version = "0.0.5"

    global file_path
    file_path = f"{sys.argv[1]}"

    global item_dict
    global inv_list
    global wfm_api_version
    global wfm_api_item_dump
    global items_df
    global json_path
    global set_list
    global bp_list

    item_dict = {}
    inv_list = []
    wfm_api_version = ""
    wfm_api_item_dump = ""
    items_df = []
    json_path = "./wfm-api-item-dump.json"
    set_list = {}
    bp_list = []
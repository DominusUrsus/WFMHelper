import csv, sys, requests, json, pandas as pd

#Global Variables
def init():
    global version
    version = "0.1.0"

    global file_path
    file_path = f"{sys.argv[1]}"

    global api_url
    api_url = "https://api.warframe.market/v2/"

    global item_dict
    global inv_list
    global wfm_api_version
    global wfm_api_item_dump
    global set_item_dump
    global items_df
    global json_path
    global set_data
    global set_list
    global set_root_item_id
    global bp_list
    global typo_list
    
    item_dict = {}
    inv_list = []
    wfm_api_version = ""
    wfm_api_item_dump = ""
    set_item_dump = {}
    items_df = []
    json_path = "./wfm-api-item-dump.json"
    set_list = []
    set_root_item_id = None
    set_data = None
    bp_list = []
    typo_list = []

item_dict = {}
inv_list = []

def get_blueprint_status(item):
    pass

def get_set_status(item):
    pass

def get_item_id(item):
    pass

def get_item_value(item):
    pass

#Open and parse csv file given as argument + create a global inventory
def csv_parser(file_path):
    with open(file_path, newline = '') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            item_dict ={"item": row[0], "count": int(row[1])}
            inv_list.append(item_dict)
    print(f"Debug: Inventory list:{inv_list}")
    return inv_list
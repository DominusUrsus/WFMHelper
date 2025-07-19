import csv, sys, requests, json, pandas as pd
#from invbuilder import get_item_id, get_blueprint_status, get_item_slug, get_item_value, get_set_count, get_set_parts, get_set_status
version = "0.0.3"

if len(sys.argv) != 2:
    print("Usage: python3 main.py <path to csv>")
    sys.exit(1)

file_path = f"{sys.argv[1]}"

#Global Variables
item_dict = {}
inv_list = []
wfm_api_version = ""
wfm_api_item_dump = ""
items_df = []
json_path = "./wfm-api-item-dump.json"

#Initialize wfm api, store items in wfm_api_item_dump var, check version information, and store wfm-api-item-dump.json
def init_wfm_api():
    try:
        wfm_api_item_dump = requests.get("https://api.warframe.market/v2/items")
        wfm_api_item_dump.raise_for_status()
        wfm_api_version = wfm_api_item_dump.json()["apiVersion"]
        with open(json_path, 'w') as file:
            json.dump(wfm_api_item_dump.json(), file, indent = 4)
            print(f"WFM API Intialized. Storing data in {json_path}")
            print(f"WFM API Version: {wfm_api_version}")
    except requests.RequestException as e:
        print(f"Error fetching API data: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except IOError as e:
        print(f"Error writing to file: {e}")

#Convert wfm_api_item_dump to a data frame
def convert_item_dataframe():
    global items_df
    with open(json_path, "r") as file:
        d = json.load(file)
        items_df = pd.json_normalize(d['data'])
    print("Converted WFM Items to a data frame")
    #print("Dataframe columns:", items_df.columns.tolist())
    #print("Sample Data:\n", items_df.head().to_string())

def get_item_id(item):
    try:
        item_id = items_df[items_df["i18n.en.name"] == item]["id"]
        #print(f"Debug: get_item_id for {item}: {item_id}")
        return item_id.iloc[0]
    except KeyError as e:
        print(f"KeyError: Column {e} not found in items_df. Available columns: {items_df.columns.tolist()}")
        return None
    except Exception as e:
        print(f"Error in get_item_id: {e}")
        return None

#Finds item slug in items_df
def get_item_slug(item):
    #print(f"Checking for {item} in items_df")
    try:
        item_slug = items_df[items_df["i18n.en.name"] == item]["slug"]
        #print(f"Debug: get_item_slug for {item}: {item_slug}")
        return item_slug.iloc[0]
    except KeyError as e:
        print(f"KeyError: Column {e} not found in items_df. Available columns: {items_df.columns.tolist()}")
        return None
    except Exception as e:
        print(f"Error in get_item_slug: {e}")
        return None

#Checks if an item is a blueprint based on name (Refactor to check against API db later?)
def get_blueprint_status(item):
    item_bp_status = False
    if item.split():
        return False

def get_set_status(item):
    pass

def get_set_parts(item):
    pass

def get_set_count(item):
    pass

def get_item_value(item):
    pass

#Function to append "Blueprint" to wf strings that do not include it
def correct_item_name (item):
    correct_string = item.split()
    correct_string.append ("Blueprint")
    result = " ".join(correct_string)
    #print(f"Debug: correct_item_name running - correct string: {result}")
    return result

#Open and parse csv file given as argument + create a global inventory
def csv_parser(file_path):
    with open(file_path, newline = '') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        prime_parts_key = ["Chassis", "Neuroptics, Systems"]
        for row in reader:
            #Checking if WF parts names contain Blueprint
            if any(keyword in row[0] for keyword in prime_parts_key) and "Blueprint" not in row[0]:
                row[0] = correct_item_name(row[0])
                #print(f"Debug: Incorrect item name for: {row[0]}")

            #CSV Returns each row as a list, index and add values to keys based on info
            item_dict = {
                "item": row[0], 
                "count": int(row[1]), 
                "item_slug": get_item_slug(row[0]), 
                "item_id": get_item_id(item_dict[item_slug]),
                "is bp": get_blueprint_status (item_dict[item_slug])
            }
            print(f"Debug: item_dict:{item_dict}")
            inv_list.append(item_dict)
    #print(f"Debug: Inventory list:{inv_list}")
    return inv_list

def main():
    print(f"WFMHelper version: {version}")
    init_wfm_api()
    convert_item_dataframe()
    print(f"Checking inventory with path: {file_path}")
    csv_parser(file_path)

main()

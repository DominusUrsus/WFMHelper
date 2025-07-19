import csv, sys, requests, json, pandas as pd, settings

#CHeck start args or error out
if len(sys.argv) != 2:
    print("Usage: python3 main.py <path to csv>")
    sys.exit(1)

#Initialize wfm api, store items in wfm_api_item_dump var, check version information, and store wfm-api-item-dump.json
def init_wfm_api():
    try:
        settings.wfm_api_item_dump = requests.get("https://api.warframe.market/v2/items")
        settings.wfm_api_item_dump.raise_for_status()
        settings.wfm_api_version = settings.wfm_api_item_dump.json()["apiVersion"]
        with open(settings.json_path, 'w') as file:
            json.dump(settings.wfm_api_item_dump.json(), file, indent = 4)
            print(f"WFM API Intialized. Storing data in {settings.json_path}")
            print(f"WFM API Version: {settings.wfm_api_version}")
    except requests.RequestException as e:
        print(f"Error fetching API data: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except IOError as e:
        print(f"Error writing to file: {e}")

        #Convert wfm_api_item_dump to a data frame
def convert_item_dataframe():
    with open(settings.json_path, "r") as file:
        d = json.load(file)
        settings.items_df = pd.json_normalize(d['data'])
    #print("Converted WFM Items to a data frame")
    #print("Dataframe columns:", settings.items_df.columns.tolist())
    #print("Sample Data:\n", settings.items_df.head().to_string())

def get_item_id(item):
    try:
        item_id = settings.items_df[settings.items_df["i18n.en.name"] == item]["id"]
        #print(f"Debug: get_item_id for {item}: {item_id}")
        return item_id.iloc[0]
    except KeyError as e:
        print(f"KeyError: Column {e} not found in settings.items_df. Available columns: {settings.items_df.columns.tolist()}")
        return None
    except Exception as e:
        print(f"Error in get_item_id: {e}")
        return None

#Finds item slug in settings.items_df
def get_item_slug(item):
    #print(f"Checking for {item} in settings.items_df")
    try:
        global item_slug
        item_slug = settings.items_df[settings.items_df["i18n.en.name"] == item]["slug"]
        #print(f"Debug: get_item_slug for {item}: {item_slug}")
        return item_slug.iloc[0]
    except KeyError as e:
        print(f"KeyError: Column {e} not found in settings.items_df. Available columns: {settings.items_df.columns.tolist()}")
        return None
    except Exception as e:
        print(f"Error in get_item_slug: {e}")
        return None

#Checks if an item is a blueprint based on name (Refactor to check against API db later?)
def get_blueprint_status(item):
    #print(f"Tags List: {settings.items_df[settings.items_df["i18n.en.name"] == item]["tags"].iloc[0]}")
    #print(f"Get BP Status arg: {item}")

    #Check first if item is NOT a BP, then check if item is a WF BP, finally verify that BP tag does exist, else should not happen - if error prints, check that the API is working, or for typos
    if "blueprint" not in settings.items_df[settings.items_df["i18n.en.name"] == item]["tags"].iloc[0]:
        return False
    elif "component" in settings.items_df[settings.items_df["i18n.en.name"] == item]["tags"].iloc[0]:
        return False
    elif "blueprint" in settings.items_df[settings.items_df["i18n.en.name"] == item]["tags"].iloc[0]:
        settings.bp_list.append(item)
        #print (f"BPs to check set: {settings.bp_list}")
        return True
    else:
        print(f"Error checking if {item} IS blueprint and NOT warframe component")
        return False

#iterate over settings.bp_list, call get_set_parts, for all sets that return true, call get_set_count
def set_builder(bp_list_checking):
    #As iterating, if a set resolves to true, get_set_count 
    pass

#Check against API for other set pieces, call inside set_builder if we have a set of item, and return IDs in list 
def get_set_parts(list_to_check):
    pass

#Call when set_builder resolves true
def get_set_count(item):
    #Check against quantityInSet
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
    with open(settings.file_path, newline = '') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        prime_parts_key = ["Chassis", "Neuroptics, Systems"]
        for row in reader:
            #Checking if WF parts names contain Blueprint
            if any(keyword in row[0] for keyword in prime_parts_key) and "Blueprint" not in row[0]:
                item_name = correct_item_name(row[0])
            else:
                item_name = row[0]
                #print(f"Debug: Incorrect item name for: {row[0]}")

            #CSV Returns each row as a list, index and add values to keys based on info
            settings.item_dict = {
                "item": item_name, 
                "count": int(row[1]), 
                "item_slug": get_item_slug(item_name), 
                "item_id": get_item_id(item_name),
                "is bp": get_blueprint_status (item_name)
            }
            print(f"Debug: settings.item_dict:{settings.item_dict}")
            settings.inv_list.append(settings.item_dict)
    #print(f"Debug: Loop Fin - Inventory list:{settings.inv_list}")
    return settings.inv_list

def main():
    settings.init()
    print(f"WFMHelper version: {settings.version}")
    init_wfm_api()
    convert_item_dataframe()
    print(f"Checking inventory with path: {settings.file_path}")
    csv_parser(settings.file_path)

main()

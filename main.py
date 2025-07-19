import csv, sys, requests, json, pandas as pd, settings
from pyrate_limiter import Duration, Rate, Limiter, BucketFullException, InMemoryBucket, LimiterDelayException

#Check start args or error out
if len(sys.argv) != 2:
    print("Usage: python3 main.py <path to csv>")
    sys.exit(1)

#Initialize wfm api, check version information, and store items in wfm-api-item-dump.json
def init_wfm_api():
    try:
        settings.wfm_api_item_dump = requests.get(settings.api_url + "items")
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

#Finds item id in settings.items_df
def get_item_id(item):
    try:
        item_id = settings.items_df[settings.items_df["i18n.en.name"] == item]["id"]
        #print(f"Debug: get_item_id for {item}: {item_id}")
        return item_id.iloc[0]
    except KeyError as e:
        print(f"KeyError: Column {e} not found in settings.items_df. Available columns: {settings.items_df.columns.tolist()}")
        return None
    except IndexError as e:
        print(f"IndexError: Check for correct spelling of item: ({item}) in csv file? Error: {e}")
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
    except IndexError as e:
        print(f"IndexError: Check for correct spelling of item: ({item}) in csv file? Error: {e}")
    except Exception as e:
        print(f"Error in get_item_slug: {e}")
        return None

#Check first if item is NOT a BP, then check if item is a WF BP, finally verify that BP tag does exist, else should not happen - if error prints, check that the API is working, or for typos
def get_blueprint_status(item):
    try:
        
        if "blueprint" not in settings.items_df[settings.items_df["i18n.en.name"] == item]["tags"].iloc[0]:
            return False
        elif "component" in settings.items_df[settings.items_df["i18n.en.name"] == item]["tags"].iloc[0]:
            return False
        elif "blueprint" in settings.items_df[settings.items_df["i18n.en.name"] == item]["tags"].iloc[0]:
            settings.bp_list.append(item_slug.iloc[0])
            return True
        else:
            print(f"Error checking if {item} IS blueprint and NOT warframe component")
            return False
    except IndexError as e:
        print(f"IndexError: Check for correct spelling of item: ({item}) in csv file? Error: {e}")

#iterate over settings.bp_list, call get_set_parts, for all sets that return true, call get_set_count
def set_builder():

    for slug_to_check in settings.bp_list:
        #print(f"Debug: Current check {slug_to_check}")
        if get_set_status(slug_to_check) == True:
            get_set_parts(slug_to_check)
            #get_set_count(set_to_check)


#Check what other parts are against api set check with slug, check existence of all item_ids in settings.inv_list, return True if all present
#API call is from this function - apply rate limit - WFM API rate limit = 3 req/sec
def get_set_status(slug_to_check):
    #print(f"Current Slug Check: {slug_to_check}")
    try:
        #Get API data with rate limit
        api_set_request = settings.api_url +"item/" + slug_to_check + "/set"
        print(f"Attempting get request to {api_set_request}")
        settings.set_item_dump = requests.get(api_set_request)
        settings.set_item_dump.raise_for_status()
        with open("wfm-set-item-dump.json", 'w') as file:
            json.dump(settings.set_item_dump.json(), file, indent = 4)
            print(f"Received set_item data. Storing data in wfm-set-item-dump.json")
        #print(f"Debug set_item_dump dict: ")

    except TypeError:
        print("TypeError: Received TypeError for get_set_status: Likely a list in item_dict, debug later")
    except BucketFullException as e:
        print(e)
        print(e.meta_info)

    with open("wfm-set-item-dump.json", "r") as file:
            set_data = json.load(file)

    
    comp_list = set_data["data"]["items"][0]["setParts"]

    id_for_check = None
    id_check_list = []
    set_root = set_data["data"]["items"][0]["setRoot"]
    #print(f"Debug: set_root = {set_root}")

    for dict_check in settings.inv_list:
        if dict_check["item_id"] in comp_list:
            id_for_check = dict_check["item_id"]
            id_check_list.append(id_for_check)

    #Remove item set id
    for comp_item in comp_list:
        for item_root in set_data["data"]["items"]:
            if item_root["id"] == comp_item and item_root["setRoot"] is True:
                comp_list.remove(comp_item)
                settings.set_root_item_id = comp_item
                settings.set_list.append(settings.set_root_item_id)
                get_set_parts(comp_list, item_root)
                #print("Somehow this worked")
        
    comp_list.sort()
    id_check_list.sort()
    #print(f"Debug: Current set_status: {id_check_list == comp_list} and set_id: {settings.set_root_item_id}")
    return id_check_list == comp_list


#If get_set_status resolves to true, return list of IDs back to set_builder
def get_set_parts(set_item_list, set_item_id):
    #Update settings.inv_list to reflect sets instead of individual parts
    print("Nothing here yet")
    return set_item_list

#Call when set_builder resolves true, check amount of each item for the set we have in settings.inv_list
def get_set_count(item):
    #Check against quantityInSet
    #Check that items evenly divide if greater than quantityInSet
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
    global item_name
    with open(settings.file_path, newline = '') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        prime_parts_key = ["Chassis", "Neuroptics", "Systems"]
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
            #Call set_builder if current item is a blueprint
            #if settings.item_dict["is bp"] == True:
                #set_builder(settings.item_dict["item_slug"])
            #print(f"Debug: settings.item_dict: {settings.item_dict}")
            settings.inv_list.append(settings.item_dict)
    #print(f"Debug: Loop Fin - Inventory list:{settings.inv_list}")
    return settings.inv_list

def main():
    settings.init()
    print(f"WFMHelper version: {settings.version}")
    init_wfm_api()
    convert_item_dataframe()
    print(f"----------Checking inventory with path: {settings.file_path} -----------")
    csv_parser(settings.file_path)
    print("---------------------- Inventory parsed ----------------------")
    print("---------------------- Checking for sets --------------------")
    set_builder()

main()

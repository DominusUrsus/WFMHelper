import csv, sys, requests, json, pandas as pd, settings

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
        with open(settings.json_path + "wfm-api-item-dump.json", 'w') as file:
            json.dump(settings.wfm_api_item_dump.json(), file, indent = 4)
            print(f"WFM API Intialized. Storing data in {settings.json_path}wfm-api-item-dump.json")
            print(f"WFM API Version: {settings.wfm_api_version}")
    except requests.RequestException as e:
        print(f"Error fetching API data: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except IOError as e:
        print(f"Error writing to file: {e}")

        #Convert wfm_api_item_dump to a data frame
def convert_item_dataframe():
    with open(settings.json_path + "wfm-api-item-dump.json", "r") as file:
        d = json.load(file)
        settings.items_df = pd.json_normalize(d['data'])
    #print("Converted WFM Items to a data frame")
    #print("Dataframe columns:", settings.items_df.columns.tolist())
    #print("Sample Data:\n", settings.items_df.head().to_string())

#Finds item id in settings.items_df
def get_item_id(item):
    global item_id
    try:
        item_id = settings.items_df[settings.items_df["i18n.en.name"] == item]["id"]
        #print(f"Debug: get_item_id for {item}: {item_id}")
        return item_id.iloc[0]
    except KeyError as e:
        print(f"KeyError: Column {e} not found in settings.items_df. Available columns: {settings.items_df.columns.tolist()}")

        return None
    except IndexError as e:
        #print(f"IndexError: Could not get item id for {item}, check for typos")
        return None
    except Exception as e:
        print(f"Error in get_item_id: {e}")
        return None

#Finds item slug in settings.items_df
def get_item_slug(item):
    global item_slug
    #print(f"Checking for {item} in settings.items_df")
    try:
        
        item_slug = settings.items_df[settings.items_df["i18n.en.name"] == item]["slug"]
        #print(f"Debug: get_item_slug for {item}: {item_slug}")
        return item_slug.iloc[0]
    except KeyError as e:
        #print(f"KeyError: Column {e} not found in settings.items_df. Available columns: {settings.items_df.columns.tolist()}")
        return None
    except IndexError as e:
        #print(f"IndexError: Could not get item slug for {item}, check for typos")
        #settings.inv
        pass
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
        #print(f"IndexError: Could not get blueprint status for {item}, check for typos")
        pass

#iterate over settings.bp_list, call get_set_parts, for all sets that return true, call get_set_count

#Check what other parts are against api set check with slug, check existence of all item_ids in settings.inv_list, return True if all present
#API call is from this function - apply rate limit - WFM API rate limit = 3 req/sec
def get_set_status():
    #print(f"Current Slug Check: {slug_to_check}")
    wait_counter = 0
    for item_dict in settings.inv_list:
        wait_counter += 1
        if wait_counter > 20:
            print("Building sets. Please wait...")
            wait_counter = 0 

        try:
            slug_to_check = item_dict["item_slug"]
            #Get API data with rate limit
            api_set_request = settings.api_url +"item/" + slug_to_check + "/set"
            #print(f"Attempting get request to {api_set_request}")
            settings.set_item_dump = requests.get(api_set_request)
            settings.set_item_dump.raise_for_status()
            with open(settings.json_path + "wfm-api-set-dump.json", "w") as file:
                json.dump(settings.set_item_dump.json(), file, indent = 4)
                #print(f"Received set_item data. Storing data in wfm-set-item-dump.json")
            #print(f"Debug set_item_dump dict: ")
        except TypeError:
            print("TypeError: Received TypeError for get_set_status: Likely a list in item_dict, debug later")

        with open(settings.json_path + "wfm-api-set-dump.json", "r") as file:
                settings.set_data = json.load(file)

        comp_list = settings.set_data["data"]["items"][0]["setParts"]

        id_for_check = None
        id_check_list = []
        set_root = settings.set_data["data"]["items"][0]["setRoot"]
        #print(f"Debug: set_root = {set_root}")

        item_dict["ducat_value"] = get_ducat_value(item_dict["item_id"])

        for dict_check in settings.inv_list:
            if dict_check["item_id"] in comp_list:
                id_for_check = dict_check["item_id"]
                id_check_list.append(id_for_check)

                comp_list.sort()
                id_check_list.sort()

        for comp_item in comp_list:
            for item_root in settings.set_data["data"]["items"]:
                if item_root["id"] == comp_item and item_root["setRoot"] is True:
                    settings.set_root_item_id = comp_item
                    comp_list.remove(comp_item)
        
        #print(f"Current list comparison {id_check_list} | {comp_list}")
        #print(f"-----\nDebug: Current set_status: {id_check_list == comp_list} and set_id: {settings.set_root_item_id}\n------")
        if id_check_list == comp_list:
            get_set_parts(comp_list, settings.set_root_item_id)
        
            settings.set_list.append(settings.set_root_item_id)
        
#If get_set_status resolves to true, return list of IDs back to set_builder
def get_set_parts(set_item_list, set_item_id):
    temp_name = None
    temp_slug = None
    #print(f"Debug: get_set_parts running with args: {set_item_list} + {set_item_id}")
    #Update settings.inv_list to reflect sets instead of individual parts
    for item_root in settings.set_data["data"]["items"]:
        if item_root["id"] == set_item_id:
            #print(f"Debug: get_set_parts check item {item_root["id"]}")

            #temp_name = settings.set_data["data"]["items"] == [item_root]["i18n"]["en"]["name"]
            temp_name = item_root["i18n"]["en"]["name"]
            temp_slug = item_root["slug"]
            #print(f"Debug: temp_name {temp_name}")
            set_dict = {
                "item": temp_name,
                "count": get_set_count(set_item_list),
                "item_slug": temp_slug,
                "item_id": set_item_id,
                "is_bp": False,
                "is_set": True,
                "ducat_value" : get_ducat_value(set_item_id),
                "plat_avg": 0 
            }
            #print(f"------------------\nDebug: set_dict: {set_dict}\n------------------")
            settings.inv_list.append(set_dict)
            #print(f"------------------\nDebug: inv_list: {settings.inv_list}\n------------------")

    pass

#Call when set_builder resolves true, check amount of each item for the set we have in settings.inv_list
def get_set_count(set_item_list):
    #print(f"Debug: running get_set_count")
    min_count = 1000
    list_to_del = []
    item_sets = {}

    #Iterate over set_item_list and inv_list, calculate how many sets we can make
    for item in set_item_list:
        for key in settings.inv_list[:]:
            if item == key["item_id"]:
                #print(f"Debug: Checking item: {key["item_slug"]} count: {key["count"]}")
                for item_count in settings.set_data["data"]["items"]:
                    if "quantityInSet" in item_count:
                        sets_possible = key["count"] // item_count["quantityInSet"]
                        item_sets[item] = sets_possible

    if item_sets:
        min_count = min(item_sets.values())                        
    
    #iterate over lists again, add parts that become sets, and delete deprecated parts
    for item in set_item_list:
        for key in settings.inv_list[:]:
            if item == key["item_id"]:
                for item_count in settings.set_data["data"]["items"]:
                    if item_count["id"] == item and "quantityInSet" in item_count:
                        items_used = min_count * item_count["quantityInSet"]
                        key["count"] -= items_used
                        #print(f"**Debug**: Checking item prep for del: {key["item_slug"]} count: {key["count"]}")
                        if key["count"] == 0:
                            #print(f"&&Debug$$: Checking item prep for del: {key["item_slug"]} count: {key["count"]}")
                            list_to_del.append(key)
                            #print(f"Debug: Prepare to remove dicts: {key}\nDebug: list to del {list_to_del}")


    
    for part_dict in list_to_del:
        settings.inv_list.remove(part_dict)
    return min_count if min_count != 1000 else 0

def get_ducat_value(item_id):
    with open(settings.json_path + "wfm-api-set-dump.json", "r") as file:
            settings.set_data = json.load(file)
    
    for listing in settings.set_data["data"]["items"]:
        if item_id == listing["id"]:
            return listing["ducats"]

#Pull current item top sales data from online users (top 5 buy/sell for item_slug) for each item in inv_list
def get_item_value():
    wait_counter = 0
    
    for item_dict in settings.inv_list:
        wait_counter += 1
        if wait_counter > 20:
            print("Checking item values. Please wait...")
            wait_counter = 0

        item_slug = item_dict["item_slug"]
        item_id = item_dict["item_id"]

        if item_slug is not None:
            #print(f"Debug: Fetching value for item: {item_slug}")
            try: 
                settings.wfm_api_value_dump = requests.get(settings.api_url + "orders/item/" + item_slug + "/top")
                settings.wfm_api_value_dump.raise_for_status()
                with open(settings.json_path + "wfm-api-value-dump.json", 'w') as file:
                    json.dump(settings.wfm_api_value_dump.json(), file, indent = 4)
            except requests.RequestException as e:
                print(f"Error fetching API data: {e}")
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
            except IOError as e:
                print(f"Error writing to file: {e}")

            with open(settings.json_path + "wfm-api-value-dump.json", "r") as file:
                price_data = json.load(file)

            price_list = price_data["data"]["sell"]
            current_avg_calc = []

            for listing in price_list:
                if item_id == listing["itemId"]:
                    current_avg_calc.append(listing["platinum"])
            
            avg_value = sum(current_avg_calc) / len(current_avg_calc)
            #print(f"item value for {item_slug} = {avg_value}")
            

            item_dict["plat_avg"] = avg_value

        else: 
            print(f"No data available for item: {item_dict["item"]} (Returned value {item_slug} for item_slug). Removing from list.")
            print(f"Debug: {item_dict}")
            try: 
                settings.inv_list.remove(item_dict)
            except Exception as e:
                print(f"Unable to remove {item_dict} due to error: {e}")
        

def correct_item_name(item):
    correct_string = item.split()
    if "Blueprint" not in correct_string:
        correct_string.append ("Blueprint")
        result = " ".join(correct_string)
    else: 
        result = " ".join(correct_string)
    return result

def correct_melee_name(item):
    correct_string = item.split()
    result = ""
    if "and" in correct_string:
        correct_string.remove("and")
        correct_string.insert(1, "&")
        result = " ".join(correct_string)
        #print(f"Debug: Correcting Melee Name: {result}")
        return result.title()
    else:
        print(f"correct_melee_name failed on item: {item} with result: {result}\nExiting.")
        sys.exit(1)

def correct_spacing(item):
    correct_string = item.split()
    result = " ".join(correct_string)
    #print(f"Debug: Corrected string: {result}")
    return result

#Open and parse csv file given as argument + create a global inventory
def csv_parser(file_path):
    global item_name
    with open(settings.file_path, newline = '') as csvfile:
        capital_stream = (line.title() for line in csvfile)
        reader = csv.reader(capital_stream)

        next(reader)

        #Correct names for sentinels, swuord and shield, and frame parts
        prime_parts_key = ["Chassis", "Neuroptics", "Systems"]
        sentinel_check = ["Carrier", "Dethcube", "Diriga", "Djinn", "Helios", "Nautilus", "Oxylus", "Shade", "Taxon", "Wyrm"]
        sword_board_check = ["silva", "aegis", "cobra", "crane"]

        for row in reader:

            if any(sent_name in row[0].title() for sent_name in sentinel_check):
                item_name = row[0].title().lstrip()
            elif any(keyword in row[0].title() for keyword in prime_parts_key) and "blueprint" not in row[0]:
                item_name = correct_item_name(row[0].title())
            elif any(melee_name in row[0].lower() for melee_name in sword_board_check):
                item_name = correct_melee_name(row[0].lower())
            else:
                item_name = row[0].title().lstrip()

            #CSV Returns each row as a list, index and add values to keys based on info
            settings.item_dict = {
                "item": item_name, 
                "count": int(row[1]), 
                "item_slug": get_item_slug(item_name),
                "item_id": get_item_id(item_name),
                "is_bp": get_blueprint_status (item_name),
                "is_set": False,
                "ducat_value" : 0,
                "plat_avg": 0 
            }

            if settings.item_dict["item_slug"] is not None:
                settings.inv_list.append(settings.item_dict)
                #get_set_status(item_slug.iloc[0])
                #get_ducat_value(item_id.iloc[0])
            else:
                print(f"ERROR: Item {item_name} not found. Check for typos.")
                pass
sales_threshold = 10
sell_list = []
vendor_list = []

def sort_item_lists():
    for item_dict in settings.inv_list:
        if item_dict["item_slug"] == None:
            pass
        elif item_dict["is_set"] == True or item_dict["plat_avg"] >= sales_threshold:
            sell_list.append(item_dict)
        else:
            vendor_list.append(item_dict)

def main():
    settings.init()
    print(f"WFMHelper version: {settings.version}")
    init_wfm_api()
    convert_item_dataframe()
    print(f"--------- Checking inventory with path: {settings.file_path} ----------")
    csv_parser(settings.file_path)
    print("---------------------- Inventory parsed ---------------------")

    print("--------------------- Checking for sets ---------------------")
    get_set_status()
    print("-------------------- Checking item values -------------------")
    get_item_value()
    print("--------------------- Sorting item lists --------------------")
    sort_item_lists()
    print("----------------- Completed. Outputting file. ---------------")

    #output_file = open("test_output.json", "w", encoding='utf-8')
    #json.dumps(settings.typo_list)
    #for line in settings.inv_list:
        #json.dump(line, output_file)
        #output_file.write("\n")

    sell_output = "sell_output.txt"
    vendor_output = "vendor_output.txt"
    sell_output_file = open(sell_output, "w", encoding='utf-8')
    vendor_output_file= open(vendor_output, "w", encoding='utf-8')

    with open(sell_output, "w") as f:
        for line in sell_list:
            f.write(f"Item:{line["item"]}\nCount:{line["count"]}\nPlatinum:{line["plat_avg"]}\nDucats:{line["ducat_value"]}\n-------------------------\n")
    with open(vendor_output, "w") as f:
        for line in vendor_list:
            f.write(f"Item:{line["item"]}\nCount:{line["count"]}\nPlatinum:{line["plat_avg"]}\nDucats:{line["ducat_value"]}\n-------------------------\n")
    print(f"-- Output file saved to {sell_output} + {vendor_output} --")
    print("---------- Output file saved to ./test_output.json ----------")



main()

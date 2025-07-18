import csv, sys, requests, json
from invbuilder import *
version = "0.0.2"

if len(sys.argv) != 2:
    print("Usage: python3 main.py <path to csv>")
    sys.exit(1)

file_path = f"{sys.argv[1]}"

#Global Variables
item_dict = {}
inv_list = []
wfm_api_version = ""

#Initialize wfm api, check version information, and store wfm-api-version-check.json
def init_wfm_api():
    try:
        wfm_api_version_check = requests.get("https://api.warframe.market/v2/versions")
        wfm_api_version_check.raise_for_status()
        json_path = "./wfm-api-version-check.json"
        #parse_response = json.loads(wfm_api_version_check)
        wfm_api_version = wfm_api_version_check.json()["apiVersion"]
        with open(json_path, 'w') as file:
            json.dump(wfm_api_version_check.json(), file, indent = 4)
            print(f"WFM API Intialized. Storing info in {json_path}")
            print(f"WFM API Version: {wfm_api_version}")
    except requests.RequestException as e:
        print(f"Error fetching API data: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except IOError as e:
        print(f"Error writing to file: {e}")
    


#Open and parse csv file given as argument + create a global inventory
def csv_parser(file_path):
    with open(file_path, newline = '') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            #CSV Returns each row as a list, index and add values to keys based on info
            item_dict ={"item": row[0], "count": int(row[1]), "is bp": get_blueprint_status(row[0])}
            inv_list.append(item_dict)
    #print(f"Debug: Inventory list:{inv_list}")
    return inv_list

def main():
    print(f"WFMHelper version: {version}")
    print(f"Checking inventory with path: {file_path}")
    init_wfm_api()
    csv_parser(file_path)

main()

import csv, sys
from invbuilder import *
version = "0.0.1"

if len(sys.argv) != 2:
    print("Usage: python3 main.py <path to csv>")
    sys.exit(1)

file_path =  f"{sys.argv[1]}"

#Open and parse csv file given as argument + create a global inventory
item_dict = {}
inv_list = []
def csv_parser(file_path):
    with open(file_path, newline = '') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            item_dict ={"item": row[0], "count": int(row[1])}
            inv_list.append(item_dict)
    print(f"Debug: Inventory list:{inv_list}")
    return inv_list

def main():
    print(f"WFMHelper version: {version}")
    print(f"Checking inventory with path: {file_path}")
    csv_parser(file_path)

main()

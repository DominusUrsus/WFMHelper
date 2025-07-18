import csv, sys
from invbuilder import *
version = "0.0.1"

if len(sys.argv) != 2:
    print("Usage: python3 main.py <path to csv>")
    sys.exit(1)

file_path =  f"{sys.argv[1]}"

def main():
    print(f"WFMHelper version: {version}")
    print(f"Checking inventory with path: {file_path}")
    csv_parser(file_path)

main()

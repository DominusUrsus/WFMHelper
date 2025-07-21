Warframe Market Helper
Current Version: 1.0.0

A tool to check prices of tradable warframe inventory items, and sort what is and isn't worth selling.
Currently builds a list of items with various metadata about provided inventory items.

To Do: 
Clean up code.
Bash file for easy running.
Implement custom sales threshold.

To Fix:

Future:
Implement auto listing to market.
UI?

Dependencies: 
pandas (pip install pandas)
Input file should be a csv file.

To use: run "python3 main.py <path to file>" within wfmhelper directory.
Returns two lists as sell_output and vendor_list, with name, count, plat, and ducat values.
Test files are in test csv files.

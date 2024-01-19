#!/usr/local/bin/python3

"""
Script for reading Data Lake CSV file from Ivy.ai

"His palms are sweaty, this is Scott's spaghetti."
Scott Kirian-Cressey
https://github.com/kirian-cressey
skirian@bgsu.edu


Script assumes .csv file exported from Ivy.ai with following filters:
Chat Start Time, Chat Length, Messages to Bot, Bot Responses (Generative),
Bot Responses (Retrieval), Bot Responses (Low Confidence),
Bot Responses (No Confidence), Attempt to Connect to Live Person,
Connection Established, Conversation Rating
NOTE: Data Lake export will include an additional column of data, Chat ID,
which is implicit in all exports and is not filterable.
"""

import sys
from utils import Utils

utils_instance = Utils()

utils_instance.read_report()

#Ask user for month and fical year. This avoids some errors with ivy's data
utils_instance.get_month()

#Let user inspect the data before writing to log
utils_instance.print_to_term()

#Ask if the data should be written
while True:
    print("\nWrite this data to log file?")
    
    response = input("Enter 'Y' to write or 'Q' to quit: ")

    if response == 'Y' or response == 'y':
        break
    elif response == 'Q' or response == 'q':
        sys.exit(0)
    else:
        print("Invalid input.\n")
        continue

#write the log file
utils_instance.print_to_file()

#be nice
print("Finished")
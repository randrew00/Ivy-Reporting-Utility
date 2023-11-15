# Script for reading Data Lake CSV file from Ivy.ai
# Script assumes .csv file exported from Ivy.ai with following filters:
# Chat Length, Messages to Bot, Bot Responses (Generative),
#   Bot Responses (Retrieval), Bot Responses (Low Confidence),
#   Bot Responses (No Confidence).

#!/usr/bin/env python3      #Run as Unix script

import csv

filename = input('Please enter the name of an Ivy Data Lake file:\n')

# Will need to ensure Data Lake CSV is filtered to contain only the fields 
# enumerated for fieldnames

with open(filename, newline='') as csvfile:

    log = csv.DictReader(csvfile, fieldnames= ("chat_id", "length",
        "user_messages", "bot_gen", "bot_retrieval", "bot_low_conf",
        "bot_no_conf"))
	
    total_chats = 0             #total number of unique chats
    total_gen = 0               #total generative responses
    total_retrieval = 0         #total retrieval responses
    total_low_conf = 0          #sum of num_low_conf
    total_no_conf = 0           #sum of num_no_conf
    total_user_messages = 0     #sum of user_messages
    zero_time_chats = 0
    zero_message_chats = 0

    next(log)                #skip first row to remove column labels

    for chat in log:
        
        #DELETE ME
        print(chat["bot_retrieval"])
        
        #do not include data for chats with no length
        if not chat["length"]:
            zero_time_chats += 1
            continue
            
        #do not include data for chats with no message from the user
        if not chat["user_messages"]:
            zero_message_chats += 1
            continue
            

        total_chats += 1
        
        if chat["user_messages"]:
            total_user_messages += int(chat["user_messages"])
        
        if chat["bot_gen"]:
            total_gen += int(chat["bot_gen"])
            
        if chat["bot_retrieval"]:
            total_retrieval += int(chat["bot_retrieval"])
            
        if chat["bot_low_conf"]:
            total_low_conf += int(chat["bot_low_conf"])
        
        if chat["bot_no_conf"]:
            total_no_conf += int(chat["bot_no_conf"])
            

    total_high_conf = total_user_messages - total_no_conf - total_no_conf

    print("Filtered chats with zero seconds: ", zero_time_chats)
    print("Filtered chats with no user interaction: ", zero_message_chats)
    print("Total unique chats served: ", total_chats)
    print("Total messages from users: ", total_user_messages)
    print("Total high confidence responses: ", total_high_conf)
    print("Total low confidence responses: ", total_low_conf)
    print("Total no confidence responses: ", total_no_conf)
    print("Total low/no confidence responses: ", total_low_conf + total_no_conf)
    print("Generative responses + retrieval responses: ",
        total_gen + total_retrieval)
    print("High confidence response rate: ",
        (total_high_conf / total_chats)*100, "%")

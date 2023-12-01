#!/usr/local/bin/python3

# Script for reading Data Lake CSV file from Ivy.ai
# Script assumes .csv file exported from Ivy.ai with following filters:
# Chat Length, Messages to Bot, Bot Responses (Generative),
#   Bot Responses (Retrieval), Bot Responses (Low Confidence),
#   Bot Responses (No Confidence).

import csv

class Report:
    
    total_chats = 0             #total number of unique chats
    total_gen = 0               #total generative responses
    total_retrieval = 0         #total retrieval responses
    total_high_conf = 0
    total_low_conf = 0          #sum of num_low_conf
    total_no_conf = 0           #sum of num_no_conf
    total_user_messages = 0     #sum of user_messages
    zero_time_chats = 0         #filter out non-real chats based on time
    zero_message_chats = 0      #filter out non-real chats based on interaction
    
def read_report():

    valid_filename = False      #loop condition to get valid filename
    report = Report()

    while valid_filename == False:

        try:
            filename = input('Please enter the name of an Ivy Data Lake file:\n')
            
            if filename == 'quit' or filename == 'q' or filename == 'Quit':
                break

            #Fragile: Ensure CSV contains only fields enumerated for fieldnames
            #Else, garbage in garbage out.
            csvfile = open(filename, newline='')
            #FIXME DELETE
            print("Opened file")
            
            log = csv.DictReader(csvfile, fieldnames= ("chat_id", "length",
                    "user_messages", "bot_gen", "bot_retrieval", "bot_low_conf",
                    "bot_no_conf"))
        
            valid_filename = True
            next(log)                #skip first row containing column labels

            #parse file data
            for chat in log:
                    
                #FIXME commented out for clarity at the moment:
                #do not include data for chats with no length
                #if not chat["length"]:
                #    zero_time_chats += 1
                #    continue
                    
                #FIXME commented out for clarity at the moment:
                #do not include data for chats with no message from the user
                #    if not chat["user_messages"]:
                #        reports.zero_message_chats += 1
                #        continue
                

                #do not count chats filtered from above against total
                report.total_chats += 1
        
                if chat["user_messages"]:
                    report.total_user_messages += int(chat["user_messages"])
        
                if chat["bot_gen"]:
                    report.total_gen += int(chat["bot_gen"])
            
                if chat["bot_retrieval"]:
                    report.total_retrieval += int(chat["bot_retrieval"])
            
                if chat["bot_low_conf"]:
                    report.total_low_conf += int(chat["bot_low_conf"])
        
                if chat["bot_no_conf"]:
                    report.total_no_conf += int(chat["bot_no_conf"])
        
            csvfile.close()
            
            #FIXME Move this under the printer function. Keep reader strictly read
            #report.total_high_conf = report.total_gen + report.total_retrieval

            
        except:
            print("\nInvalid filename.")
            print("Enter filename or type 'quit'.\n")
            continue

    if valid_filename == False:
        raise SystemExit(0)
        
    return report

report = read_report()

#print("Filtered chats with zero seconds: ", zero_time_chats)
#print("Filtered chats with no user interaction: ", zero_message_chats)
print("Total unique chats served: ", report.total_chats)
print("Total messages from users: ", report.total_user_messages)
print("Total generative responses: ", report.total_gen)
print("Total retrieval responses: ", report.total_retrieval)
print("Total low confidence responses: ", report.total_low_conf)
print("Total no confidence responses: ", report.total_no_conf)
print("Total high confidence responses: ", report.total_high_conf)
      
if report.total_chats:                                #avoid div by 0
    print("High confidence response rate: ",
        (report.total_high_conf / report.total_chats)*100, "%")

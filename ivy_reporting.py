#!/usr/local/bin/python3

# Script for reading Data Lake CSV file from Ivy.ai
# Script assumes .csv file exported from Ivy.ai with following filters:
# Chat Length, Messages to Bot, Bot Responses (Generative),
#   Bot Responses (Retrieval), Bot Responses (Low Confidence),
#   Bot Responses (No Confidence).

import csv


class Report:
    
    #raw data attributes present in Data Lake csv file
    total_chats = 0             #total number of unique chats
    total_gen = 0               #total generative responses
    total_retrieval = 0         #total retrieval responses
    total_low_conf = 0          #sum of num_low_conf
    total_no_conf = 0           #sum of num_no_conf
    total_user_messages = 0     #sum of user_messages
    
    #derived attrubutes
    total_high_conf = 0
    zero_time_chats = 0         #filter out non-real chats based on time
    zero_message_chats = 0      #filter out non-real chats based on interaction
    
    def debug_print(self):
        """Method to print raw data summary being read into report"""

        print("Total chats = ", self.total_chats)
        print("Total messages to bot = ", self.total_user_messages)
        print("Total generative = ", self.total_gen)
        print("Total retrieval = ", self.total_retrieval)
        print("Total low confidence responses = ", self.total_low_conf)
        print("Total no confidence responses = ", self.total_no_conf)


def read_report():

    valid_filename = False      #loop condition to get valid filename
    report = Report()

    while valid_filename == False:

        try:
            filename = input('Please enter the name of an Ivy Data Lake file:\n')
            if filename == 'quit' or filename == 'q' or filename == 'Quit':
                break

            csvfile = open(filename, newline='')
            log = csv.DictReader(csvfile, fieldnames= ("chat_id", "length",
                    "user_messages", "bot_gen", "bot_retrieval", "bot_low_conf",
                    "bot_no_conf"))
        
            valid_filename = True       #if file is open, filename is valid
            next(log)                   #skip first row containing column label

            #parse file data
            for chat in log:
                    
                #FIXME: uncomment to filter out chats based on length
                #do not include data for chats shorter than ???
                #if not chat["length"]:
                #    zero_time_chats += 1
                #    continue
                    
                #FIXME: uncomment to filter chats based on number of messages
                #do not include data for chats with less than ??? messages
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

            
        except:
            print("\nInvalid filename.")
            print("Enter filename or type 'quit'.\n")
            continue

    if valid_filename == False:
        raise SystemExit(0)
        
    return report


def print_to_term(report):
    
    #report.total_high_conf = report.total_gen + report.total_retrieval

    #print("Filtered chats with zero seconds: ", zero_time_chats)
    #print("Filtered chats with no user interaction: ", zero_message_chats)
    print("Total unique chats served: ", report.total_chats)
    print("Total messages from users: ", report.total_user_messages)
    print("Total generative responses: ", report.total_gen)
    print("Total retrieval responses: ", report.total_retrieval)
    print("Total low confidence responses: ", report.total_low_conf)
    print("Total no confidence responses: ", report.total_no_conf)
    #print("Total high confidence responses: ", report.total_high_conf)
      
    #if report.total_chats:                                #avoid div by 0
    #    print("High confidence response rate: ",
    #        (report.total_high_conf / report.total_chats)*100, "%")


#def print_to_file(report):
    """Coming soon to a theatre near you"""


print_to_term(read_report())

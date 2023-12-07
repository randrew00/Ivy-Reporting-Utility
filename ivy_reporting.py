#!/usr/local/bin/python3

#His palms are sweaty, this is Scott's spaghetti.

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
    
    #calculated attrubutes
    total_high_conf = 0         #total_retrival + total_gen
    total_chats_fired = 0       #retrieval + gen + low + no
    chats_with_high_conf = 0    #chats which fired a high confidence response
    accuracy_rate = 0           #total_high_conf / total_user_messages
    resolution_rate = 0         #total_high_conf / total_chats
    zero_time_chats = 0         #filter out non-real chats based on time
    zero_message_chats = 0      #filter out non-real chats based on interaction
    
    
    def calculate_attributes(self):
        self.total_high_conf = self.total_gen + self.total_retrieval
        self.total_chats_fired = self.total_gen + self.total_retrieval \
            + self.total_low_conf + self.total_no_conf
        self.accuracy_rate = self.total_high_conf / self.total_chats


    def debug_print(self):
        """Method to print raw data summary being read into report"""

        print("Total chats = ", self.total_chats)
        print("Total messages to bot = ", self.total_user_messages)
        print("Total generative = ", self.total_gen)
        print("Total retrieval = ", self.total_retrieval)
        print("Total low confidence responses = ", self.total_low_conf)
        print("Total no confidence responses = ", self.total_no_conf)


    def print_to_term(self):
        
        #print("Filtered chats with zero seconds: ", zero_time_chats)
        #print("Filtered chats with no user interaction: ", zero_message_chats)
        print("Total unique chats served: ", self.total_chats)
        print("Chats with a high confidence response: ",
            self.chats_with_high_conf)
        print("Total messages from users: ", self.total_user_messages)
        print("Total generative responses: ", self.total_gen)
        print("Total retrieval responses: ", self.total_retrieval)
        print("Total low confidence responses: ", self.total_low_conf)
        print("Total no confidence responses: ", self.total_no_conf)
        if self.total_chats:          #avoid div by 0
            print("Accuracy rate: ",
                (self.total_high_conf / self.total_chats)*100, "%")
        if self.total_chats:          #avoid div by 0
            print("Resolution rate: ",
                self.chats_with_high_conf / self.total_chats)


#FIXME: Will return to print-to-file. Set aside until fundamentals complete
"""
    def print_to_file(self):
        
        bot_report = open('ivy_log.csv', 'a')
        
        bot_report.write(report_header + "\n")
        bot_report.write("Total chats: ")
        bot_report.write(str(self.total_chats))
        
        
        #Seperate months with double newline and close file
        bot_report.write("\n\n")
        bot_report.close()
"""


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
                    
                """
                #Comment out this block to compare raw data with Ivy
                #do not include data for chats with no time
                if not chat["length"]:
                    zero_time_chats += 1
                    continue
                    
                #Comment out this block to compare raw data with Ivy
                #do not include data for chats with zero messages
                    if not chat["user_messages"]:
                        reports.zero_message_chats += 1
                        continue
                """

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
                    
                if chat["bot_gen"] or chat["bot_retrieval"]:
                    report.chats_with_high_conf += 1
        
            csvfile.close()

            
        except:
            print("\nInvalid filename.")
            print("Enter filename or type 'quit'.\n")
            continue

    if valid_filename == False:
        raise SystemExit(0)
        
    #report read complete. now get derived attibutes
    report.calculate_attributes()
    
    return report


monthly_report = read_report()

monthly_report.print_to_term()
#print_to_file(monthly_report)

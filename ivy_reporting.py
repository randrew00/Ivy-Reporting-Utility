#!/usr/local/bin/python3

#His palms are sweaty, this is Scott's spaghetti.

#default to use Data Lake filter for Nov 13 - 19

#Script for reading Data Lake CSV file from Ivy.ai

#Script assumes .csv file exported from Ivy.ai with following filters:
#Chat Start Time, Chat Length, Messages to Bot, Bot Responses (Generative),
#Bot Responses (Retrieval), Bot Responses (Low Confidence),
#Bot Responses (No Confidence), Attempt to Connect to Live Person,
#Connection Established, Conversation Rating
#NOTE: Data Lake export will include an additional column of data, Chat ID,
#which is implicit in all exports and is not filterable.

import csv
import calendar             #https://docs.python.org/3/library/calendar.html
import string
import sys

#Service Desk hours in minutes of the day
weekend_open = 660          #11:00am
weekend_close = 1020        #5:00pm
weekday_open = 450          #7:30am
weekday_close = 1320        #10:00pm
months = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5,
    'June': 6, 'July': 7, 'August': 8, 'September': 9, 'October': 10,
    'November': 11, 'December': 12}

class Report:
    
    #raw data attributes present in Data Lake csv file
    total_user_messages = 0     #sum Messages to Bot
    total_gen = 0               #sum Bot Responses (Generative)
    total_retrieval = 0         #sum Bot Responses (Retrieval)
    total_low_conf = 0          #sum Bot Responses (Low Confidence)
    total_no_conf = 0           #sum Bot Responses (No Confidence)
    total_live_request = 0      #sum requests for live chat
    total_live_connect = 0      #sum successful connections to live agent
    
    ah_messages = 0             #sum messages to bot after hours
    ah_gen = 0                  #sum generative responses after hours
    ah_retrieval = 0            #sum retrieval after hours
    ah_low_conf = 0             #sum low confidence after hours
    ah_no_conf = 0              #sum no confidence after hours
    ah_live_request = 0         #sum requests for live chat after hours
    ah_live_connect = 0         #Note: in theory, this should be zero
    ah_resolved = 0             #sum chats with high conf. resp. after hours
    
    bh_messages = 0             #sum messages to bot during business hours
    bh_gen = 0                  #sum generative responses during business
    bh_retrieval = 0            #sum retrieval responses during business
    bh_low_conf = 0             #sum low confidence during business
    bh_no_conf = 0              #sum no confidence during business
    bh_live_request = 0         #sum requests for live chat during business
    bh_live_connect = 0         #sum successful connections during business
    bh_resolved = 0             #sum chats with high conf. resp during hours

    #calculated attrubutes
    filtered_chats = 0          #chats not counted in total: no time or message
    total_chats = 0             #total number of unique chats
    total_high_conf = 0         #total_retrival + total_gen
    total_responses = 0         #retrieval + gen + low + no
    resolved_chats = 0          #chats which fired a high confidence response
    accuracy_rate = 0           #total_high_conf / total_user_messages
    resolution_rate = 0         #resolved_chats / total_chats
    zero_time_chats = 0         #filter out non-real chats based on time
    zero_message_chats = 0      #filter out non-real chats based on interaction
    sum_ratings = 0
    num_ratings = 0

    
    #FIXME: WORKING HERE
    def calculate_attributes(self):
        self.total_user_messages = self.ah_messages + self.bh_messages
        self.total_gen = self.ah_gen + self.bh_gen
        self.total_retrieval = self.ah_retrieval + self.bh_retrieval
        self.total_high_conf = self.total_gen + self.total_retrieval
        self.total_low_conf = self.ah_low_conf + self.bh_low_conf
        self.total_no_conf = self.ah_no_conf + self.bh_no_conf
        self.total_responses = self.total_gen + self.total_retrieval \
            + self.total_low_conf + self.total_no_conf
        self.accuracy_rate = self.total_high_conf / self.total_chats
        self.resolved_chats = self.ah_resolved + self.bh_resolved
        self.resolution_rate = self.resolved_chats / self.total_chats

        if self.num_ratings:             #avoid div / 0
            self.average_rating = self.sum_ratings / self.num_ratings


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
            self.resolved_chats)
        print("Total messages from users: ", self.total_user_messages)
        print("Total generative responses: ", self.total_gen)
        print("Total retrieval responses: ", self.total_retrieval)
        print("Total low confidence responses: ", self.total_low_conf)
        print("Total no confidence responses: ", self.total_no_conf)
        if self.total_chats:          #avoid div by 0
            print("Accuracy rate: ",
                (self.total_high_conf / self.total_chats) * 100, "%")
        if self.total_chats:          #avoid div by 0
            print("Resolution rate: ",
                (self.resolved_chats / self.total_chats) * 100, "%")
        if self.average_rating:
            print("Average rating: ", self.average_rating, "/ 5")


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


def check_hours(start_time):
    """
    Assumes start_time is a string in the format "November 13, 2023 8:51 AM"
    and determine if this time is during Service Desk hours. Returns a Bool.
    Hours can be adjusted by changing weekday_open, weekday_close,
    weekend_open, weekend_close.
    """
    
    after_hours = False                 #will be returned

    #stripper will remove all punctuation listed on table at
    #string.punctuation when given as arg to str.translate(arg)
    stripper = str.maketrans('', '', string.punctuation)
    
    #apply stripper to start time and split on spaces
    date = start_time.translate(stripper).split()

    month = date[0]
    day = date[1]
    year = date[2]
    time = date[3]
    hour = int(int(time) / 100)     #get the hours in mil time
    minute = int(time) - (hour * 100)    #get the mins
    ampm = date[4]
    
    if (ampm == "PM") and (hour != 12):
        hour += 12
    if (ampm == "AM") and (hour == 12):
        hour += 12
        
    time_in_mins = (hour * 60) + minute #mins since yesterday
    month_abbr = months[month]
    
    #day_of_week: Monday = 0, Sunday = 6, etc.
    day_of_week = calendar.weekday(int(year), month_abbr, int(day))
    
    #determine if during or after hours
    if day_of_week <= 4:
        if (time_in_mins >= weekday_open) and \
            (time_in_mins <= weekday_close):
            after_hours = False
        else:
            after_hours = True
    elif day_of_week > 4:
        if (time_in_mins >= weekend_open) and \
            (time_in_mins <= weekend_close):
            after_hours = False
        else:
            after_hours = True
    else:
        #FIXME: Handle this better
        raise SystemExit(0)
    
    return after_hours


def read_report():

    report = Report()
    valid_filename = False      #loop condition to get valid filename

    #Get Data Lake file name from user
    while valid_filename == False:

        try:
            filename = input('Please enter the name of an Ivy Data Lake file:\n')
            if filename == 'quit' or filename == 'q' or filename == 'Quit':
                break
            
            csvfile = open(filename, newline='')
            
        except:
            print("\nInvalid filename. Enter filename or type 'quit'.\n")
            continue
            
        else:
            valid_filename = True
            print("Data Lake file opened successfully...\n")
    
    if valid_filename == False:
        sys.exit(0)

    log = csv.DictReader(csvfile, fieldnames= ("chat_id", "start_time",
    "length", "user_messages", "bot_gen", "bot_retrieval",
    "bot_low_conf", "bot_no_conf", "live_request", "live_connect",
    "rating"))
    
    next(log)                   #skip first row containing column label

    #parse file data
    for chat in log:
        
        """
        Comment out block below marked FILTER to turn off filtering.
        Note that chats with only of button clicks will show zero responses.
        At this time Data Lake does not provide any exposure to buttons.
        """
        
        #FILTER: do not include data for chats with no time or messages
        if not chat["length"] or not chat["user_messages"]:
            report.filtered_chats += 1
            continue
            
        #do not count chats filtered from above against total
        report.total_chats += 1
        
        #determine if chat was after hours
        after_hours = check_hours(chat["start_time"])
        
        if chat["user_messages"]:
            if after_hours:
                report.ah_messages += int(chat["user_messages"])
            else:
                report.bh_messages += int(chat["user_messages"])
        
        if chat["bot_gen"]:
            if after_hours:
                report.ah_gen += int(chat["bot_gen"])
            else:
                report.bh_gen += int(chat["bot_gen"])
    
        if chat["bot_retrieval"]:
            if after_hours:
                report.ah_retrieval += int(chat["bot_retrieval"])
            else:
                report.bh_retrieval += int(chat["bot_retrieval"])
        
        if chat["bot_gen"] or chat["bot_retrieval"]:
            if after_hours:
                report.ah_resolved += 1
            else:
                report.bh_resolved += 1

        if chat["bot_low_conf"]:
            if after_hours:
                report.ah_low_conf += int(chat["bot_low_conf"])
            else:
                report.bh_low_conf += int(chat["bot_low_conf"])
                

        if chat["bot_no_conf"]:
            if after_hours:
                report.ah_no_conf += int(chat["bot_no_conf"])
            else:
                report.bh_no_conf += int(chat["bot_no_conf"])

        if chat["live_request"]:
            if after_hours:
                report.ah_live_request += 1
            else:
                report.bh_live_request += 1

        if chat["live_connect"]:
            if after_hours:
                report.ah_live_connect += 1
            else:
                report.ah_live_connect += 1

        if chat["rating"]:
            report.sum_ratings += float(chat["rating"])
            report.num_ratings += 1
                    
    csvfile.close()
    
        
    #report read complete, now get derived attibutes
    report.calculate_attributes()
    if report.num_ratings:             #avoid div / 0
        report.average_rating = report.sum_ratings / report.num_ratings
    #FIXME: else what? How to handle months with no ratings?
    
    return report


monthly_report = read_report()
monthly_report.print_to_term()
#print_to_file(monthly_report)

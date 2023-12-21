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
    """
    A report object representing data from an ivy.ai Data Lake export.
    Report assumes a one-month period, but there is nothing stopping a user
    from using another unit of time. Period of time depends on the Data Lake
    file read in, and user will define this period of time (month, fiscal year)
    through input.
    """
    
    #get from user
    month = ''                  #i.e. 'October'
    fy = 0                      #fiscal year
    
    #raw data attributes present in Data Lake csv file
    total_user_messages = 0     #sum Messages to Bot
    total_gen = 0               #sum Bot Responses (Generative)
    total_retrieval = 0         #sum Bot Responses (Retrieval)
    total_low_conf = 0          #sum Bot Responses (Low Confidence)
    total_no_conf = 0           #sum Bot Responses (No Confidence)
    total_live_request = 0      #sum requests for live chat
    total_live_connect = 0      #sum successful connections to live agent
    
    ah_chats = 0                #unique chats after hours
    ah_messages = 0             #sum messages to bot after hours
    ah_gen = 0                  #sum generative responses after hours
    ah_retrieval = 0            #sum retrieval after hours
    ah_low_conf = 0             #sum low confidence after hours
    ah_no_conf = 0              #sum no confidence after hours
    ah_live_request = 0         #sum requests for live chat after hours
    ah_live_connect = 0         #Note: in theory, this should be zero
    ah_resolved = 0             #sum chats with high conf. resp. after hours
    ah_by_percent = 0.0         #percentage of chats occuring after hours
    
    bh_chats = 0
    bh_messages = 0             #unique chats during business hours
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
    time_filtered = 0           #chats filtered due to no time
    message_filtered = 0        #chats filtered due to no messages
    total_chats = 0             #total number of unique chats
    total_high_conf = 0         #total_retrival + total_gen
    total_responses = 0         #retrieval + gen + low + no
    resolved_chats = 0          #= >0 high conf. response + no live request
    accuracy_rate = 0           #total_high_conf / total_user_messages
    resolution_rate = 0         #resolved_chats / total_chats
    sum_ratings = 0             #sum of all ratings (meaningless on its own)
    num_ratings = 0             #total number of chats rated

    
    def calculate_attributes(self):
        self.total_chats = self.ah_chats + self.bh_chats
        self.total_user_messages = self.ah_messages + self.bh_messages
        
        if not self.ah_gen:
            self.ah_gen = 0
        if not self.bh_gen:
            self.bh_gen = 0
        self.total_gen = int(self.ah_gen) + int(self.bh_gen)
        
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
        self.ah_by_percent=float(self.ah_chats) / float(self.total_chats)*100


    def get_month(self):
        
        month_ask = "Please enter the month of the report (ie. \"October\"): "
        self.month = input(month_ask)
        
        year_ask = "Please enter the fiscal year of the report: "
        self.fy = input(year_ask)

    def debug_print(self):
        """Method to print raw data summary being read into report"""

        print("Total chats = ", self.total_chats)
        print("Total messages to bot = ", self.total_user_messages)
        print("Total generative = ", self.total_gen)
        print("Total retrieval = ", self.total_retrieval)
        print("Total low confidence responses = ", self.total_low_conf)
        print("Total no confidence responses = ", self.total_no_conf)


    def print_to_term(self):
        
        print("\nNote: ", self.filtered_chats, \
            "chats were filtered from data.\n",\
            "     ", self.time_filtered, " chats had zero time\n",\
            "     ", self.message_filtered, " chats had zero messages\n\n")
        print("TOTALS")
        print("Chats served: ", self.total_chats)
        print("Chats with a high confidence response: ",
            self.resolved_chats)
        print("Messages from users: ", self.total_user_messages)
        print("Generative responses: ", self.total_gen)
        print("Retrieval responses: ", self.total_retrieval)
        print("Low confidence responses: ", self.total_low_conf)
        print("No confidence responses: ", self.total_no_conf)
        if self.total_chats:          #avoid div by 0
            print("Accuracy rate: ",
                (self.total_high_conf / self.total_chats) * 100, "%")
        if self.total_chats:          #avoid div by 0
            print("Resolution rate: ",
                (self.resolved_chats / self.total_chats) * 100, "%")
        if self.average_rating:
            print("Average rating: ", self.average_rating, "/ 5")
        print("Requests for live agents: ", \
            self.ah_live_request + self.bh_live_request)
        print("Chats connected with live agent: ", \
            self.ah_live_connect + self.bh_live_connect)
        print("\nAFTER HOURS")
        print("Chats after hours: ", self.ah_chats)
        print("Percentage of chats occuring after hours: ",\
              self.ah_by_percent)
        print("Resolved chats after hours: ", self.ah_resolved)
        print("Low or no confidence response after hours: ", \
            self.ah_low_conf + self.ah_no_conf)
        print("Live agent requests after hours: ", self.ah_live_request)


    def print_to_file(self):
        """
        Print monthly reporting data to csv file. One line = one month.
        """
        
        bot_report = open('ivy_log.csv', 'a')
        
        bot_report.write('\n')              #start new month on new line
        
        #line template
        line = '{month},{year},{filtered},{notime},{nomess},{chats},{nummess}'
        line += '{genresp},{retresp},{lowresp},{noresp},{accuracy},{rez},{rating}'
        line += '{reqlive},{connlive},{ahchats},{percentah},{rezah},{live_req_ah}'
        
        #fill template
        bot_report.write(line.format(\
            month=self.month,\
            year=self.fy,\
            filtered=self.filtered_chats,\
            notime=self.time_filtered,\
            nomess=self.message_filtered,\
            chats=self.total_chats,\
            nummess=self.total_user_messages,\
            genresp=self.total_gen,\
            retresp=self.total_retrieval,\
            lowresp=self.total_low_conf,\
            noresp=self.total_no_conf,\
            accuracy=self.accuracy_rate,\
            rez=self.resolution_rate,\
            rating=self.average_rating,\
            reqlive=self.total_live_request,\
            connlive=self.total_live_connect,\
            ahchats=self.ah_chats,\
            percentah=self.ah_by_percent,\
            rezah=self.ah_resolved,\
            live_req_ah=self.ah_live_request
            ))
            
        print("Write complete. Closing log file.")
        bot_report.close()


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
            if not chat["length"]:
                report.time_filtered +=1
            if not chat["user_messages"]:
                report.message_filtered += 1
            report.filtered_chats += 1
            continue
        
            
        #determine if chat was after hours
        after_hours = check_hours(chat["start_time"])
        
        #flags first of two conditions for "resolved chat"
        rez_flag = False
        
        #Read-in report attributes
        if after_hours:
            report.ah_chats += 1
        else:
            report.bh_chats += 1

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
            rez_flag = True

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

        if chat["live_request"] == 'Yes':
            if after_hours:
                report.ah_live_request += 1
            else:
                report.bh_live_request += 1
        elif chat["live_request"] == 'No' and rez_flag == True:
            if after_hours:
                report.ah_resolved += 1
            else:
                report.bh_resolved += 1

        if chat["live_connect"] == 'Yes':
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

#*************************DO THE THING****************************************

#read in a report object from a Data Lake .csv
monthly_report = read_report()

#Ask user for month and fical year. This avoids some errors with ivy's data
monthly_report.get_month()

#Let user inspect the data before writing to log
monthly_report.print_to_term()

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
monthly_report.print_to_file()

#be nice
print("Finished")

from report import Report
import calendar
import string
import csv
import sys

#Service Desk hours in minutes of the day
weekend_open = 660          #11:00am
weekend_close = 1020        #5:00pm
weekday_open = 450          #7:30am
weekday_close = 1320        #10:00pm
months = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5,
    'June': 6, 'July': 7, 'August': 8, 'September': 9, 'October': 10,
    'November': 11, 'December': 12}

report = Report()

class Utils:

    def get_month(self):
        
        month_ask = "Please enter the month of the report (ie. \"October\"): "
        self.month = input(month_ask)
        
        year_ask = "Please enter the fiscal year of the report: "
        self.fy = input(year_ask)
    
    def debug_print(self):
        """Method to print raw data summary being read into report"""

        print("Total chats = ", report.total_chats)
        print("Total messages to bot = ", report.total_user_messages)
        print("Total generative = ", report.total_gen)
        print("Total retrieval = ", report.total_retrieval)
        print("Total low confidence responses = ", report.total_low_conf)
        print("Total no confidence responses = ", report.total_no_conf)


    def print_to_term(self):
        
        print("\nNote: ", report.filtered_chats, \
            "chats were filtered from data.\n",\
            "     ", report.time_filtered, " chats had zero time\n",\
            "     ", report.message_filtered, " chats had zero messages\n\n")
        print("TOTALS")
        print("Chats served: ", report.total_chats)
        print("Chats with a high confidence response: ",
            report.resolved_chats)
        print("Messages from users: ", report.total_user_messages)
        print("Generative responses: ", report.total_gen)
        print("Retrieval responses: ", report.total_retrieval)
        print("Low confidence responses: ", report.total_low_conf)
        print("No confidence responses: ", report.total_no_conf)
        if report.total_chats:          #avoid div by 0
            print("Accuracy rate: ",
                (report.total_high_conf / report.total_chats) * 100, "%")
        if report.total_chats:          #avoid div by 0
            print("Resolution rate: ",
                (report.resolved_chats / report.total_chats) * 100, "%")
        if report.average_rating:
            print("Average rating: ", report.average_rating, "/ 5")
        print("Requests for live agents: ", \
            report.ah_live_request + report.bh_live_request)
        print("Chats connected with live agent: ", \
            report.ah_live_connect + report.bh_live_connect)
        print("\nAFTER HOURS")
        print("Chats after hours: ", report.ah_chats)
        print("Percentage of chats occuring after hours: ",\
              report.ah_by_percent)
        print("Resolved chats after hours: ", report.ah_resolved)
        print("Low or no confidence response after hours: ", \
            report.ah_low_conf + report.ah_no_conf)
        print("Live agent requests after hours: ", report.ah_live_request)


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
            filtered=report.filtered_chats,\
            notime=report.time_filtered,\
            nomess=report.message_filtered,\
            chats=report.total_chats,\
            nummess=report.total_user_messages,\
            genresp=report.total_gen,\
            retresp=report.total_retrieval,\
            lowresp=report.total_low_conf,\
            noresp=report.total_no_conf,\
            accuracy=report.accuracy_rate,\
            rez=report.resolution_rate,\
            rating=report.average_rating,\
            reqlive=report.total_live_request,\
            connlive=report.total_live_connect,\
            ahchats=report.ah_chats,\
            percentah=report.ah_by_percent,\
            rezah=report.ah_resolved,\
            live_req_ah=report.ah_live_request
            ))
            
        print("Write complete. Closing log file.")
        bot_report.close()

    def check_hours(self, start_time):
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
    
    def read_report(self):
        
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
            after_hours = self.check_hours(chat["start_time"])
            
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
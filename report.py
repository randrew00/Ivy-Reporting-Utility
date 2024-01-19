class Report:
    """
    A report object representing data from an ivy.ai Data Lake export.
    Report assumes a one-month period, but there is nothing stopping a user
    from using another unit of time. Period of time depends on the Data Lake
    file read in, and user will define this period of time (month, fiscal year)
    through input.
    """
    
    def __init__(self):#get from user
        self.month = ''                  #i.e. 'October'
        self.fy = 0                      #fiscal year
    
    #raw data attributes present in Data Lake csv file
        self.total_user_messages = 0     #sum Messages to Bot
        self.total_gen = 0               #sum Bot Responses (Generative)
        self.total_retrieval = 0         #sum Bot Responses (Retrieval)
        self.total_low_conf = 0          #sum Bot Responses (Low Confidence)
        self.total_no_conf = 0           #sum Bot Responses (No Confidence)
        self.total_live_request = 0      #sum requests for live chat
        self.total_live_connect = 0      #sum successful connections to live agent
    
        self.ah_chats = 0                #unique chats after hours
        self.ah_messages = 0             #sum messages to bot after hours
        self.ah_gen = 0                  #sum generative responses after hours
        self.ah_retrieval = 0            #sum retrieval after hours
        self.ah_low_conf = 0             #sum low confidence after hours
        self.ah_no_conf = 0              #sum no confidence after hours
        self.ah_live_request = 0         #sum requests for live chat after hours
        self.ah_live_connect = 0         #Note: in theory, this should be zero
        self.ah_resolved = 0             #sum chats with high conf. resp. after hours
        self.ah_by_percent = 0.0         #percentage of chats occuring after hours
    
        self.bh_chats = 0
        self.bh_messages = 0             #unique chats during business hours
        self.bh_gen = 0                  #sum generative responses during business
        self.bh_retrieval = 0            #sum retrieval responses during business
        self.bh_low_conf = 0             #sum low confidence during business
        self.bh_no_conf = 0              #sum no confidence during business
        self.bh_live_request = 0         #sum requests for live chat during business
        self.bh_live_connect = 0         #sum successful connections during business
        self.bh_resolved = 0             #sum chats with high conf. resp during hours

    #calculated attrubutes
        self.filtered_chats = 0          #chats not counted in total: no time or message
        self.time_filtered = 0           #chats filtered due to no time
        self.message_filtered = 0        #chats filtered due to no messages
        self.total_chats = 0             #total number of unique chats
        self.total_high_conf = 0         #total_retrival + total_gen
        self.total_responses = 0         #retrieval + gen + low + no
        self.resolved_chats = 0          #= >0 high conf. response + no live request
        self.accuracy_rate = 0           #total_high_conf / total_user_messages
        self.resolution_rate = 0         #resolved_chats / total_chats
        self.sum_ratings = 0             #sum of all ratings (meaningless on its own)
        self.num_ratings = 0             #total number of chats rated
        self.average_rating = 0

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
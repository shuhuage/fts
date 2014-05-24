
import datetime
from bs4 import BeautifulSoup
import urllib2
import sys, traceback, getopt
import re


#**********************************
#Exception classes
#**********************************

class Error(Exception): """Base class for exceptions in this module."""; pass

class DateNotAvailableError(Error): pass

class DbConnectionError(Error): pass

class DictValueError(Error): pass

class ParamError(Error):

    def __init__(self,param):
        self.value = ('"' + param + '"' + " is not a valid argument.  param should be an integer preceded or not by " + '"' + "r" + '"')
    def __str__(self):
        return self.value
    
class WatchlistParamError(Error):
    
    def __init__(self,watchlist):
        self.value = ('"' + watchlist + '"' + " is not a valid argument for watchlist. Use either True or False (default)")
    def __str__(self):
        return self.value

class DayRangeError(Error):
    
    def __init__(self):
        self.value = ("Please choose a range between 1 and 5 days")
    def __str__(self):
        return self.value


        




#**********************************
#Main class
#**********************************

class Earnings():
    '''
    Handles web scraping, db calls and printing methods related to
    getting earnings data
    public methods are
        - print(day from _today or range of days from _today, all companies (default) 
        or watched items only): prints earnings data
        - addwatched(company name): add new company to watched list
        - getwatched(): print list of wahtched companies

    '''
    
    def __init__(self):
        #store earnings data into a self.earningsdata list object
        self._today = datetime.date.today()
        self.earnings_data = []
        
        
    def __del__(self):
        self.earnings_data = []

    def _get_page(self):   #function that returns contents of yahoo earnings web page

        self._url = "http://biz.yahoo.com/research/earncal/"+self._date_earnings.strftime("%Y%m%d")+".html"
        req = urllib2.Request(self._url)
        response = urllib2.urlopen(req)
        return response.read()




    def _get_soup_data(self):
        
        #obtains earnings data from yahoo earnings and
        #store that data into the yahoo_e database
        self.symbol_ticker = []
        self.earnings_data = []
        self.symbol_before_open = []
        
        try:
            soup = BeautifulSoup(self._get_page())
        except:
            return
            #raise DateNotAvailableError, "there are no earnings data available for " + str(self._date_earnings)

        #print(soup.prettify())
                
        self.soup_table = soup('table')[6]

        i = 2
        tp_index = 0
        while self.soup_table('tr')[i].next_sibling != None: #skipping first row of data, i.e data_table headings
            try:
                company_name = self.soup_table('tr')[i].td.string
                tp_index += 1
                if tp_index > 100:
                    break
            except:
                company_name = "N.A."
            try:
                symbol_ticker = self.soup_table('tr')[i].a.string
            except:
                symbol_ticker = "N.A."
            try:
                before_after = self.soup_table('tr')[i].small.string
                if before_after == None:
                    before_after = "N.A."
            except:
                before_after = "N.A."
            if symbol_ticker.isalpha() and not symbol_ticker.__contains__("."):
                self.earnings_data.append(((company_name),(symbol_ticker),(before_after),(self._today),(self._date_earnings)))
                 
                if before_after.__eq__("Before Market Open"):
                    self.symbol_before_open.append((symbol_ticker))
 
                self.symbol_ticker.append((symbol_ticker))
            
            i += 1
    
        return self.earnings_data
               

    def get_symbols(self,daynum):
        
        self._date_earnings = self._today + datetime.timedelta(daynum)
        self.symbol_ticker = []
        
        
        if self._date_earnings >= self._today:
 
            # retrieve data from yahoo! earnings webpage and store in db        
            self._get_soup_data()
       
        return self.symbol_ticker
    
    def _pretty_print(self, option):

 
        datainfo = {"earnings":(('Name','Ticker','When','Date Earnings','Date Added'),self.earnings_data),
                    }


        if option not in datainfo:
            raise KeyError, str(option) + " is not a key value in prettyprint"
        
        header = datainfo[option][0]
        
        
        #statement below generates a tuple of nbers from 0 to header.len()
        collist = tuple([i for i in range(header.__len__() + 1)])
        
        #this allows the colwidth dict to adjust to nber of columns in colnames
        colwidth = dict(zip(collist,(len(str(x)) for x in header)))
        
        for x in datainfo[option][1]:
            colwidth.update(( i, max(colwidth[i],len(str(el))) ) for i,el in enumerate(x))
        
        #widthpattern yields this format: %-10s ie 10 spaces after word 
        widthpattern = ' | '.join('%%-%ss' % colwidth[i] for i in xrange(0,5))
        
        #mapping successive row patterns to withpattern and printing results
        print '\n'.join((widthpattern % header,
                         '-|-'.join( colwidth[i]*'-' for i in xrange(5)),
                         '\n'.join(widthpattern % collist for collist in datainfo[option][1])))






       
    def _print_day(self,daynum,watchlist=False):
        
        self._date_earnings = self._today + datetime.timedelta(daynum)
        
        
        if self.isRefresh == True and self._date_earnings >= self._today:
 
            # retrieve data from yahoo! earnings webpage and store in db        
            self._get_soup_data()
       

            self._pretty_print("earnings")



    def print_earnings(self,days=0,isRange=False,isRefresh=True):
        '''
        retrieves and prints earnings data.
        
        the following args can be provided:
        
        - 'param' (default = 0):
            param can take two forms:
                - a day,e.g. param=1, for tomorrow's date
                - a isRange of days, in which case the number must be preceded
                by 'r', e.g. r3 (for a three days isRange from tomorrow)
            Note if param is a isRange, it returns always at least the current day's earnings
            Note param defaults to 0, i.e. todays earnings date
        
        - 'watchlist':
            = False (default) : shows companies included in watchlist followed by those companies not included in the
            watchlist
            = True : shows those companies included in watchlist only
        '''

        self.isRefresh = isRefresh
        
        #depending on value of isRange, days will be a number referring either to a single day
        #or a isRange of days
        dayslist = []
        if isRange == True:
            if days > 5 or days < 1:
                raise DayRangeError
            x = 1
            while x < days+1:
                dayslist.append(x)
                x+=1

        else:
            dayslist.append(days)

        
        #days to print
        print 'About to process the following days: ' + str(dayslist)
        for daynum in dayslist:
            self._print_day(daynum)
            
            
    def add_to_watchlist(self, name):
        pass


    

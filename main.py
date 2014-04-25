import urllib.request
import xml.etree.ElementTree as etree
import configparser
import time
import datetime
import textwrap

class Terminal_Weather(object):
    def __init__(self):
        self.config = self.read_config('config.ini')
        self.line_count = self.config['INFO']['LINE']
        self.data = self.weather_data(self.config['INFO']['WOEID'], self.config['INFO']['UNITS'])
        
        self.todays_message = self.todays_message()

        self.forecast = self.forecast()

        self.draw_menu(self.todays_message, self.forecast)
        
    def weather_data(self, woeid, unit):
        url = 'http://weather.yahooapis.com/forecastrss?w=' + str(woeid) + '&u=' + unit
        #print(url)
        try:
            xmltext = (urllib.request.urlretrieve(url))
        except:
            print('Internet connection or WOEID is not valid')
        root = (etree.parse(xmltext[0])).getroot()
        
        data = dict()
        #Pull any useful information out of the xml
        try:
            for i in range(0, 4):
                data['day'+str(i)] = root[0][12][i+7].attrib
                #data['day'+str(i)]['conditions']= self.translate_code(data['day'+str(i)]['code'])
            data['language'] = root[0][3].text
            data['location'] = root[0][6].attrib
            data['units'] = root[0][7].attrib
            data['day0']['wind'] = root[0][8].attrib
            data['day0']['atmosphere'] = root[0][9].attrib
            data['day0']['astronomy'] = root[0][10].attrib
            data['day0']['current_conditions'] = root[0][12][5].attrib
            
            data['location_lat'] = root[0][12][1].text
            data['location_long'] = root[0][12][2].text
            data['yahoo_link'] = root[0][12][3].text
            data['pubDate'] = root[0][12][4].text
            
            #Get forecast data, today being day
            
        except IndexError as e:
            print("WOEID: " + str(woeid) + " Is not a valid WOEID")
            print(e)
        return data
    
    def fancy_print(self, message):
        lnc =  int(self.line_count) #How many characters you want the screen to be wide (Line Count)
        genline = lambda mes: print(' '*((lnc - len(mes) -1)//2) + mes + ' '*((lnc - len(mes) -1)//2)) #Centre text on screen based on lnc

        for i in textwrap.wrap(message, lnc - 5):
            genline(i)
        
    def draw_menu(self, message, forecast):
        lnc =  int(self.line_count)
        unit = self.data['units']
        
        #CURRENT CONDITIONS
        cur_temp = 'Current Temperature: ' + self.data['day0']['current_conditions']['temp'] + u'°' + unit['temperature']
        cur_high_low = "High: " + self.data['day0']['high'] + u'°' + unit['temperature'] + " " + "Low: " + self.data['day0']['low'] + u'°' + unit['temperature']
        
        #WIND VARIABLES
        windchill = int(self.data['day0']['wind']['chill'])
        windspeed = float(self.data['day0']['wind']['speed'])
        winddir = self.data['day0']['wind']['direction']
        master_line = cur_high_low + ' | ' + str(windspeed) + ' ' + unit['speed'] + ' ' + str(winddir) + u'°' + ' | ' + self.data['day0']['text']
        
        today = time.strftime('%A %B %d')
        
        cur_master = [today, cur_temp, master_line]
        
        ### Forecast
        Fdata = []
        #print(forecast[2])
        for i in range(0, len(forecast)):
            Fdata.append(str(forecast[i][0]) + ' ==  ' + ' High: ' + str(forecast[i][1]) + u'°' + unit['temperature']+ \
                         ' Low: ' + str(forecast[i][2]) + u'°' + unit['temperature'] +"  " + str(forecast[i][3]) + '\n') 
        
        ## Draw screen
        
        print('='*lnc) # 63 characters long

        for i in cur_master:
            self.fancy_print(i)
            print('')
            
        for i in Fdata:
            self.fancy_print(i)

        print('='*lnc)
    
    def forecast(self):
        hold = []
        for num in range(1, 4):
            day = datetime.date.today() + datetime.timedelta(days=num)
            hold.append((day.strftime('%A'), self.data['day'+str(num)]['high'], self.data['day'+str(num)]['low'], self.data['day'+str(num)]['text']))
        return hold
    
    def todays_message(self): #Generate small message to summarize weather (mostly based on tempurature and windspeed)
        windchill = int(self.data['day0']['wind']['chill'])
        windspeed = float(self.data['day0']['wind']['speed'])
        high = int(self.data['day0']['high'])
        low = int(self.data['day0']['low'])
        #conditions = day0['text']
        message = []

        b = lambda x, a, b: True if x > a and x <= b else False # b = Between
        scarf = True if windspeed > 15 and low <= 0 else False  #Check if it's cold and windy
        ## Starting statement about weather
        if low < -20 or windchill < -20:
            if scarf:
                message.append("It's extremely cold, You will need a good jacket and a scarf.")
            else:
                message.append("It's extremely cold, You will need to wear a jacket and maybe a scarf.")   
        elif b(low, -20, 0) or b(windchill, -20, 0):
            if scarf:
                message.append("It's pretty cold, You'll need a good jacket and a scarf.")
            else:
                message.append("It's pretty cold, You'll need a good jacket.")
        elif b(low, 0, 15) or b(windchill, 0, 15):
            message.append("It's cool, You'll need a light jacket.")
        elif b(low, 15, 25) or b(windchill, 15, 25):
            message.append("It's pretty warm, you'll survive in a t-Shirt.")
        elif low > 25 or windchill > 25:
            message.append("It's pretty hot, wear something light.")  
        
        ## Check if there's a large difference in high/low
        if abs(high) - abs(low) > 10:
            message.append(" You may also want to dress in layers.")
        messStr = ''.join(message)
        
        return str(messStr)
    
    def read_config(self, file):
        config = configparser.ConfigParser()
        config.read(file)
        return config
    
Terminal_Weather()

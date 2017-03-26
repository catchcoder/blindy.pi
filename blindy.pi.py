from bs4 import BeautifulSoup
import requests
import os
import subprocess
from fake_useragent import UserAgent
ua = UserAgent()
ua.update()

# use random browser
headers = ua.random

#import RPi.GPIO as GPIO

btn1 =23
next = 0
#GPIO.setwarnings(False) 

#GPIO.setmode(GPIO.BCM)
#GPIO.setup(led1, GPIO.OUT)
#GPIO.setup(btn, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

soup = ""
channels = []
whatson = ""

#Url to read
url = 'http://blindy.tv'

# If payload required
#payload = {
#    'q': 'Python',
#}

def loadpage():
    global soup
    r = requests.get(url, headers) #
    soup = BeautifulSoup(r.text, "html.parser")

def getchannels():
    global channels
    global soup
    table = soup.find("table")
    for row in table.findAll("tr"):
        cells = row.findAll("td")
        if len(cells) == 3:
            channels.append( (cells[2].find('a').get('href') ))
            print (cells[1].text)

def getallhrefs():
    titles = soup.findAll('a', href=True)
    for t in titles:
        if 'm3u' in t['href']:
            print(t['href'])
            print (t.string)

def waitforbutton():
    global next
    global channels
    print ("playing ", channels[next])
    while True:
        testVar = raw_input("\nPress enter for next track or press q + enter to quit.")
        if testVar == "q":
            break
        if next == (len(channels)-1):
            next = 0
        else:
            next += 1
        print ("playing ", channels[next])
            
        #if GPIO.input(btn1) == True:
        

loadpage()

getchannels()

waitforbutton()






        

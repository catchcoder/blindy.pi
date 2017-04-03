from bs4 import BeautifulSoup
import time
import requests
import os
import subprocess
# import vlc
from fake_useragent import UserAgent
ua = UserAgent()
ua.update()

# use random browser
headers = ua.random

start_time = time.time()
import RPi.GPIO as GPIO

btn1 = 23 # next channel
btn2 = 14 # stop
btn3 = 25 # turn off blindy pi radio
btn4 = 12 # volume up
btn5 = 16 # volume down
next = 0

GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)
# GPIO.setup(led1, GPIO.OUT)
GPIO.setup(btn1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(btn2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(btn3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(btn4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(btn5, GPIO.IN, pull_up_down=GPIO.PUD_UP)


soup = ""
channels = []
whatson = ""
channelname = ""
firstrun = True
# Url to read
url = 'http://blindy.tv'
url2 = 'http://www.radiofeeds.co.uk/mp3.asp'
# If payload required
# payload = {
#    'q': 'Python',
# }


def loadpage():
    global start_time
    global firstrun
    global soup
    # add time delay to stop dos on blindy.tv website, it will update the
    # channels array only every 1 minute
    if (int((time.time() - start_time)) <= 60 and firstrun == False):
        return
    start_time = time.time()
    firstrun = False
    r = requests.get(url,headers)
    soup = BeautifulSoup(r.text, "html.parser")


def getchannels():
    global channels
    global soup
    table = soup.find("table")
    for row in table.findAll("tr"):
        cells = row.findAll("td")
        if len(cells) == 3:
            channels.append((cells[2].find('a').get('href')))


def getplaying(playing):
    loadpage()
    global whatson
    global channelname
    table = soup.find("table")
    for row in table.findAll("tr"):
        cells = row.findAll("td")
        if len(cells) == 3:
            if (cells[2].find('a').get('href')) == playing:
                whatson = (cells[1].text)
                channelname = (cells[0].text)
                return (cells[1].text)


def getallhrefs():
    titles = soup.findAll('a', href=True)
    for t in titles:
        if 'm3u' in t['href']:
            print(t['href'])
            print(t.string)


def waitforbutton():
    global next
    global channels
    global weblink

    while True:
        if GPIO.input(btn2) == False:
           speak("Blindy tv", "stopping")
           subprocess.call(['mpc', 'stop', '-q'])
 
        if GPIO.input(btn3) == False:
           speak("shutting down", "blindy tv pi")
           subprocess.call(['mpc', 'stop', '-q'])
 
        if GPIO.input(btn4) == False:
           speak("volume", "up")
           subprocess.call(['mpc', 'volume', '+1','-q'])
 
        if GPIO.input(btn5) == False:
           speak("volume", "down")
           subprocess.call(['mpc', 'volume','-1', '-q'])
 

        if GPIO.input(btn1) == False:
            #testVar = input(
            #    "\nPress enter for next track or press q + enter to quit.")
            #if testVar == "q":
            #subprocess.call(['mpc', 'stop', '-q'])

            #break
            if next == (len(channels) - 1):
                next = 0
            else:
                next += 1
            getplaying(channels[next])
            weblink = (channels[next])
            speakwhatson([channelname, whatson, weblink])
        # if GPIO.input(btn1) == True:


def speakwhatson(channelinfo=[]):
    speak("Channel:", channelname)
    speak("Playing:", whatson)
    play()


def speak(a, b):
    subprocess.call(['mpc', 'stop', '-q'])
    subprocess.call(['espeak', a, '2>/dev/null'])
    subprocess.call(['espeak', b, '2>/dev/null'], stderr=subprocess.STDOUT)


def play():
    subprocess.call(['mpc', 'clear', '-q'])
    subprocess.call(['mpc', 'load', weblink])
    p = subprocess.Popen(['mpc',
                          'play',
                          '-q'],
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)


def startup_play():
    global weblink
    getplaying(channels[0])
    weblink = (channels[0])
    speakwhatson([channelname, whatson, weblink])
   
loadpage()

getchannels()

startup_play()

waitforbutton()

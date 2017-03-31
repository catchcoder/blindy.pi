from bs4 import BeautifulSoup
import time
import requests
import os
import subprocess
import vlc
from fake_useragent import UserAgent
ua = UserAgent()
ua.update()

Instance = vlc.Instance()
player = Instance.media_player_new()
Media = ""

# use random browser
headers = ua.random

start_time = time.time()
# import RPi.GPIO as GPIO

btn1 = 23
next = 0
# GPIO.setwarnings(False)

# GPIO.setmode(GPIO.BCM)
# GPIO.setup(led1, GPIO.OUT)
# GPIO.setup(btn, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

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
    # add time delay to stop dos on blindy.tv website, it will update the channels array only every 1 minute
    if (int((time.time() - start_time)) <= 60 and firstrun == False):
        print ("less than 60 seconds")
        return
    print ("greater than 60 seconds")
    start_time = time.time()
    firstrun = False
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

def getchannels():
    global channels
    global soup
    table = soup.find("table")
    for row in table.findAll("tr"):
        cells = row.findAll("td")
        if len(cells) == 3:
            channels.append((cells[2].find('a').get('href')))
            # print (cells[1].text)

def getplaying(playing):
    loadpage()
    # global channels
    # global soup
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
            print (t.string)

def waitforbutton():
    global next
    global channels
    global weblink

    # print ("playing ", channels[next])
    while True:
        testVar = raw_input("\nPress enter for next track or press q + enter to quit.")
        if testVar == "q":
            # subprocess.call (['mpc','stop'],shell=True)
 
            # player.stop()
            break
        if next == (len(channels)-1):
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
    vlcplay()

def speak(a, b):

    pipe = subprocess.call(['espeak', a], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # pipe.wait()
    pipe = subprocess.call(['espeak', b], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #pipe.wait()
    # name = pipe.communicate()[0]
    # pipe.wait(timeout=120)
    # print (name)

def play():
    subprocess.call (['mpc','stop'],shell=True)
    subprocess.call (['mpc','clear'],shell=True)
    subprocess.call (['mpc','add',weblink],shell=True)
    pipe = subprocess.call(['mpc','play'],shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    name = pipe.communicate()[0]
    # pipe.wait(timeout=120)
    print (name)

def startup_play():
    global weblink
    getplaying(channels[0])
    weblink = (channels[0])
    speakwhatson([channelname, whatson, weblink])
    vlcplay()

def vlcplay():
	global Media
	global player
	Media = Instance.media_new(weblink)
	Media.get_mrl()
	player.set_media(Media)
	player.play()

loadpage()

getchannels()

startup_play()

waitforbutton()

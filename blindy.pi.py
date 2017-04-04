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
HEADERS = ua.random

START_TIME = time.time()
import RPi.GPIO as GPIO

BTN_1 = 23  # next channel
BTN_2 = 14  # stop
BTN_3 = 25  # turn off blindy pi radio
BTN_4 = 12  # volume up
BTN_5 = 16  # volume down
NEXT_STREAM = 0

GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)
# GPIO.setup(led1, GPIO.OUT)
GPIO.setup(BTN_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN_3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN_4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN_5, GPIO.IN, pull_up_down=GPIO.PUD_UP)


SOUP = ""
channels = []
WHATS_ON = ""
channelname = ""
firstrun = True
# URL to read
URL = 'http://blindy.tv'
URL2 = 'http://www.radiofeeds.co.uk/mp3.asp'
# If payload required
# payload = {
#    'q': 'Python',
# }


def loadpage():
    """" Get web page and parse wioth beatifulsoup """
    global START_TIME
    global firstrun
    global SOUP
    # add time delay to stop dos on blindy.tv website, it will update the
    # channels array only every 1 minute
    if int((time.time() - START_TIME)) <= 60 and firstrun == False:
        return
    START_TIME = time.time()
    firstrun = False
    r = requests.get(URL, HEADERS)
    SOUP = BeautifulSoup(r.text, "html.parser")


def getchannels():
    """" Search web page and load hrefs into channels array """
    global channels
    global SOUP
    table = SOUP.find("table")
    for row in table.findAll("tr"):
        cells = row.findAll("td")
        if len(cells) == 3:
            channels.append((cells[2].find('a').get('href')))


def getplaying(playing):
    """ Find whats playing online now"""
    loadpage()
    global WHATS_ON
    global channelname
    table = SOUP.find("table")
    for row in table.findAll("tr"):
        cells = row.findAll("td")
        if len(cells) == 3:
            if (cells[2].find('a').get('href')) == playing:
                WHATS_ON = (cells[1].text)
                channelname = (cells[0].text)
                return cells[1].text


def getallhrefs():
    """ Get all Hrefs with m3u in the tag """
    titles = SOUP.findAll('a', href=True)
    for t in titles:
        if 'm3u' in t['href']:
            print(t['href'])
            print(t.string)


def main():
    """ Main loop to check if and what button is pressed """
    global NEXT_STREAM
    global WEB_LINK

    while True:
        if GPIO.input(BTN_2) == False:
            speak("Blindy tv", "stopping")
            subprocess.call(['mpc', 'stop', '-q'])

        if GPIO.input(BTN_3) == False:
            speak("shutting down", "blindy tv pi")
            subprocess.call(['sudo', 'shutdown', '-t', 'now'])

        if GPIO.input(BTN_4) == False:
            speak("volume", "up")
            subprocess.call(['mpc', 'volume', '+1', '-q'])

        if GPIO.input(BTN_5) == False:
            speak("volume", "down")
            subprocess.call(['mpc', 'volume', '-1', '-q'])

        if GPIO.input(BTN_1) == False:
            # testVar = input(
            #    "\nPress enter for next track or press q + enter to quit.")
            # if testVar == "q":
            #subprocess.call(['mpc', 'stop', '-q'])

            # break
            NEXT_STREAM += 1
            if NEXT_STREAM == len(channels):
                NEXT_STREAM = 0

            getplaying(channels[NEXT_STREAM])
            WEB_LINK = (channels[NEXT_STREAM])
            speakwhatson([channelname, WHATS_ON, WEB_LINK])
        # if GPIO.input(BTN_1) == True:


def speakwhatson(channelinfo=[]):
    """ Speak using whats on and play stream """
    speak("Channel:", channelname)
    speak("Playing:", WHATS_ON)
    play()


def speak(a, b):
    """ Use espeak to say what the playing or what button was pressed """
    subprocess.call(['mpc', 'stop', '-q'])
    subprocess.call(['espeak', a, '2>/dev/null'])
    subprocess.call(['espeak', b, '2>/dev/null'], stderr=subprocess.STDOUT)


def play():
    """  Using MPC load new stream and play it """
    subprocess.call(['mpc', 'clear', '-q'])
    subprocess.call(['mpc', 'load', WEB_LINK])
    subprocess.Popen(['mpc',
                          'play',
                          '-q'],
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)


def startup_play():
    """ Start playing stream on startup """
    global WEB_LINK
    getplaying(channels[0])
    WEB_LINK = (channels[0])
    speakwhatson([channelname, WHATS_ON, WEB_LINK])


if __name__ == '__main__':
    """ Start up """
    loadpage()
    getchannels()
    startup_play()
    main()



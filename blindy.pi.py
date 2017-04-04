"""
Play Blindy.tv on a Raspberry PI
"""
from bs4 import BeautifulSoup
import time
import requests
import subprocess
# import vlc
from fake_useragent import UserAgent
UA = UserAgent()
UA.update()

# use random browser
HEADERS = UA.random

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
CHANNELS = []
WHATS_ON = ""
CHANNEL_NAME = ""
WEB_LINK = ""
FIRST_RUN = True
START_VOLUME = '70'
# URL to read
URL = 'http://blindy.tv'
URL2 = 'http://www.radiofeeds.co.uk/mp3.asp'


def loadpage():
    """" Get web page and parse wioth beatifulsoup """
    global START_TIME
    global FIRST_RUN
    global SOUP
    # add time delay to stop dos on blindy.tv website, it will update the
    # channels array only every 1 minute
    if int((time.time() - START_TIME)) <= 60 and FIRST_RUN == False:
        return
    START_TIME = time.time()
    FIRST_RUN = False
    req_page = requests.get(URL, HEADERS)
    SOUP = BeautifulSoup(req_page.text, "html.parser")


def getchannels():
    """" Search web page and load hrefs into channels array """
    table = SOUP.find("table")
    for row in table.findAll("tr"):
        cells = row.findAll("td")
        if len(cells) == 3:
            CHANNELS.append((cells[2].find('a').get('href')))


def getplaying(playing):
    """ Find whats playing online now"""
    loadpage()
    global WHATS_ON
    global CHANNEL_NAME
    table = SOUP.find("table")
    for row in table.findAll("tr"):
        cells = row.findAll("td")
        if len(cells) == 3:
            if (cells[2].find('a').get('href')) == playing:
                WHATS_ON = (cells[1].text)
                CHANNEL_NAME = (cells[0].text)
                return cells[1].text


def main():
    """ Main loop to check if and what button is pressed """

    while True:
        if GPIO.input(BTN_2) == False:
            speak("Blindy tv", "stopping")
            subprocess.call(['mpc', 'stop', '-q'])

        if GPIO.input(BTN_3) == False:
            speak("shutting down", "blindy tv pi")
            subprocess.call(['mpc', 'stop', '-q'])
            subprocess.call(['sudo', 'shutdown', '-t', 'now'])

        if GPIO.input(BTN_4) == False:
            speak("volume", "up")
            subprocess.call(['mpc', '-q', 'volume', '+5'])
            play()

        if GPIO.input(BTN_5) == False:
            speak("volume", "down")
            subprocess.call(['mpc', '-q', 'volume', '-5'])
            play()

        if GPIO.input(BTN_1) == False:
            global WEB_LINK
            global NEXT_STREAM
            NEXT_STREAM += 1
            # check if at end of list
            if NEXT_STREAM == len(CHANNELS):
                NEXT_STREAM = 0

            getplaying(CHANNELS[NEXT_STREAM])
            WEB_LINK = CHANNELS[NEXT_STREAM]
            speakwhatson()


def speakwhatson():
    """ Speak using whats on and play stream """
    speak("Channel:", CHANNEL_NAME)
    speak("Playing:", WHATS_ON)
    play()


def speak(speak_a, speak_b):
    """ Use espeak to say what the playing or what button was pressed """
    subprocess.call(['mpc', 'stop', '-q'])
    subprocess.call(['espeak', speak_a, '2>/dev/null'])
    subprocess.call(['espeak', speak_b, '2>/dev/null'],
                    stderr=subprocess.STDOUT)


def play():
    """  Using MPC load new stream and play it """
    subprocess.call(['mpc', 'clear', '-q'])
    subprocess.call(['mpc', 'load', WEB_LINK])
    subprocess.Popen(['mpc', 'play', '-q'], stdin=subprocess.PIPE,
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def startup_play():
    """ Start playing stream on startup """
    global WEB_LINK
    getplaying(CHANNELS[0])
    WEB_LINK = (CHANNELS[0])
    speakwhatson()


def set_startup_volume():
    """ Set defualt volume for mpc to START_VOLUME variable """
    subprocess.call(['mpc', '-q', 'volume', START_VOLUME])


if __name__ == '__main__':
    loadpage()
    getchannels()
    set_startup_volume()
    startup_play()
    main()

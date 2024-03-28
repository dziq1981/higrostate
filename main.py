import picozero
from dht import DHT22
from ssd1306 import SSD1306_I2C
from machine import Pin, I2C
from time import sleep, ticks_diff, ticks_ms
from constants import *
from settings import Settings, WorkType
from random import randrange

#methods go first

#sets the relay high if parameter is True or low otherwise 
#(may require some adjustments depending if the relay is activated by low or high signal)
#it also resets the timer for display, and sets relayState
#variable to a number reflecting assumed relay state
def setRelay(state : bool):
    global relay, relayState, displayTimer
    if state and relayState==0:
        relay.high()
        relayState=1
        displayTimer = float(DISPLAY_TIMER_DEFAULT)*10
    elif not state and relayState==1:
        relay.low()
        relayState=0
        displayTimer = float(DISPLAY_TIMER_DEFAULT)*10

def regularUpButtonPressReaction():
    global buttonTimer
    buttonTimer=ticks_ms()
    
def specialUpOnThresholdButtonPressReaction():
    global settings, oled, specialActionTimer
    print("special up")
    settings.onThreshold+=1
    oled.fill(0)
    oled.text("Prog wlaczenia:",1,5)
    oled.text("%3.1f" %settings.onThreshold,1,15)
    oled.show()
    specialActionTimer = 5.0

def specialDownOnThresholdButtonPressReaction():
    global settings, oled, specialActionTimer
    print("special down")
    settings.onThreshold-=1
    oled.fill(0)
    oled.text("Prog wlaczenia:",1,5)
    oled.text("%3.1f" %settings.onThreshold,1,15)
    oled.show()
    specialActionTimer = 5.0

def doNothing():
    pass

def regularUpButtonReleaseReaction():
    global buttonTimer, oled, displayTimer, specialActionInterval, specialActionTimer, buttonRed, buttonBlue
            
    oled.fill(0)
    oled.text("Prog wlaczenia:",1,5)
    oled.text("%3.1f" %settings.onThreshold,1,15)
    oled.show()
    #sleep(2)
    oled.fill(0)
    displayTimer = DISPLAY_TIMER_DEFAULT

    if ticks_diff(ticks_ms(),buttonTimer)>=1200:
        print("else")
        buttonRed.when_activated = specialUpOnThresholdButtonPressReaction
        buttonBlue.when_activated = specialDownOnThresholdButtonPressReaction
        buttonRed.when_deactivated = doNothing
        buttonBlue.when_deactivated = doNothing
        specialActionTimer=5.0
        print("elser")
        while specialActionTimer>=0:
            sleep(specialActionInterval)
            specialActionTimer-=specialActionInterval
            pass
        print("more elser")
        buttonRed.when_activated = regularUpButtonPressReaction
        buttonBlue.when_activated = doNothing
        buttonRed.when_deactivated = regularUpButtonReleaseReaction
        buttonBlue.when_deactivated = doNothing
#i/o devices setup
sensor = DHT22(Pin(SENSOR_PIN_NUMBER))
buttonRed = picozero.Button(BUTTON_RED_PIN_NUMBER)
buttonBlue = picozero.Button(BUTTON_BLUE_PIN_NUMBER)
buttonTimer = 0
specialActionTimer = 5.0
specialActionInterval=0.1
buttonRed.when_activated = regularUpButtonPressReaction
buttonRed.when_deactivated = regularUpButtonReleaseReaction

oled = SSD1306_I2C(OLED_WIDTH,OLED_HEIGHT,I2C(I2C_ID, scl=Pin(I2C_SCL_PIN_NUMBER), sda=Pin(I2C_SDA_PIN_NUMBER)))
#read or setup settings
settings = Settings(oled)
#setting up a relay
relay = Pin(RELAY_PIN_NUMBER, Pin.OUT, Pin.PULL_UP)
relay.high()
relayState=1
#display initialization message with a countdown
displayTimer=2
interval = 0.1
while displayTimer>=0: 
    oled.text("Uruchamiam",5,0)
    oled.text("sensor",5,10)
    oled.text("Zaczekaj %1.1fs" %displayTimer,5,20)
    oled.show()    
    oled.fill(0)
    displayTimer-=interval
    sleep(interval)

displayTimer = 30
interval = 2.0
#main loop
try:
    while True:
        sensor.measure()    
        hum = sensor.humidity()
        if settings.getWorkType()==WorkType.humidifier:
            if hum<settings.onThreshold:
                setRelay(False)                
            if hum>settings.offThreshold:
                setRelay(True)                
        else:
            if hum>settings.onThreshold:
                setRelay(False)                
            if hum<settings.offThreshold:
                setRelay(True)                
        if displayTimer>0.0: #displays humidity information for some time and at random locations to reduce oled screen wear
            buff : str = 'Rh= %3.1f %%' %hum        
            graphLen =  len(buff)*8+1
            x = randrange(0,120-graphLen,1)
            y = randrange(0,24,1)
            oled.ellipse(x+graphLen+4,y+4,3,3,1,relayState==0)
            oled.text(buff,x,y)            
        if displayTimer>-interval: #updates the screen and makes sure it stays black after the time interval had passed
            oled.show()
            oled.fill(0)        
            displayTimer-=interval                  
        sleep(interval)
except Exception as e:
    print(e.args)
    while True: #display a short blinking error message if something is wrong
        oled.text("Problem!",randrange(0,100,1),randrange(0,24))
        oled.show()
        sleep(1)
        oled.fill(0)
        oled.show()
        sleep(1)

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
        relay.off()
        relayState=1
        displayTimer = float(DISPLAY_TIMER_DEFAULT)*10
    elif not state and relayState==1:
        relay.on()
        relayState=0
        displayTimer = float(DISPLAY_TIMER_DEFAULT)*10

   
def specialUpOnThresholdButtonPressReaction():
    global settings, oled, actionTimer
    print("special up")
    settings.onThreshold+=1
    oled.fill(0)
    oled.text("Prog wlaczenia:",1,5)
    oled.text("%3.1f" %settings.onThreshold,1,15)
    oled.show()
    actionTimer = ACTION_TIMER_DEFAULT

def specialDownOnThresholdButtonPressReaction():
    global settings, oled, actionTimer
    print("special down")
    settings.onThreshold-=1
    oled.fill(0)
    oled.text("Prog wlaczenia:",1,5)
    oled.text("%3.1f" %settings.onThreshold,1,15)
    oled.show()
    actionTimer = ACTION_TIMER_DEFAULT

def regularUpButtonReleaseReaction():
    global oled, displayTimer            
    oled.fill(0)
    oled.text("Prog wlaczenia:",1,5)
    oled.text("%3.1f" %settings.onThreshold,1,15)
    oled.show()
    sleep(2)
    oled.fill(0)
    displayTimer = DISPLAY_TIMER_DEFAULT

def specialUpOffThresholdButtonPressReaction():
    global settings, oled, actionTimer
    print("special up")
    settings.offThreshold+=1
    oled.fill(0)
    oled.text("Prog wylaczenia:",1,5)
    oled.text("%3.1f" %settings.offThreshold,1,15)
    oled.show()
    actionTimer = ACTION_TIMER_DEFAULT

def specialDownOffThresholdButtonPressReaction():
    global settings, oled, actionTimer
    print("special down")
    settings.offThreshold-=1
    oled.fill(0)
    oled.text("Prog wylaczenia:",1,5)
    oled.text("%3.1f" %settings.offThreshold,1,15)
    oled.show()
    actionTimer = ACTION_TIMER_DEFAULT

def regularDownButtonReleaseReaction():
    global oled, displayTimer            
    oled.fill(0)
    oled.text("Prog wylaczenia:",1,5)
    oled.text("%3.1f" %settings.offThreshold,1,15)
    oled.show()
    sleep(2)
    oled.fill(0)
    displayTimer = DISPLAY_TIMER_DEFAULT

#i/o devices setup
oled = SSD1306_I2C(OLED_WIDTH,OLED_HEIGHT,I2C(I2C_ID, scl=Pin(I2C_SCL_PIN_NUMBER), sda=Pin(I2C_SDA_PIN_NUMBER)))
sensor = DHT22(Pin(SENSOR_PIN_NUMBER))
buttonRed = picozero.Button(BUTTON_RED_PIN_NUMBER)
buttonBlue = picozero.Button(BUTTON_BLUE_PIN_NUMBER)
buttonTimer = 0
actionTimer = 3.0
specialActionInterval=0.1


#read or setup settings
try:
    settings = Settings(oled)
    #setting up a relay & test
    relay = picozero.DigitalOutputDevice(RELAY_PIN_NUMBER)
    relayState=0
    #display initialization message with a countdown
    displayTimer=3
    interval = 0.1
    while displayTimer>=0: 
        oled.text("Uruchamiam",5,0)
        oled.text("sensor",5,10)
        oled.text("Zaczekaj %1.1fs" %displayTimer,5,20)
        oled.show()    
        oled.fill(0)
        displayTimer-=interval
        sleep(interval)

    displayTimer = DISPLAY_TIMER_DEFAULT
    interval = 2
    divider :int = 20
    counter :int = 0
    #main loop

    while True:
        if counter==0:
            try:
                sensor.measure()    
                hum = sensor.humidity()
            except:                
                hum = READ_ERROR                            
            counter = divider
            if settings.getWorkType()==WorkType.humidifier:
                if hum!=READ_ERROR:
                    if hum<settings.onThreshold:
                        setRelay(False)                
                    if hum>settings.offThreshold:
                        setRelay(True)                
            else:
                if hum!=READ_ERROR:
                    if hum>settings.onThreshold:
                        setRelay(False)                
                    if hum<settings.offThreshold:
                        setRelay(True)                
            if displayTimer>0.0: #displays humidity information for some time and at random locations to reduce oled screen wear
                buff : str = 'Rh= %3.1f %%' %hum if hum!=READ_ERROR else "BLAD CZUJNIKA"
                graphLen =  len(buff)*8+1
                x = randrange(0,120-graphLen,1)
                y = randrange(0,24,1)
                oled.ellipse(x+graphLen+4,y+4,3,3,1,relayState==0)
                oled.text(buff,x,y)            
            if displayTimer>-interval: #updates the screen and makes sure it stays black after the time interval had passed
                oled.show()
                oled.fill(0)        
                displayTimer-=interval  
        if buttonRed.is_active and buttonBlue.is_inactive:            
            timeStart = ticks_ms()
            while buttonRed.is_active:
                pass 
            if ticks_diff(ticks_ms(),timeStart)<1000:                
                regularUpButtonReleaseReaction()
            else:                
                singleClick = True
                regularUpButtonReleaseReaction()
                actionTimer = ACTION_TIMER_DEFAULT               
                while actionTimer>0:     
                    if buttonRed.is_active and singleClick and buttonBlue.is_inactive:
                        specialUpOnThresholdButtonPressReaction()
                        singleClick = False                        
                    if buttonBlue.is_active and singleClick and buttonRed.is_inactive: 
                        specialDownOnThresholdButtonPressReaction()
                        singleClick = False                        
                    if buttonRed.is_inactive and buttonBlue.is_inactive:
                        singleClick = True
                    sleep(specialActionInterval)
                    actionTimer-=specialActionInterval
                oled.fill(0)
                oled.show()
                settings.saveSettings()
            displayTimer = DISPLAY_TIMER_DEFAULT
        
        if buttonRed.is_inactive and buttonBlue.is_active:            
            timeStart = ticks_ms()
            print ("Blue button pressed")
            while buttonBlue.is_active:                
                pass 
            if ticks_diff(ticks_ms(),timeStart)<1000:                
                print ("Blue button pressed SHORT")
                regularDownButtonReleaseReaction()
            else:                
                print ("Blue button pressed LOOONG")
                singleClick = True
                actionTimer = ACTION_TIMER_DEFAULT
                regularDownButtonReleaseReaction()               
                while actionTimer>0:     
                    if buttonRed.is_inactive and singleClick and buttonBlue.is_active:
                        print ("Blue button down off")
                        specialDownOffThresholdButtonPressReaction()
                        singleClick = False                        
                    if buttonBlue.is_inactive and singleClick and buttonRed.is_active: 
                        print ("Blue button up off")
                        specialUpOffThresholdButtonPressReaction()
                        singleClick = False                        
                    if buttonRed.is_inactive and buttonBlue.is_inactive:
                        singleClick = True
                    sleep(specialActionInterval)
                    actionTimer-=specialActionInterval
                oled.fill(0)
                oled.show()                
                settings.saveSettings()
            displayTimer = DISPLAY_TIMER_DEFAULT

        sleep(interval/divider)
        counter-=1
except Exception as e:
    print(e.args)   
    while True: #display a short blinking error message if something is wrong
        oled.text("Problem!",randrange(0,100,1),randrange(0,24))
        oled.show()
        sleep(1)
        oled.fill(0)
        oled.show()
        sleep(1)

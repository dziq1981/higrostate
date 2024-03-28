from constants import ON_THRESHOLD, OFF_THRESHOLD, SETTINGS_FILENAME
import ujson as json
from ssd1306 import SSD1306_I2C
from time import sleep
from sys import exit

class WorkType():
    dryer = 1
    humidifier = 2

class Settings():

    onThreshold : float= 85
    offThreshold : float = 70
    settingsJson = {ON_THRESHOLD: onThreshold, OFF_THRESHOLD: offThreshold} #deafult values & settings json init

    def __init__(self, oled : SSD1306_I2C) -> None:
        print("Reading settings")
        if not self.loadSettings():
            if not self.saveSettings():
                oled.text("Blad odczytu ustawien!",5,5)
                oled.text("Wezwij serwis.",5,15)
                oled.show()            
                sleep(10)
                oled.fill(0)
                oled.show()
                exit()

    def loadSettings(self)-> bool:            
        try:
            with open(SETTINGS_FILENAME, 'r') as f:
                self.settingsJson = json.load(f)
            self.onThreshold = float(self.settingsJson[ON_THRESHOLD])
            self.offThreshold = float(self.settingsJson[OFF_THRESHOLD])
            return True
        except:
            return False

    def saveSettings(self)-> bool:    
        self.settingsJson = {ON_THRESHOLD: self.onThreshold, OFF_THRESHOLD: self.offThreshold}
        try:
            with open(SETTINGS_FILENAME, 'w') as f:
                json.dump(self.settingsJson, f)
            return True
        except:
            return False
        
    def getWorkType(self) -> int:
        if self.onThreshold<=self.offThreshold:
            return WorkType.humidifier
        else:
            return WorkType.dryer
    

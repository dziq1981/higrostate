from micropython import const

#constants - pin numbers
SENSOR_PIN_NUMBER = const(22)
BUTTON_RED_PIN_NUMBER = const(17)
BUTTON_BLUE_PIN_NUMBER = const(16)
I2C_SCL_PIN_NUMBER = const(1)
I2C_SDA_PIN_NUMBER = const(0)
RELAY_PIN_NUMBER = const(20)
I2C_ID = const(0)
OLED_WIDTH = const(128)
OLED_HEIGHT = const(32)
#constants - filename to store the settings
SETTINGS_FILENAME = const("settings.json")
ON_THRESHOLD = const("on_threshold")
OFF_THRESHOLD = const("off_threshold")
DISPLAY_TIMER_DEFAULT = const(30.0)
LCD_INTERVAL = const(2)
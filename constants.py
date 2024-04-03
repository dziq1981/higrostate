from micropython import const

#constants - pin numbers
SENSOR_PIN_NUMBER = const(28)
BUTTON_RED_PIN_NUMBER = const(17)
BUTTON_BLUE_PIN_NUMBER = const(16)
I2C_SCL_PIN_NUMBER = const(27)
I2C_SDA_PIN_NUMBER = const(26)
RELAY_PIN_NUMBER = const(19)
I2C_ID = const(0)
#constants oled screen size
OLED_WIDTH = const(128)
OLED_HEIGHT = const(32)
#constants - filename to store the settings and names used in the file
SETTINGS_FILENAME = const("settings.json")
ON_THRESHOLD = const("on_threshold")
OFF_THRESHOLD = const("off_threshold")
#constant timers and interval defaults
DISPLAY_TIMER_DEFAULT = const(30.0)
ACTION_TIMER_DEFAULT = const(3.0)
LCD_INTERVAL = const(2)
#constants other
READ_ERROR = const(150)
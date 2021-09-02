import network, ntptime, os, time
from ssd1351 import Display, color565
from machine import Pin, SPI, TouchPad, Timer
from xglcd_font import XglcdFont

spi = SPI(2, baudrate=14500000, sck=Pin(18), mosi=Pin(23))
display = Display(spi, dc=Pin(16), cs=Pin(17), rst=Pin(5))
big_font = XglcdFont('fonts/EspressoDolce18x24.c', 18, 24)
font = XglcdFont('fonts/Bally7x9.c', 7, 9)

touchPin = TouchPad(Pin(32))
touchTreshold = 450
touchAntiErrorChecks = 3
holdTreshold = 500

appNames = ['empty']
appIDs = ['empty']

file = open('sys/wifi/ssid')
ssid = file.read()
file.close
file = open('sys/wifi/password')
password = file.read()
file.close

try:
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(ssid, password)
except:
    #relax
    print()
ntptime.settime()

def millis():
    return time.ticks_ms()

def drawBG():
    display.draw_image('bg.raw', 0, 0, 128, 128)

def getBatteryPercent():
    #will have to analogread smth; not on current hardware; also just 0, 20, 40, 60 and 100 to return
    return 100

def getInteraction():
    touchAntiError = 0
    while touchPin.read() < touchTreshold:
        #relax
        print()
    while True:
        touchAntiError = touchAntiError + 1
        if touchPin.read() > touchTreshold:
            touchAntiError = 0
        
        if touchAntiError == touchAntiErrorChecks:
            break
    initialTouchTime = millis()
    while touchPin.read() < touchTreshold and millis() < initialTouchTime + holdTreshold:
        #relax
        print()
    if millis() < initialTouchTime + holdTreshold:
        return "tap"
    else:
        return "hold"

def getTime():
    file = open('sys/time/zone')
    utc_difference = int(file.read())
    file.close
    hour = time.localtime()[3] + utc_difference
    minute = time.localtime()[4]
    return str(hour) + ':' + str(minute)

def dispoff():
    display.fill_rectangle(0, 0, 128, 128, color565(0, 0, 0,))
    time.sleep(1)
    getInteraction()
    home()

def infoBar():
    if sta_if.isconnected():
        display.draw_image('sys/icons/wifi.raw', 0, 0, 8, 8)
    else:
        display.draw_image('sys/icons/no_wifi.raw', 0, 0, 8, 8)
    
    if getBatteryPercent() == 0:
        display.draw_image('sys/icons/battery_0.raw', 10, 0, 8, 8)
    if getBatteryPercent() == 20:
        display.draw_image('sys/icons/battery_20.raw', 10, 0, 8, 8)
    if getBatteryPercent() == 40:
        display.draw_image('sys/icons/battery_40.raw', 10, 0, 8, 8)
    if getBatteryPercent() == 60:
        display.draw_image('sys/icons/battery_60.raw', 10, 0, 8, 8)
    if getBatteryPercent() == 80:
        display.draw_image('sys/icons/battery_80.raw', 10, 0, 8, 8)
    if getBatteryPercent() == 100:
        display.draw_image('sys/icons/battery_100.raw', 10, 0, 8, 8)

def apps(page):
    try:
        app1Name = appNames[page*2-1]
    except:
        app1Name = '-'
    try:
        app2Name = appNames[page*2]
    except:
        app2Name = '-'
    option = 1
    while True:
        drawBG()
        infoBar()
        display.draw_text(10, 10, 'Apps (' + str(page) + ')', big_font, color565(255, 255, 255), 0, False, 1)
        if option == 1:
            display.draw_text(10, 100, app1Name, font, color565(44, 242, 140), 0, False, 0)
        else:
            display.draw_text(10, 100, app1Name, font, color565(255, 255, 255), 0, False, 0)
        if option == 2:
            display.draw_text(64, 100, app2Name, font, color565(44, 242, 140), 0, False, 0)
        else:
            display.draw_text(64, 100, app2Name, font, color565(255, 255, 255), 0, False, 0)
        if option == 3:
            display.draw_text(10, 110, '<', font, color565(44, 242, 140), 0, False, 0)
        else:
            display.draw_text(10, 110, '<', font, color565(255, 255, 255), 0, False, 0)
        if option == 4:
            display.draw_text(64, 110, '>', font, color565(44, 242, 140), 0, False, 0)
        else:
            display.draw_text(64, 110, '>', font, color565(255, 255, 255), 0, False, 0)

        if getInteraction() == 'tap':
            if option == 4:
                option = 1
            else:
                option = option + 1
        else:
            if option == 1:
                try:
                    appIDs[page*2-1]()
                except:
                    print()
            elif option == 2:
                try:
                    appIDs[page*2]()
                except:
                    print()
            elif option == 3:
                if page != 1:
                    apps(page - 1)
                else:
                    home()
            else:
                if page != 16:
                    apps(page + 1)

def home():
    option = 1
    while True:
        drawBG()
        infoBar()
        time=getTime()
        display.draw_text(10, 10, time, big_font, color565(255, 255, 255), 0, False, 1)
        display.draw_hline(10, 37, 90, color565(255, 255, 255))
        if option == 1:
            display.draw_text(10, 100, "Apps", font, color565(44, 242, 140), 0, False, 1)
            display.draw_text(64, 100, "Power off", font, color565(255, 255, 255), 0, False, 1)
        else:
            display.draw_text(10, 100, "Apps", font, color565(255, 255, 255), 0, False, 1)
            display.draw_text(64, 100, "Power off", font, color565(44, 242, 140), 0, False, 1)

        if getInteraction() == "tap":
            if option == 1:
                option = 2
            else:
                option = 1
        else:
            if option == 1:
                apps(1)
            else:
                dispoff()
        

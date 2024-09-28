from PyP100 import PyL530
import requests.exceptions
import colorsys
import time
import json
import ast

email = "chrissypantsplays@gmail.com"
password = "lol12345"

prevent_overload, prevent_overload_color = 0, 0


class LightBulb:
    def __init__(self, ip, bulb_num):
        self._ip = ip
        self._bulb_num = bulb_num

        self._bulb_item = None
        self._device_state = None
        self._info = None

    def handshake(self):
        loop = True
        if self._bulb_item is None:
            print("[ERROR] - 005 - Bulb has not been initialized")

        id_ = 0
        while loop:
            try:
                self._bulb_item.handshake()
            except requests.exceptions.ConnectTimeout or requests.exceptions.ConnectionError:
                print(f"Connection to bulb {self._bulb_num} failed retrying in 1 Second")
                time.sleep(5)
            except Exception as e:
                id_ += 1
                if id_ == 5:
                    print(f"No connection could be established to light bulb number {self._bulb_num}")
                    loop = False
                time.sleep(1) 
            else:
                print(f"Bulb {self._bulb_num} Logged in ")
                self._bulb_item.login()
                loop = False
        if id_ == 5:
            exit()
        self._info = self.get_device_info()

    def create_bulb(self):
        self._bulb_item = PyL530.L530(self._ip, email, password)

    def get_device_info(self):
        self._info = self._bulb_item.getDeviceInfo()
        return self._info

    def bulb_state(self):
        self.get_device_info()
        if self._info["device_on"] is False:
            self._bulb_item.turnOn()
        elif self._info["device_on"] is True:
            self._bulb_item.turnOff()

    def brightness(self, bright):
        self._bulb_item.setBrightness(int(bright).__round__())

    def color(self, hue=None, sat=None, rgb=None):
        if rgb is not None:
            rgb = ast.literal_eval(rgb)
            r_normalized = rgb[0] / 255.0
            g_normalized = rgb[1] / 255.0
            b_normalized = rgb[2] / 255.0

            hue, saturation, _ = colorsys.rgb_to_hsv(r_normalized, g_normalized, b_normalized)

            hue = hue * 360
            sat = saturation * 100

        self._bulb_item.setColor(hue.__round__(), sat.__round__())

    def reconnect(self):
        self.create_bulb()
        self.handshake()
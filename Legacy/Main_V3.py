import colorsys
import os
import threading
import requests.exceptions
import speech_recognition.exceptions
from PyP100 import PyL530
from customtkinter import *
from PIL import Image
import time
import ast
# -- need to install on orange pi
import speech_recognition as sr

# -- Config vars
# Config for CustomTkinter
root = CTk()
root.rowconfigure(0)
root.columnconfigure(0)
widgets = []
page_id_row = 0
page_id_col = 0
font = ("Arial", 20, "bold")

# Config for Home Assistant
freq = 44100
duration = 5

# get_settings() Vars
default_settings = {'voice_control': False}
settings_file_path = "Misc/settings.txt"

# Config for settings
settings_dict = {}

# Config for Light Bulbs
email = "chrissypantsplays@gmail.com"
password = "lol12345"
# -- End

mac_lamp1 = '14:eb:b6:d2:29:38'
mac_lamp2 = '14:eb:b6:d2:97:1a'

ip_lamp1 = "192.168.2.124"
ip_lamp2 = "192.168.2.125"

# [     ]   []   {   }   {}  \ @

bulb_chris_1 = PyL530.L530(ip_lamp1, email, password)
bulb_chris_2 = PyL530.L530(ip_lamp2, email, password)
prevent_overload, prevent_overload_color = 0, 0


def handshake(bulb_item, bulb_num):
    loop = True
    while loop:
        try:
            bulb_item.handshake()
        except requests.exceptions.ConnectTimeout or requests.exceptions.ConnectionError:
            print(f"Connection to bulb {bulb_num} failed retrying in 1 Second")
            time.sleep(1)
        except Exception as e:
            if str(e) == "Failed to initialize protocol":
                print(f"No connection could be established to light bulb number {bulb_num}")
                exit()
        else:
            print(f"Bulb {bulb_num} Logged in ")
            bulb_item.login()
            loop = False


handshake(bulb_chris_1, "1")
handshake(bulb_chris_2, "2")

device_info = bulb_chris_1.getDeviceInfo()

device_brightness = device_info["brightness"]
device_on = device_info["device_on"]
if device_on is False:
    bulb_state = "off"
elif device_on is True:
    bulb_state = "on"

colors = tuple(
    round(i * 255) for i in colorsys.hsv_to_rgb(device_info["hue"] / 360, device_info["saturation"] / 100, 1))
hex_ = "#%02x%02x%02x" % colors


# Process the voice control commands
def process_voice_command(command):
    command_mapping = {"turn the lights on": lambda: bulb_switch(switch="on"),
                       "turn the lights off": lambda: bulb_switch(switch="off"),
                       "system shutdown": lambda: exit()}

    cmd = command.split()  # Use the command (excluding "Luna") as the key
    cmd_key = ""
    for i in cmd:
        cmd_key = cmd_key + i + " "
        print(cmd_key[:-1])
        if cmd_key[:-1] in command_mapping:
            command_mapping[cmd_key[:-1]]()


# sets up the voice recognition loop
def voice_recognition():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        while settings_dict["voice_control"]:
            try:
                audio = r.listen(source, timeout=5)
                voice_command_text = r.recognize_google(audio)

                command_list = voice_command_text.split(" ")

                for i, word in enumerate(command_list):
                    print(i, word)
                    if word == "Luna":
                        process_voice_command(" ".join(command_list[i+1:]))
                        break

            except sr.UnknownValueError:
                print("[ERROR] No Voice Detected")


# Gets Current Settings From File
def get_settings():
    global settings_dict

    os.makedirs("Misc", exist_ok=True)

    if not os.path.isfile(settings_file_path):
        with open(settings_file_path, "w") as f:
            f.write(str(default_settings))

    with open(settings_file_path) as f:
        settings_dict = ast.literal_eval(f.read())


# Deletes All items in widgets list
def delete():
    global widgets
    for i in widgets:
        i.destroy()
    widgets = []


# Turns Light On/Off
def bulb_switch(bulb_on_off_button=None, switch=""):
    global bulb_state
    if bulb_state == "off" or switch == "on":
        bulb_chris_1.turnOn()
        bulb_chris_2.turnOn()
        bulb_state = "on"
        if bulb_on_off_button is not None:
            bulb_on_off_button.configure(text="Turn Off")

    elif bulb_state == "on" or switch == "off":
        bulb_chris_1.turnOff()
        bulb_chris_2.turnOff()
        bulb_state = "off"
        if bulb_on_off_button is not None:
            bulb_on_off_button.configure(text="Turn On")


# Bulb Page
def bulb():
    def brightness(event, reset="nothing"):
        global prevent_overload
        if bulb_state == "off":
            return
        elif prevent_overload != 0 and reset == "nothing":
            return

        bulb_chris_1.setBrightness(bulb_brightness_scale.get().__round__())
        bulb_chris_2.setBrightness(bulb_brightness_scale.get().__round__())
        bulb_bright_label.configure(text=str(bulb_brightness_scale.get().__round__()))
        if reset == "reset":
            prevent_overload = 0
        else:
            prevent_overload = 1
            bulb_brightness_scale.after(1000, lambda: brightness("place holder", reset="reset"))

    def color(event, reset="nothing"):
        global colors, hex_, prevent_overload_color
        if bulb_state == "off":
            return
        elif prevent_overload_color != 0 and reset == "nothing":
            return
        hue = bulb_hue_scale.get().__round__()
        sat = bulb_saturation_scale.get().__round__()

        bulb_chris_1.setColor(hue, sat)
        bulb_chris_2.setColor(hue, sat)

        colors = tuple(round(i * 255) for i in colorsys.hsv_to_rgb(hue / 360, sat / 100, 1))
        hex_ = "#%02x%02x%02x" % colors
        bulb_view_button.configure(bg_color=hex_, fg_color=hex_, hover_color=hex_)
        if reset == "reset":
            prevent_overload_color = 0
        else:
            prevent_overload_color = 1
            bulb_hue_scale.after(1000, lambda: color("place holder", reset="reset"))

    def reconnect():
        global bulb_chris_1, bulb_chris_2
        bulb_chris_1 = PyL530.L530(ip_lamp1, email, password)
        bulb_chris_2 = PyL530.L530(ip_lamp2, email, password)

        handshake(bulb_chris_1, "1")
        handshake(bulb_chris_2, "2")

    global bulb_state, hex_

    bulb_frame = CTkFrame(root)
    bulb_frame.grid(row=0, column=0)
    widgets.append(bulb_frame)

    back = CTkButton(bulb_frame,
                     text="Back",
                     font=font,
                     command=lambda: (delete(), menu()))
    back.grid(row=0, column=0,
              pady=5, padx=5, sticky="nw")

    # Bulb State Frame
    bulb_state_frame = CTkFrame(bulb_frame)
    bulb_state_frame.grid(row=1, column=0, padx=5, pady=5, sticky="n")

    bulb_on_info = CTkLabel(bulb_state_frame,
                            text="Turn Light On/Off",
                            font=font)
    bulb_on_info.grid(row=1, column=0,
                      pady=5, padx=5, sticky="nw")

    if bulb_state == "off":
        text = "Turn On"
    else:
        text = "Turn Off"

    bulb_on_off_button = CTkButton(bulb_state_frame,
                                   text=text,
                                   font=font,
                                   command=lambda: (bulb_switch(bulb_on_off_button)))
    bulb_on_off_button.grid(row=2, column=0,
                            pady=5, padx=5, sticky="nw")

    # Bulb Brightness Frame
    bulb_brightness_frame = CTkFrame(bulb_frame)
    bulb_brightness_frame.grid(row=1, column=2, padx=5, pady=5, sticky="n")

    bulb_brightness_label = CTkLabel(bulb_brightness_frame,
                                     text="Brightness",
                                     font=font)
    bulb_brightness_label.grid(row=0, column=0,
                               padx=5, pady=5, sticky="n")

    bulb_bright_label = CTkLabel(bulb_brightness_frame,
                                 text=str(device_brightness),
                                 font=font)
    bulb_bright_label.grid(row=1, column=0, padx=5, pady=5, sticky="n")

    bulb_brightness_scale = CTkSlider(bulb_brightness_frame, orientation="horizontal",
                                      from_=1, to=100, number_of_steps=100, width=200,
                                      command=brightness)
    bulb_brightness_scale.set(device_brightness)
    bulb_brightness_scale.grid(row=1, column=0, padx=5, pady=50, sticky="nw")

    # Bulb Color Frame
    bulb_color_frame = CTkFrame(bulb_frame)
    bulb_color_frame.grid(row=1, column=4, padx=5, pady=5, sticky="n")

    bulb_color_label = CTkLabel(bulb_color_frame,
                                text="Change color",
                                font=font)
    bulb_color_label.grid(row=1, column=1, columnspan=2,
                          padx=5, pady=5, sticky="n")

    bulb_view_button = CTkButton(bulb_color_frame, text="",
                                 bg_color=hex_, fg_color=hex_, hover_color=hex_,
                                 width=400, height=125)
    bulb_view_button.grid(row=2, column=1, columnspan=2,
                          padx=5, pady=5, sticky="w")

    bulb_hue_label = CTkLabel(bulb_color_frame,
                              text="Hue", font=font)
    bulb_hue_label.grid(row=3, column=1,
                        padx=5, pady=5, sticky="w")

    bulb_hue_scale = CTkSlider(bulb_color_frame,
                               orientation="horizontal",
                               from_=0, to=360, number_of_steps=360, width=300,
                               command=color)
    bulb_hue_scale.grid(row=3, column=2,
                        padx=5, pady=5, sticky="nw")

    bulb_saturation_label = CTkLabel(bulb_color_frame,
                                     text="Saturation",
                                     font=font)
    bulb_saturation_label.grid(row=4, column=1,
                               padx=5, pady=5, sticky="w")

    bulb_saturation_scale = CTkSlider(bulb_color_frame,
                                      orientation="horizontal",
                                      from_=0, to=100, number_of_steps=360, width=300,
                                      command=color)
    bulb_saturation_scale.grid(row=4, column=2,
                               padx=5, pady=5, sticky="nw")

    # Reconnect Frame
    bulb_reconnect_frame = CTkFrame(bulb_frame)
    bulb_reconnect_frame.grid(row=1, column=6, padx=5, pady=5, sticky="n")

    bulb_reconnect_label = CTkLabel(bulb_reconnect_frame,
                                    text="Reconnect to Bulb",
                                    font=font)
    bulb_reconnect_label.grid(row=1, column=1,
                              padx=5, pady=5, sticky="n")

    bulb_reconnect_button = CTkButton(bulb_reconnect_frame,
                                      text="Reconnect",
                                      font=font,
                                      command=reconnect)
    bulb_reconnect_button.grid(row=2, column=1,
                               padx=5, pady=5, sticky="n")


# Computer Page
def computer():
    pc_frame = CTkFrame(root)
    pc_frame.grid(row=0, column=0)
    widgets.append(pc_frame)

    back = CTkButton(pc_frame, text="Back",
                     font=font,
                     command=lambda: (delete(), menu()))
    back.grid(row=0, column=0,
              pady=5, padx=5, sticky="nw")


# Settings Page
def settings():
    def voice_control_toggle():
        global settings_dict
        if not settings_dict["voice_control"]:
            settings_dict["voice_control"] = True
            settings_voice_control_button.configure(text="Turn Off")
            threading.Thread(target=voice_recognition).start()
            print("Voice Control On")
        else:
            settings_dict["voice_control"] = False
            settings_voice_control_button.configure(text="Turn On")
            print("Voice Control Off")

    get_settings()

    settings_frame = CTkFrame(root)
    settings_frame.grid(row=0, column=0)
    widgets.append(settings_frame)

    back = CTkButton(settings_frame, text="Back",
                     font=font,
                     command=lambda: (delete(), menu()))
    back.grid(row=0, column=0,
              pady=5, padx=5, sticky="nw")

    # Settings Frame
    settings_general_frame = CTkFrame(settings_frame)
    settings_general_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nw")

    settings_general_label = CTkLabel(settings_general_frame,
                                      text="General Settings",
                                      font=font)
    settings_general_label.grid(row=0, column=0, padx=5, pady=5, sticky="nw")

    settings_voice_control_label = CTkLabel(settings_general_frame,
                                            text="Voice Control Toggle",
                                            font=font)
    settings_voice_control_label.grid(row=1, column=0, padx=5, pady=5, sticky="nw")

    settings_voice_control_button = CTkButton(settings_general_frame,
                                              text=f"Turn On",
                                              font=font,
                                              command=voice_control_toggle)
    settings_voice_control_button.grid(row=2, column=0, padx=5, pady=5, sticky="nw")


# Menu Page
def menu():
    # Creates Pages (Image_Name=ButtonIcon - Command=ButtonCommand)
    def create_page(image_name, command):
        global page_id_row, page_id_col
        image = CTkImage(Image.open(f"Images/{image_name}.png"), size=(300, 300))
        button = CTkButton(root, text="",
                           image=image,
                           command=lambda: (delete(), command()))
        button.grid(row=page_id_row, column=page_id_col,
                    padx=5, pady=5, sticky="nw")
        widgets.append(button)

        page_id_col += 1
        if page_id_col == 3:
            page_id_row += 1
            page_id_col = 0

    create_page("bulb", bulb)
    create_page("computer", computer)
    create_page("settings", settings)


# bulb()
get_settings()
menu()
root.attributes("-topmost", True)
root.geometry("1024x600")
root.mainloop()

import tkinter as tk
from tkinter import ttk, scrolledtext, simpledialog
import pyttsx3
import speech_recognition as sr
import datetime
import os
import webbrowser
import pyautogui
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pywhatkit
import random
import subprocess
import re
import threading
import requests
from sympy import sympify, sin, cos, tan, sqrt, pi
import socket
import glob
import logging
from dotenv import load_dotenv
import urllib.request 
import cv2 
import numpy as np

# Load environment variables
load_dotenv()

class IshaAssistant:
    """A personal desktop assistant with voice and text command capabilities."""
    def __init__(self, root):
        self.root = root
        self.root.title("Isha Assistant")
        self.root.geometry("600x400")
        
        # Initialize logging
        logging.basicConfig(filename="isha_assistant.log", level=logging.INFO, 
                           format="%(asctime)s - %(levelname)s - %(message)s")
        
        # Initialize text-to-speech
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        selected_voice = voices[0] if voices else None
        for voice in voices:
            if "zira" in voice.name.lower() or "female" in voice.name.lower():
                selected_voice = voice
                break
        if not voices:
            self.chat_box_insert("Output: No voices available for text-to-speech\n")
        else:
            self.engine.setProperty('voice', selected_voice.id)
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 0.9)
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = None
        try:
            self.microphone = sr.Microphone()
        except (AttributeError, OSError) as e:
            logging.error(f"Microphone initialization failed: {str(e)}")
            self.chat_box_insert("Output: Voice recognition disabled. PyAudio not found or microphone issue. Please install PyAudio and check microphone.\n")
        
        self.is_listening = False
        
        # Internet check caching
        self.last_internet_check = 0
        self.internet_status = False
        self.internet_check_interval = 10
        
        # GUI Elements
        self.create_gui()
        
        # Settings and Apps lists
        self.SETTING_MAP = {
            "display setting": ("ms-settings:display", "01"),
            "sound setting": ("ms-settings:sound", "03"),
            "notification & action setting": ("ms-settings:notifications", "07"),
            "focus assist setting": ("ms-settings:quiethours", "08"),
            "power & sleep setting": ("ms-settings:powersleep", "04"),
            "storage setting": ("ms-settings:storagesense", "05"),
            "tablet setting": ("ms-settings:tablet", "03"),
            "multitasking setting": ("ms-settings:multitasking", "088"),
            "projecting to this pc setting": ("ms-settings:project", "099"),
            "shared experiences setting": ("ms-settings:crossdevice", "076"),
            "system components setting": ("ms-settings:appsfeatures-app", "098"),
            "clipboard setting": ("ms-settings:clipboard", "054"),
            "remote desktop setting": ("ms-settings:remotedesktop", "00"),
            "optional features setting": ("ms-settings:optionalfeatures", "021"),
            "about setting": ("ms-settings:about", "007"),
            "system setting": ("ms-settings:system", "0022"),
            "devices setting": ("ms-settings:devices", "0033"),
            "mobile devices setting": ("ms-settings:mobile-devices", "0044"),
            "network & internet setting": ("ms-settings:network", "0055"),
            "personalization setting": ("ms-settings:personalization", "0066"),
            "apps setting": ("ms-settings:appsfeatures", "0099"),
            "account setting": ("ms-settings:yourinfo", "0088"),
            "time & language setting": ("ms-settings:dateandtime", "0010"),
            "gaming setting": ("ms-settings:gaming", "0009"),
            "ease of access setting": ("ms-settings:easeofaccess", "0080"),
            "privacy setting": ("ms-settings:privacy", "0076"),
            "updated & security": ("ms-settings:windowsupdate", "0087")
        }

        self.SETTING_MAP4s = {
            "01": ("ms-settings:display"),
            "03": ("ms-settings:sound"),
            "07": ("ms-settings:notifications"),
            "08": ("ms-settings:quiethours"),
            "04": ("ms-settings:powersleep"),
            "05": ("ms-settings:storagesense"),
            "03": ("ms-settings:tablet"),
            "088": ("ms-settings:multitasking"),
            "099": ("ms-settings:project"),
            "076": ("ms-settings:crossdevice"),
            "098": ("ms-settings:appsfeatures-app"),
            "054": ("ms-settings:clipboard"),
            "00": ("ms-settings:remotedesktop"),
            "021": ("ms-settings:optionalfeatures",),
            "007": ("ms-settings:about"),
            "0022": ("ms-settings:system"),
            "0033": ("ms-settings:devices"),
            "0044": ("ms-settings:mobile-devices"),
            "0055": ("ms-settings:network"),
            "0066": ("ms-settings:personalization"),
            "0099": ("ms-settings:appsfeatures"),
            "0088": ("ms-settings:yourinfo"),
            "0010": ("ms-settings:dateandtime"),
            "0009": ("ms-settings:gaming"),
            "0080": ("ms-settings:easeofaccess"),
            "0076": ("ms-settings:privacy"),
            "0087": ("ms-settings:windowsupdate")
        }

        self.apps_commands = {
            "alarms & clock": "ms-clock:",
            "calculator": "calc",
            "calendar": "outlookcal:",
            "camera": "microsoft.windows.camera:",
            "copilot": "ms-copilot:",
            "cortana": "ms-cortana:",
            "game bar": "ms-gamebar:",
            "groove music": "mswindowsmusic:",
            "mail": "outlookmail:",
            "maps": "bingmaps:",
            "microsoft edge": "msedge",
            "microsoft solitaire collection": "ms-solitaire:",
            "microsoft store": "ms-windows-store:",
            "mixed reality portal": "ms-mixedreality:",
            "movies & tv": "mswindowsvideo:",
            "office": "ms-office:",
            "onedrive": "ms-onedrive:",
            "onenote": "ms-onenote:",
            "outlook": "outlookmail:",
            "outlook (classic)": "ms-outlook:",
            "paint": "mspaint",
            "paint 3d": "ms-paint:",
            "phone link": "ms-phonelink:",
            "power point": "ms-powerpoint:",
            "settings": "ms-settings:",
            "skype": "skype:",
            "snip & sketch": "ms-snip:",
            "sticky note": "ms-stickynotes:",
            "tips": "ms-tips:",
            "voice recorder": "ms-soundrecorder:",
            "weather": "msnweather:",
            "windows backup": "ms-settings:backup",
            "windows security": "ms-settings:windowsdefender",
            "word": "ms-word:",
            "xbox": "ms-xbox:",
            "about your pc": "ms-settings:about"
        }

        self.apps_commands4q = {
            "a1": "ms-clock:",
            "c1": "calc",
            "c2": "outlookcal:",
            "c3": "microsoft.windows.camera:",
            "c4": "ms-copilot:",
            "c5": "ms-cortana:",
            "gb1": "ms-gamebar:",
            "gm1": "mswindowsmusic:",
            "m1": "outlookmail:",
            "ms1": "bingmaps:",
            "me1": "msedge",
            "mc1": "ms-solitaire:",
            "ms1": "ms-windows-store:",
            "mp1": "ms-mixedreality:",
            "mt1": "mswindowsvideo:",
            "o1": "ms-office:",
            "oe": "ms-onedrive:",
            "oe": "ms-onenote:",
            "ouk": "outlookmail:",
            "oc1": "ms-outlook:",
            "p1": "mspaint",
            "p3d": "ms-paint:",
            "pk": "ms-phonelink:",
            "pt": "ms-powerpoint:",
            "ss": "ms-settings:",
            "sk1": "skype:",
            "s0h": "ms-snip:",
            "s1e": "ms-stickynotes:",
            "ts0": "ms-tips:",
            "vr0": "ms-soundrecorder:",
            "weather": "msnweather:",
            "windows backup": "ms-settings:backup",
            "windows security": "ms-settings:windowsdefender",
            "word": "ms-word:",
            "xbox": "ms-xbox:",
            "about your pc": "ms-settings:about"
        }

        self.software_dict = {
            "notepad": "notepad",
            "ms word": "winword",
            "command prompt": "cmd",
            "excel": "excel",
            "vscode": "code",
            "word16": "winword",
            "file explorer": "explorer",
            "edge": "msedge",
            "microsoft 365 copilot": "ms-copilot:",
            "outlook": "outlook",
            "microsoft store": "ms-windows-store:",
            "photos": "microsoft.photos:",
            "xbox": "xbox:",
            "solitaire": "microsoft.microsoftsolitairecollection:",
            "clipchamp": "clipchamp",
            "to do": "microsoft.todos:",
            "linkedin": "https://www.linkedin.com",
            "calculator": "calc",
            "news": "bingnews:",
            "one drive": "onedrive",
            "onenote 2016": "onenote",
            "google": "https://www.google.com"
        }

        # Merge commands_dict with priority to apps_commands to avoid conflicts
        self.commands_dict = {**self.SETTING_MAP, **self.SETTING_MAP4s, **self.software_dict, **self.apps_commands, **self.apps_commands4q}
        self.commands_dict = {k: v if isinstance(v, str) else v[0] for k, v in self.commands_dict.items()}
        
        self.settings_list = [f"{name} ({code})" for name, (_, code) in self.SETTING_MAP.items()]
        self.apps_list = list(self.apps_commands.keys())
        
        # Check for Gemini API key and prompt if not found
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            api_key = simpledialog.askstring("Gemini API Key", "Enter your Gemini API key (get one from https://aistudio.google.com/app/apikey):", parent=self.root)
            if api_key:
                os.environ["GEMINI_API_KEY"] = api_key
            else:
                self.chat_box_insert("Output: Gemini API key not provided. AI queries may not work.\n")
        
        self.wish_me()

    def check_internet(self):
        """Check internet connectivity with caching."""
        current_time = time.time()
        if current_time - self.last_internet_check < self.internet_check_interval:
            return self.internet_status

        self.last_internet_check = current_time
        for host in [("8.8.8.8", 80), ("1.1.1.1", 80)]:
            try:
                socket.create_connection(host, timeout=2)
                self.internet_status = True
                return True
            except (socket.gaierror, socket.timeout):
                continue
        self.internet_status = False
        return False

    def create_gui(self):
        """Create the GUI elements for the assistant."""
        self.chat_box = scrolledtext.ScrolledText(self.root, height=10, width=60)
        self.chat_box.pack(pady=10)
        
        self.input_box = ttk.Entry(self.root, width=50)
        self.input_box.pack(pady=5)
        self.input_box.bind("<Return>", self.process_text_input)
        
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)
        
        style = ttk.Style()
        style.configure('Voice.Off.TButton', background='red', foreground='black')
        style.configure('Voice.On.TButton', background='green', foreground='black')
        style.configure('Settings.TButton', background='green', foreground='black')
        style.configure('Apps.TButton', background='orange', foreground='black')
        style.configure('FileM.TButton', background='yellow', foreground='black')
        style.configure('Download.TButton', background='blue', foreground='black')
        style.configure('About.TButton', background='pink', foreground='black')
        
        self.voice_button = ttk.Button(button_frame, text="V", style='Voice.Off.TButton', command=self.toggle_voice)
        self.voice_button.grid(row=0, column=0, padx=5)
        
        ttk.Button(button_frame, text="Settings", style='Settings.TButton', command=self.toggle_settings).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Apps", style='Apps.TButton', command=self.toggle_apps).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="File M", style='FileM.TButton', command=self.open_file_explorer).grid(row=0, column=3, padx=5)
        ttk.Button(button_frame, text="Download", style='Download.TButton', command=self.open_downloads).grid(row=0, column=4, padx=5)
        ttk.Button(button_frame, text="About", style='About.TButton', command=self.show_about).grid(row=0, column=5, padx=5)
        
        self.status_label = ttk.Label(self.root, text="Internet: Checking...")
        self.status_label.pack(pady=5)
        self.update_internet_status()
        
        self.settings_popup = None
        self.apps_popup = None

    def update_internet_status(self):
        """Update the internet status label periodically."""
        status = "Online" if self.check_internet() else "Offline"
        self.status_label.config(text=f"Internet: {status}")
        self.root.after(10000, self.update_internet_status)

    def toggle_voice(self):
        """Toggle voice input on or off."""
        if self.microphone is None:
            self.speak("Voice recognition is disabled due to missing dependencies or hardware. Use text input instead.")
            self.chat_box_insert("Output: Voice recognition disabled. Please use text input.\n")
            return
        self.is_listening = not self.is_listening
        if self.is_listening:
            self.voice_button.configure(style='Voice.On.TButton')
            self.speak("Microphone is now on")
            threading.Thread(target=self.listen_voice, daemon=True).start()
        else:
            self.voice_button.configure(style='Voice.Off.TButton')
            self.speak("Microphone is now off")

    def wish_me(self):
        """Greet the user based on the time of day."""
        current_hour = datetime.datetime.now().hour
        greeting = (
            "Good morning" if 5 <= current_hour < 12 else
            "Good afternoon" if 12 <= current_hour < 17 else
            "Good evening" if 17 <= current_hour < 21 else
            "Good night"
        )
        self.speak(greeting)
        self.chat_box_insert(f"Output: {greeting}\n")

    def listen(self):
        """Listen for voice input and return transcribed text, fallback to text input if voice unavailable."""
        if self.microphone is None:
            query = simpledialog.askstring("Input", "Voice not available. Enter your command:", parent=self.root)
            return query.lower() if query else None
        
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                for _ in range(3):
                    try:
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                        return self.recognizer.recognize_google(audio).lower()
                    except sr.WaitTimeoutError:
                        self.speak("No speech detected, please try again")
                        continue
                    except sr.UnknownValueError:
                        self.speak("Could not understand audio, please try again")
                        continue
                    except sr.RequestError as e:
                        self.speak(f"Speech recognition error: {str(e)}")
                        return None
            return None
        except Exception as e:
            self.speak("Voice input failed. Please use text input.")
            self.chat_box_insert(f"Output: Voice input failed: {str(e)}. Please use text input.\n")
            query = simpledialog.askstring("Input", "Voice not available. Enter your command:", parent=self.root)
            return query.lower() if query else None

    def listen_voice(self):
        """Continuously listen for voice commands while enabled."""
        while self.is_listening:
            command = self.listen()
            if command:
                self.root.after(0, self.process_command, command)

    def chat_box_insert(self, text):
        """Insert text into the chat box and scroll to the end."""
        self.chat_box.insert(tk.END, text)
        self.chat_box.see(tk.END)

    def process_text_input(self, event):
        """Process text input from the entry box."""
        command = self.input_box.get().lower().strip()
        if command:
            self.input_box.delete(0, tk.END)
            self.process_command(command)

    def query_gemini_api(self, query):
        """Send a query to the Google Gemini API and return the response."""
        if not self.check_internet():
            self.speak("This feature requires an internet connection.")
            self.chat_box_insert("Output: Gemini API requires an internet connection.\n")
            return

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            self.speak("Gemini API key not found. Please configure it.")
            self.chat_box_insert("Output: Gemini API key not found.\n")
            return

        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": api_key
        }
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": query}
                    ]
                }
            ]
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            generated_text = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No response from API")
            self.speak(generated_text)
            self.chat_box_insert(f"Output: {generated_text}\n")
        except requests.exceptions.RequestException as e:
            logging.error(f"Gemini API error: {str(e)} - Response: {e.response.text if e.response else 'No response'}")
            self.speak("Failed to get a response from the Gemini API")
            self.chat_box_insert(f"Output: Failed to get a response from the Gemini API: {str(e)}\n")

    def process_command(self, command):
        """Process user commands and execute corresponding actions."""
        logging.info(f"Processing command: {command}, Internet: {self.internet_status}")
        self.chat_box_insert(f"Input: {command}\n")
        command = command.lower().strip()

        # Handle Gemini API queries
        if command.startswith("explain ") or command.startswith("what is ") or command.startswith("tell me about "):
            query = command
            self.query_gemini_api(query)
        # Handle time and date commands
        elif command in ["what is the time", "samaye kya ho raha hai", "time"]:
            self.get_time()
        elif command in ["what is the date", "aaj date kya hai", "date"]:
            self.get_date()
        # Handle math and calculator commands
        elif command.startswith("solve ") or re.match(r"^\d+\s*[\+\-\*/]\s*\d+", command):
            expression = command[6:] if command.startswith("solve ") else command
            self.solve_math(expression)
        elif command in ["open calculator", "calculator"]:
            self.open_calculator()
        elif command == "about all setting":
            self.show_all_settings_popup()
        elif command in ["open file m", "open file explorer"]:
            self.open_file_explorer()
        elif command in ["open download"]:
            self.open_downloads()
        elif command in ["open minimize", "minimize"]:
            self.minimize_windows()
        elif command in ["search", "app", "file", "setting"]:
            self.open_search()
        elif command in ["news", "show news"]:
            if self.check_internet():
                self.open_news_widget()
            else:
                self.speak("News requires internet. Opening local news app instead.")
                self.chat_box_insert("Output: Opening local news app\n")
                subprocess.run(["start", "msnweather:"], shell=True)
        elif command in ["open run command", "open run"]:
            self.open_run_command()
        elif command in ["open setting"]:
            self.open_settings()
        elif command in ["ok isha","ok google"]:
            self.find_now()    
        elif command in ["open about setting", "about this pc"]:
            self.open_about_settings()
        elif command in ["open project screen", "show project screen"]:
            self.open_project_screen()
        elif command in ["enhanced security"]:
            self.open_performance_settings()
        elif command in ["open feedback", "showing feedback", "show feedback"]:
            self.open_feedback_hub()
        elif command in ["open xbox", "game bar"]:
            self.open_game_bar()
        elif command in ["open mic"]:
            self.open_voice_typing()
        elif command in ["connect", "show all connect", "show network"]:
            self.open_connect_panel()
        elif command in ["lock screen", "screen lock kar do"]:
            self.lock_screen()
        elif command in ["show all menu"]:
            self.open_quick_menu()
        elif command in ["open cortana"]:
            self.open_cortana()
        elif command in ["open clipboard", "show clipboard"]:
            self.open_clipboard_history()
        elif command in ["duplicate window"]:
            self.open_notifications()
        elif "isha play song" in command or "play song" in command or "play music" in command:
            self.play_song()
        elif "youtube" in command or "isha youtube" in command or "manoranjan suru kiya jaaye" in command:
            self.open_youtube()
        elif "google" in command or "isha open google" in command or "google open now" in command or "open google" in command:
            self.open_google()
        elif "instagram" in command or "isha open instagram" in command or "instagram chalu karo" in command or "gili gili chu" in command or "gili gili chhu" in command or "gili gili suit" in command:
            self.open_instagram()
        elif "iti" in command:
            self.open_25()
        elif "open phone camera" in command:
            self.came2()
        elif "phone camera off" in command:
            self.cmaw21()
        elif "h1" in command.lower() or "open h1" in command or "isha open h1" in command:
            self.open_chatbox()
        elif "download photo" in command or "download picture" in command or "isha download photo" in command or "isha download picture" in command or "dd photo" in command or "dd picture" in command:
            self.download_picture()
        elif "instagram login" in command or "isha login instagram" in command or "instagram login now" in command:
            self.login_instagram()
        elif "whatsapp" in command or "isha whatsapp" in command:
            self.open_whatsapp()
        elif "hello" in command or "hello isha" in command or "hi" in command or "hi isha" in command:
            self.hello()
        elif "thank you isha" in command or "thank you" in command or "thanks isha" in command:
            self.thank_you_reply()
        elif "what you mane" in command or "what is your name" in command:
            self.what_is_your_name()
        elif "select all text" in command or "select all" in command:
            self.select_all_text()
        elif "good morning" in command or "morning" in command or "good morning isha" in command or "isha good morning" in command:
            self.morningtime()
        elif "stop song" in command or "stop" in command or "stop music" in command or "isha song band karo" in command:
            self.stop_song()
        elif "download reel" in command or "download storie" in command or "download instagram reel" in command or "instagram reel download" in command or "isha download instagram reel" in command or "download instagram stories" in command or "download instagram storie" in command or "isha downloas instagram storie" in command or "isha instagram storie download" in command or "isha instagram stories download" in command or "ist reel" in command:
            self.download_instagram_reel()
        elif "mute" in command or "song mute" in command or "isha song mute" in command or "awaaz band karo" in command or "isha song unmute karo" in command or "unmute song" in command or "unmute" in command:
            self.mute_unmute()
        elif "full screen" in command or "screen full karo" in command:
            self.full_screen()
        elif "caption chalu karo" in command or "caption" in command or "caption band karo" in command or "isha caption band karo" in command:
            self.toggle_caption()
        elif "weather" in command or "isha what is weather" in command or "aaj ka mausam kya hai" in command:
            self.get_weather()
        elif "shutdown" in command or "isha shutdown now" in command or "shutdown now" in command or "good night" in command or "isha good night" in command:
            self.shutdown_pc()
        elif "restart" in command or "isha pc restart now" in command or "restart now" in command:
            self.restart_pc()
        elif "find now" in command or "give me a answer" in command or "isha find now" in command or "search" in command or "search now" in command or "isha search now" in command:
            self.find_now()
        elif command == "about":
            self.show_about()
        elif command == "greet me":
            self.wish_me()
        else:
            self.handle_settings_apps_commands(command)

    def get_time(self):
        """Display the current time."""
        try:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            response = f"The current time is {current_time}"
            self.speak(response)
            self.chat_box_insert(f"Output: {response}\n")
        except Exception as e:
            self.speak("Error retrieving time")
            self.chat_box_insert(f"Output: Error retrieving time: {str(e)}\n")

    def get_date(self):
        """Display the current date."""
        try:
            current_date = datetime.datetime.now().strftime("%B %d, %Y")
            response = f"Today's date is {current_date}"
            self.speak(response)
            self.chat_box_insert(f"Output: {response}\n")
        except Exception as e:
            self.speak("Error retrieving date")
            self.chat_box_insert(f"Output: Error retrieving date: {str(e)}\n")

    def find_now(self):
        self.speak("What do you want me to search?")
        query = self.listen() 
        if query: 
            url = f"https://www.google.com/search?q={query}"
            webbrowser.open(url)
            self.speak(f"Searching for {query}")
        else:
            self.speak("I didn't catch that. Please try again.")

    def came2(self):
        URL = "https://192.168.43.1:8080/shot.jpg"
        while True:
              img_arr = np.array(bytearray(urllib.request.urlopen(URL).read()),dtype=np.uint8)
              img = cv2.imdecode(img_arr,-1)
              cv2.imshow('IPWebcam',img)
              q = cv2.waitkey(1)
              if q == ord("q"):
                break;
    cv2.destroyAllWindows()

    def solve_math(self, expression):
        """Solve a mathematical expression using sympy."""
        try:
            expression = expression.strip().replace(" ", "")
            expr = sympify(expression, locals={"sin": sin, "cos": cos, "tan": tan, "sqrt": sqrt, "pi": pi})
            result = expr.evalf()
            response = f"The result is {result}"
            self.speak(response)
            self.chat_box_insert(f"Output: {response}\n")
        except Exception as e:
            self.speak("Sorry, I couldn't solve that math problem")
            self.chat_box_insert(f"Output: Sorry, I couldn't solve that math problem: {str(e)}\n")

    def open_calculator(self):
        """Open the Windows Calculator app."""
        try:
            subprocess.run(["start", "calc"], shell=True, check=True)
            self.speak("Opening Calculator")
            self.chat_box_insert("Output: Opening Calculator\n")
        except subprocess.CalledProcessError as e:
            self.speak("Failed to open Calculator")
            self.chat_box_insert(f"Output: Failed to open Calculator: {str(e)}\n")

    def minimize_windows(self):
        """Minimize all windows using Win+M."""
        try:
            pyautogui.hotkey('win', 'm')
            self.speak("Minimizing all windows")
            self.chat_box_insert("Output: Minimizing all windows\n")
        except Exception as e:
            self.speak("Failed to minimize windows")
            self.chat_box_insert(f"Output: Failed to minimize windows: {str(e)}\n")

    def open_search(self):
        """Open Windows search using Win+Q."""
        try:
            pyautogui.hotkey('win', 'q')
            self.speak("Opening search")
            self.chat_box_insert("Output: Opening search\n")
        except Exception as e:
            self.speak("Failed to open search")
            self.chat_box_insert(f"Output: Failed to open search: {str(e)}\n")

    def open_news_widget(self):
        """Open the Windows news widget using Win+W."""
        try:
            pyautogui.hotkey('win', 'w')
            self.speak("Opening news widget")
            self.chat_box_insert("Output: Opening news widget\n")
        except Exception as e:
            self.speak("Failed to open news widget")
            self.chat_box_insert(f"Output: Failed to open news widget: {str(e)}\n")

    def open_run_command(self):
        """Open the Run command dialog using Win+R."""
        try:
            pyautogui.hotkey('win', 'r')
            self.speak("Opening run command")
            self.chat_box_insert("Output: Opening run command\n")
        except Exception as e:
            self.speak("Failed to open run command")
            self.chat_box_insert(f"Output: Failed to open run command: {str(e)}\n")

    def open_settings(self):
        """Open Windows settings using Win+I."""
        try:
            pyautogui.hotkey('win', 'i')
            self.speak("Opening settings")
            self.chat_box_insert("Output: Opening settings\n")
        except Exception as e:
            self.speak("Failed to open settings")
            self.chat_box_insert(f"Output: Failed to open settings: {str(e)}\n")

    def open_about_settings(self):
        """Open About settings using Win+I."""
        try:
            subprocess.run(["start", "ms-settings:about"], shell=True, check=True)
            self.speak("Opening about settings")
            self.chat_box_insert("Output: Opening about settings\n")
        except subprocess.CalledProcessError as e:
            self.speak("Failed to open about settings")
            self.chat_box_insert(f"Output: Failed to open about settings: {str(e)}\n")

    def open_project_screen(self):
        """Open project screen settings using Win+P."""
        try:
            pyautogui.hotkey('win', 'p')
            self.speak("Opening project screen")
            self.chat_box_insert("Output: Opening project screen\n")
        except Exception as e:
            self.speak("Failed to open project screen")
            self.chat_box_insert(f"Output: Failed to open project screen: {str(e)}\n")

    def open_performance_settings(self):
        """Open performance settings using Win+S."""
        try:
            pyautogui.hotkey('win', 's')
            self.speak("Opening performance settings")
            self.chat_box_insert("Output: Opening performance settings\n")
        except Exception as e:
            self.speak("Failed to open performance settings")
            self.chat_box_insert(f"Output: Failed to open performance settings: {str(e)}\n")

    def open_feedback_hub(self):
        """Open Feedback Hub using Win+F."""
        try:
            pyautogui.hotkey('win', 'f')
            self.speak("Opening feedback hub")
            self.chat_box_insert("Output: Opening feedback hub\n")
        except Exception as e:
            self.speak("Failed to open feedback hub")
            self.chat_box_insert(f"Output: Failed to open feedback hub: {str(e)}\n")

    def open_game_bar(self):
        """Open Game Bar using Win+G."""
        try:
            pyautogui.hotkey('win', 'g')
            self.speak("Opening game bar")
            self.chat_box_insert("Output: Opening game bar\n")
        except Exception as e:
            self.speak("Failed to open game bar")
            self.chat_box_insert(f"Output: Failed to open game bar: {str(e)}\n")

    def open_25(self):
        webbrowser.open("https://itiadmission.gujarat.gov.in/")        

    def open_voice_typing(self):
        """Open voice typing using Win+H."""
        try:
            pyautogui.hotkey('win', 'h')
            self.speak("Opening voice typing")
            self.chat_box_insert("Output: Opening voice typing\n")
        except Exception as e:
            self.speak("Failed to open voice typing")
            self.chat_box_insert(f"Output: Failed to open voice typing: {str(e)}\n")

    def open_connect_panel(self):
        """Open connect panel using Win+K."""
        try:
            pyautogui.hotkey('win', 'k')
            self.speak("Opening connect panel")
            self.chat_box_insert("Output: Opening connect panel\n")
        except Exception as e:
            self.speak("Failed to open connect panel")
            self.chat_box_insert(f"Output: Failed to open connect panel: {str(e)}\n")

    def lock_screen(self):
        """Lock the screen using Win+L."""
        try:
            pyautogui.hotkey('win', 'l')
            self.speak("Locking screen")
            self.chat_box_insert("Output: Locking screen\n")
        except Exception as e:
            self.speak("Failed to lock screen")
            self.chat_box_insert(f"Output: Failed to lock screen: {str(e)}\n")

    def open_quick_menu(self):
        """Open quick menu using Win+X."""
        try:
            pyautogui.hotkey('win', 'x')
            self.speak("Opening quick menu")
            self.chat_box_insert("Output: Opening quick menu\n")
        except Exception as e:
            self.speak("Failed to open quick menu")
            self.chat_box_insert(f"Output: Failed to open quick menu: {str(e)}\n")

    def open_cortana(self):
        """Open Cortana using Win+C."""
        try:
            pyautogui.hotkey('win', 'c')
            self.speak("Opening Cortana")
            self.chat_box_insert("Output: Opening Cortana\n")
        except Exception as e:
            self.speak("Failed to open Cortana")
            self.chat_box_insert(f"Output: Failed to open Cortana: {str(e)}\n")

    def open_clipboard_history(self):
        """Open clipboard history using Win+V."""
        try:
            pyautogui.hotkey('win', 'v')
            self.speak("Opening clipboard history")
            self.chat_box_insert("Output: Opening clipboard history\n")
        except Exception as e:
            self.speak("Failed to open clipboard history")
            self.chat_box_insert(f"Output: Failed to open clipboard history: {str(e)}\n")

    def open_notifications(self):
        """Open notifications using Win+N."""
        try:
            pyautogui.hotkey('win', 'n')
            self.speak("Opening notifications")
            self.chat_box_insert("Output: Opening notifications\n")
        except Exception as e:
            self.speak("Failed to open notifications")
            self.chat_box_insert(f"Output: Failed to open notifications: {str(e)}\n")

    def select_all_text(self):
        """Select all text using Ctrl+A."""
        try:
            pyautogui.hotkey('ctrl', 'a')
            self.speak("Selecting all text")
            self.chat_box_insert("Output: Selecting all text\n")
        except Exception as e:
            self.speak("Failed to select all text")
            self.chat_box_insert(f"Output: Failed to select all text: {str(e)}\n")

    def toggle_settings(self):
        """Toggle the settings popup window."""
        if self.settings_popup and self.settings_popup.winfo_exists():
            self.settings_popup.destroy()
            self.settings_popup = None
        else:
            self.show_settings_popup()

    def show_settings_popup(self):
        """Show a popup with available settings."""
        if self.settings_popup and self.settings_popup.winfo_exists():
            return
        self.settings_popup = tk.Toplevel(self.root)
        self.settings_popup.title("Settings")
        listbox = tk.Listbox(self.settings_popup, width=50, height=20)
        for setting in self.settings_list:
            listbox.insert(tk.END, setting)
        listbox.pack(pady=10)

    def toggle_apps(self):
        """Toggle the apps popup window."""
        if self.apps_popup and self.apps_popup.winfo_exists():
            self.apps_popup.destroy()
            self.apps_popup = None
        else:
            self.show_apps_popup()

    def show_apps_popup(self):
        """Show a popup with available apps."""
        if self.apps_popup and self.apps_popup.winfo_exists():
            return
        self.apps_popup = tk.Toplevel(self.root)
        self.apps_popup.title("Apps")
        listbox = tk.Listbox(self.apps_popup, width=50, height=20)
        for app in self.apps_list:
            listbox.insert(tk.END, app)
        listbox.pack(pady=10)

    def open_file_explorer(self):
        """Open File Explorer."""
        try:
            subprocess.run(["explorer"], shell=True, check=True)
            self.speak("Opening File Explorer")
            self.chat_box_insert("Output: Opening File Explorer\n")
        except subprocess.CalledProcessError as e:
            self.speak("Failed to open File Explorer")
            self.chat_box_insert(f"Output: Failed to open File Explorer: {str(e)}\n")

    def open_downloads(self):
        """Open the Downloads folder."""
        try:
            downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
            subprocess.run(["explorer", downloads_path], shell=True, check=True)
            self.speak("Opening Downloads folder")
            self.chat_box_insert("Output: Opening Downloads folder\n")
        except subprocess.CalledProcessError as e:
            self.speak("Failed to open Downloads folder")
            self.chat_box_insert(f"Output: Failed to open Downloads folder: {str(e)}\n")

    def show_all_settings_popup(self):
        """Show a popup with all Windows settings."""
        popup = tk.Toplevel(self.root)
        popup.title("Windows Settings List")
        popup.geometry("500x600")
        popup.configure(bg="white")
        label = tk.Label(popup, text="Settings List", font=("Arial", 14, "bold"), bg="white")
        label.pack(pady=10)
        setting_text = ""
        for name, (_, code) in self.SETTING_MAP.items():
            setting_text += f"{name.title()} ({code})\n"
        text_area = scrolledtext.ScrolledText(popup, wrap=tk.WORD, width=60, height=30, font=("Arial", 10), bg="#f0f0f0")
        text_area.insert(tk.END, setting_text)
        text_area.configure(state='disabled')
        text_area.pack(pady=10)

    def show_about(self):
        """Show information about the assistant."""
        about_popup = tk.Toplevel(self.root)
        about_popup.title("About")
        tk.Label(about_popup, text="Isha Assistant - Your personal desktop assistant").pack(pady=10)
        self.speak("Isha Assistant, your personal desktop assistant")
        self.chat_box_insert("Output: Isha Assistant, your personal desktop assistant\n")

    def handle_settings_apps_commands(self, command):
        """Handle commands to open settings or apps."""
        for name, cmd in self.commands_dict.items():
            if command in [f"open {name.lower()}", f"open {name.lower().replace(' ', '')}", name.lower()]:
                try:
                    if cmd.startswith("http"):
                        webbrowser.open(cmd)
                    elif cmd.startswith("ms-"):
                        subprocess.run(["start", "", cmd], shell=True, check=True)
                    else:
                        subprocess.run(["start", "", cmd], shell=True, check=True)
                    self.speak(f"Opening {name}")
                    self.chat_box_insert(f"Output: Opening {name}\n")
                except subprocess.CalledProcessError as e:
                    self.speak(f"Failed to open {name}")
                    self.chat_box_insert(f"Output: Failed to open {name}: {str(e)}\n")
                return
        # If no match, query Gemini API
        self.query_gemini_api(command)

    def speak(self, text):
        """Speak the given text using text-to-speech in a separate thread."""
        def run_speak():
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                self.chat_box_insert(f"Output: Speech error: {str(e)}\n")
        threading.Thread(target=run_speak, daemon=True).start()

    def play_song(self):
        """Play a song from YouTube or a local file."""
        if self.check_internet():
            playlist_links = [
                "https://youtu.be/bzSTpdcs-EI?si=TPrjRhE4pRVjO0Hh",
                "https://youtu.be/j9GxZ6MtJSU?si=jQM2uGAnbxt356MO",
                "https://youtu.be/AbkEmIgJMcU?si=nCsq6FjQCoE9mfMH",
                "https://youtu.be/tNc2coVC2aw?si=XHFQpaQnOD0fOzOc",
                "https://youtu.be/xPfzx5F-8aw?si=GvwUrqZY7nclNN2M",
                "https://youtu.be/JgDNFQ2RaLQ?si=RJaFIARD3TmmryIp",
                "https://youtu.be/jdqUfW21vAY?si=tbqSj28ZVzxulVEN",
                "https://youtu.be/ax6OrbgS8lI?si=Qu8ATX1PYByTcTam",
                "https://youtu.be/UyoDdroSXXs?si=BENWSEo5AP5dAP7j",
                "https://youtu.be/NW6Dgax2d6I?si=KKqQLtl4g6_dNYCw",
                "https://youtu.be/YUyze3hvKFo?si=4ABKHN-2aqly9eIF",
                "https://youtu.be/n2dVFdqMYGA?si=sE1OQqLurU7LkUHH",
                "https://youtu.be/gPpQNzQP6gE?si=Eji_2ze9U5prBQpz",
                "https://youtu.be/AX6OrbgS8lI?si=l5miVi6KYBdpcxjY",
                "https://youtu.be/TkAiQJzctFY?si=ftSyKFuCJ0ufYHv4",
                "https://youtu.be/TkAiQJzctFY?si=JBG-YdzoTZEAsKgV",
                "https://youtu.be/uFbayWnLGxs?si=–VMABpuHCU2RMP2",
                "https://youtu.be/9KCtZ9r4OAw?si=e7n28CCQ1bL699uR",
                "https://youtu.be/uSb0M_UQE1o?si=gk3WGAU7979W_jBd",
                "https://youtu.be/FudfVyYWNxQ?si=PBCUyE56uU52OsO9"
            ]
            url = random.choice(playlist_links)
            webbrowser.open(url)
            time.sleep(2)
            pyautogui.press("k")
            self.speak("Playing a song from YouTube")
            self.chat_box_insert("Output: Playing a song from YouTube\n")
        else:
            music_dir = os.path.join(os.path.expanduser("~"), "Music")
            music_files = glob.glob(os.path.join(music_dir, "*.mp3")) + glob.glob(os.path.join(music_dir, "*.wav"))
            if music_files:
                music_file = random.choice(music_files)
                subprocess.run(["start", "", music_file], shell=True)
                self.speak("Playing a local music file")
                self.chat_box_insert(f"Output: Playing local music file: {os.path.basename(music_file)}\n")
            else:
                self.speak("No internet connection and no local music files found")
                self.chat_box_insert("Output: No internet connection and no local music files found\n")

    def search_web(self, platform, query):
        """Search on YouTube or Google."""
        if platform == "youtube":
            webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
        elif platform == "google":
            webbrowser.open(f"https://www.google.com/search?q={query}")

    def open_youtube(self):
        """Open YouTube and optionally search for a query."""
        if self.check_internet():
            self.speak("Do you want to search for something on YouTube?")
            query = self.listen()
            if query and query not in ["none", "cancel", "no"]:
                self.search_web("youtube", query)
                self.speak(f"Searching for {query} on YouTube")
                self.chat_box_insert(f"Output: Searching for {query} on YouTube\n")
            else:
                webbrowser.open("https://www.youtube.com")
                self.speak("Opening YouTube")
                self.chat_box_insert("Output: Opening YouTube\n")
        else:
            self.speak("No internet connection. Opening local video folder instead.")
            video_dir = os.path.join(os.path.expanduser("~"), "Videos")
            subprocess.run(["explorer", video_dir], shell=True)
            self.chat_box_insert("Output: Opening local Videos folder\n")

    def open_google(self):
        """Open Google and optionally search for a query."""
        if self.check_internet():
            self.speak("What do you want to search?")
            query = self.listen()
            if query and query not in ["none", "cancel", "no"]:
                self.search_web("google", query)
                self.speak(f"Searching for {query} on Google")
                self.chat_box_insert(f"Output: Searching for {query} on Google\n")
            else:
                webbrowser.open("https://www.google.com")
                self.speak("Opening Google")
                self.chat_box_insert("Output: Opening Google\n")
        else:
            self.speak("No internet connection. Opening local file explorer.")
            subprocess.run(["explorer"], shell=True)
            self.chat_box_insert("Output: Opening local file explorer\n")

    def open_instagram(self):
        """Open Instagram."""
        if self.check_internet():
            webbrowser.open("https://www.instagram.com")
            self.speak("Opening Instagram")
            self.chat_box_insert("Output: Opening Instagram\n")
        else:
            self.speak("Instagram requires an internet connection. Opening local Photos app instead.")
            self.chat_box_insert("Output: Instagram unavailable offline. Opening Photos app instead.\n")
            subprocess.run(["start", "", "microsoft.photos:"], shell=True)

    def login_instagram(self):
        """Log into Instagram using Selenium with GUI input."""
        if not self.check_internet():
            self.speak("Instagram requires an internet connection. Opening local Photos app instead.")
            self.chat_box_insert("Output: Instagram unavailable offline. Opening Photos app instead.\n")
            subprocess.run(["start", "", "microsoft.photos:"], shell=True)
            return

        def run_login():
            try:
                driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
                driver.set_page_load_timeout(30)
                driver.get("https://www.instagram.com/accounts/login/")
                self.root.after(0, self.speak, "Logging into Instagram")
                self.root.after(0, self.chat_box_insert, "Output: Logging into Instagram\n")
                time.sleep(3)

                username = simpledialog.askstring("Input", "Enter Instagram username:", parent=self.root)
                password = simpledialog.askstring("Input", "Enter Instagram password:", parent=self.root, show="*")
                if not username or not password:
                    self.root.after(0, self.speak, "Login cancelled: Username or password not provided")
                    self.root.after(0, self.chat_box_insert, "Output: Login cancelled: Username or password not provided\n")
                    driver.quit()
                    return

                user_input = driver.find_element(By.NAME, "username")
                pass_input = driver.find_element(By.NAME, "password")
                user_input.send_keys(username)
                pass_input.send_keys(password)
                pass_input.send_keys(Keys.RETURN)
                time.sleep(5)
                driver.quit()
                self.root.after(0, self.speak, "Logged into Instagram successfully")
                self.root.after(0, self.chat_box_insert, "Output: Logged into Instagram successfully\n")
            except Exception as e:
                self.root.after(0, self.speak, f"Failed to log into Instagram: {str(e)}")
                self.root.after(0, self.chat_box_insert, f"Output: Failed to log into Instagram: {str(e)}\n")

        threading.Thread(target=run_login, daemon=True).start()

    def open_chatbox(self):
        """Open the hack.chat chatbox."""
        if self.check_internet():
            webbrowser.open("https://hack.chat/?Isha")
            self.speak("Opening chatbox")
            self.chat_box_insert("Output: Opening chatbox\n")
        else:
            self.speak("Chatbox requires an internet connection.")
            self.chat_box_insert("Output: Chatbox requires an internet connection.\n")

    def download_picture(self):
        """Open Pixabay for downloading pictures."""
        if self.check_internet():
            webbrowser.open("https://pixabay.com/")
            self.speak("Opening Pixabay to download pictures")
            self.chat_box_insert("Output: Opening Pixabay to download pictures\n")
        else:
            self.speak("Downloading pictures requires an internet connection.")
            self.chat_box_insert("Output: Downloading pictures requires an internet connection.\n")

    def download_instagram_reel(self):
        """Open a website to download Instagram reels."""
        if self.check_internet():
            webbrowser.open("https://igram.world/reels-downloader/")
            self.speak("Opening Instagram reel downloader")
            self.chat_box_insert("Output: Opening Instagram reel downloader\n")
        else:
            self.speak("Downloading reels requires an internet connection.")
            self.chat_box_insert("Output: Downloading reels requires an internet connection.\n")

    def open_whatsapp(self):
        """Open WhatsApp and send a message if specified."""
        if not self.check_internet():
            self.speak("WhatsApp requires an internet connection. Opening notepad instead.")
            self.chat_box_insert("Output: WhatsApp unavailable offline. Opening notepad instead.\n")
            subprocess.run(["start", "", "notepad"], shell=True)
            return

        self.speak("Please provide a phone number with country code.")
        contact = self.listen()
        if contact and re.match(r"^\+\d{10,15}$", contact):
            self.speak("What message should I send?")
            message = self.listen()
            if message and message not in ["none", "cancel", "no"]:
                try:
                    webbrowser.open("https://web.whatsapp.com")
                    time.sleep(20)
                    pywhatkit.sendwhatmsg_instantly(contact, message, wait_time=20, tab_close=True)
                    self.speak(f"Message sent to {contact}")
                    self.chat_box_insert(f"Output: Message sent to {contact}\n")
                except Exception as e:
                    self.speak(f"Failed to send WhatsApp message: {str(e)}")
                    self.chat_box_insert(f"Output: Failed to send WhatsApp message: {str(e)}\n")
            else:
                self.speak("No message provided")
                self.chat_box_insert("Output: No message provided\n")
        else:
            self.speak("Invalid or no contact provided. Please use country code, e.g., +1234567890")
            self.chat_box_insert("Output: Invalid or no contact provided\n")

    def hello(self):
        """Respond to a greeting."""
        responses = ["Hi!", "Kaise ho?"]
        response = random.choice(responses)
        self.speak(response)
        self.chat_box_insert(f"Output: {response}\n")

    def thank_you_reply(self):
        """Respond to a thank you."""
        responses = ["Welcome, I can help you!", "Welcome!"]
        response = random.choice(responses)
        self.speak(response)
        self.chat_box_insert(f"Output: {response}\n")

    def what_is_your_name(self):
        """Respond with the assistant's name."""
        responses = ["I am Isha", "My name is Isha"]
        response = random.choice(responses)
        self.speak(response)
        self.chat_box_insert(f"Output: {response}\n")

    def morningtime(self):
        """Respond to a morning greeting."""
        responses = ["Good morning", "Morning there, kaise ho?"]
        response = random.choice(responses)
        self.speak(response)
        self.chat_box_insert(f"Output: {response}\n")

    def stop_song(self):
        """Stop the currently playing song."""
        time.sleep(1)
        pyautogui.press('k')
        self.speak("Stopping the song")
        self.chat_box_insert("Output: Stopping the song\n")

    def mute_unmute(self):
        """Toggle mute/unmute for media."""
        time.sleep(1)
        pyautogui.press('m')
        self.speak("Toggling mute/unmute")
        self.chat_box_insert("Output: Toggling mute/unmute\n")

    def full_screen(self):
        """Toggle full screen for media."""
        time.sleep(1)
        pyautogui.press('f')
        self.speak("Toggling full screen")
        self.chat_box_insert("Output: Toggling full screen\n")

    def cmaw21(self):
        """Toggle full screen for media."""
        time.sleep(1)
        pyautogui.press('q')
        self.speak("phone camera is disconnect")
        self.chat_box_insert("Output: camera is disconnect\n")


    def toggle_caption(self):
        """Toggle captions for media."""
        time.sleep(1)
        pyautogui.press('c')
        self.speak("Toggling captions")
        self.chat_box_insert("Output: Toggling captions\n")

    def shutdown_pc(self):
        """Shut down the PC."""
        try:
            subprocess.run(["shutdown", "/s", "/t", "1"], shell=True, check=True)
            self.speak("Shutting down the PC")
            self.chat_box_insert("Output: Shutting down the PC\n")
        except subprocess.CalledProcessError as e:
            self.speak("Failed to shut down the PC")
            self.chat_box_insert(f"Output: Failed to shut down the PC: {str(e)}\n")

    def restart_pc(self):
        """Restart the PC."""
        try:
            subprocess.run(["shutdown", "/r", "/t", "1"], shell=True, check=True)
            self.speak("Restarting the PC")
            self.chat_box_insert("Output: Restarting the PC\n")
        except subprocess.CalledProcessError as e:
            self.speak("Failed to restart the PC")
            self.chat_box_insert(f"Output: Failed to restart the PC: {str(e)}\n")

    def get_weather(self):
        """Fetch weather information for a specified city."""
        if self.check_internet():
            self.speak("Which city's weather do you want to check?")
            city = self.listen()
            if not city or city in ["none", "cancel", "no"]:
                self.speak("No city provided. Please try again.")
                self.chat_box_insert("Output: No city provided. Please try again.\n")
                return
            try:
                response = requests.get(f"https://wttr.in/{city}?format=3")
                response.raise_for_status()
                weather_info = response.text
                with open("weather_cache.txt", "w") as f:
                    f.write(f"{city}:{weather_info}:{int(time.time())}")
                self.speak(weather_info)
                self.chat_box_insert(f"Output: {weather_info}\n")
            except Exception as e:
                self.speak(f"Failed to fetch weather for {city}")
                self.chat_box_insert(f"Output: Failed to fetch weather for {city}: {str(e)}\n")
        else:
            try:
                with open("weather_cache.txt", "r") as f:
                    city, weather_info, timestamp = f.read().split(":", 2)
                    age = int(time.time()) - int(timestamp)
                    if age < 3600:
                        self.speak(f"No internet. Showing cached weather for {city}: {weather_info}")
                        self.chat_box_insert(f"Output: Cached weather for {city}: {weather_info}\n")
                    else:
                        self.speak("No internet and cached weather is too old.")
                        self.chat_box_insert("Output: No internet and cached weather is too old.\n")
            except FileNotFoundError:
                self.speak("No internet connection and no cached weather available.")
                self.chat_box_insert("Output: No internet and no cached weather available.\n")

    def find_now(self):
        """Search for a query on Google or open file explorer offline."""
        if self.check_internet():
            self.speak("Tell me what to search")
            search_query = self.listen()
            if search_query and search_query not in ["none", "cancel", "no"]:
                webbrowser.open(f"https://www.google.com/search?q={search_query}")
                self.speak(f"Searching for {search_query} on Google")
                self.chat_box_insert(f"Output: Searching for {search_query} on Google\n")
            else:
                self.speak("No search query provided")
                self.chat_box_insert("Output: No search query provided\n")
        else:
            self.speak("No internet connection. Opening local file explorer.")
            subprocess.run(["explorer"], shell=True)
            self.chat_box_insert("Output: Opening local file explorer\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = IshaAssistant(root)
    root.mainloop()

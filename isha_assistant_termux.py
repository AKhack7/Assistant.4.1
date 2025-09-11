```python
import datetime
import os
import webbrowser
import time
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
import pywhatkit

# Load environment variables
load_dotenv()

class IshaAssistant:
    """A personal desktop assistant for Termux with text-based command capabilities."""
    def __init__(self):
        # Initialize logging
        logging.basicConfig(filename="isha_assistant.log", level=logging.INFO, 
                           format="%(asctime)s - %(levelname)s - %(message)s")
        
        # Internet check caching
        self.last_internet_check = 0
        self.internet_status = False
        self.internet_check_interval = 10
        
        # Check for Gemini API key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            api_key = input("Enter your Gemini API key (get one from https://aistudio.google.com/app/apikey): ")
            if api_key:
                os.environ["GEMINI_API_KEY"] = api_key
            else:
                print("Output: Gemini API key not provided. AI queries may not work.")
                self.speak("Gemini API key not provided. AI queries may not work.")
        
        self.wish_me()
        self.run()

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

    def speak(self, text):
        """Speak the given text using Termux TTS."""
        try:
            subprocess.run(["termux-tts-speak", text], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Output: Speech error: {str(e)}")
            logging.error(f"Speech error: {str(e)}")

    def wish_me(self):
        """Greet the user based on the time of day."""
        current_hour = datetime.datetime.now().hour
        greeting = (
            "Good morning" if 5 <= current_hour < 12 else
            "Good afternoon" if 12 <= current_hour < 17 else
            "Good evening" if 17 <= current_hour < 21 else
            "Good night"
        )
        print(f"Output: {greeting}")
        self.speak(greeting)

    def listen(self):
        """Get input from the user (text or voice)."""
        try:
            # Try using termux-speech-to-text for voice input
            result = subprocess.run(["termux-speech-to-text"], capture_output=True, text=True, timeout=10)
            query = result.stdout.strip().lower()
            if query:
                return query
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            print("Voice input failed or not detected. Please type your command.")
        return input("Input: ").lower().strip()

    def query_gemini_api(self, query):
        """Send a query to the Google Gemini API and return the response."""
        if not self.check_internet():
            print("Output: Gemini API requires an internet connection.")
            self.speak("This feature requires an internet connection.")
            return

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Output: Gemini API key not found.")
            self.speak("Gemini API key not found.")
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
            print(f"Output: {generated_text}")
            self.speak(generated_text)
        except requests.exceptions.RequestException as e:
            logging.error(f"Gemini API error: {str(e)} - Response: {e.response.text if e.response else 'No response'}")
            print(f"Output: Failed to get a response from the Gemini API: {str(e)}")
            self.speak("Failed to get a response from the Gemini API")

    def process_command(self, command):
        """Process user commands and execute corresponding actions."""
        logging.info(f"Processing command: {command}, Internet: {self.internet_status}")
        print(f"Input: {command}")

        if command.startswith("explain ") or command.startswith("what is ") or command.startswith("tell me about "):
            self.query_gemini_api(command)
        elif command in ["what is the time", "samaye kya ho raha hai", "time"]:
            self.get_time()
        elif command in ["what is the date", "aaj date kya hai", "date"]:
            self.get_date()
        elif command.startswith("solve ") or re.match(r"^\d+\s*[\+\-\*/]\s*\d+", command):
            expression = command[6:] if command.startswith("solve ") else command
            self.solve_math(expression)
        elif command in ["open file explorer", "open file m"]:
            self.open_file_explorer()
        elif command in ["open downloads"]:
            self.open_downloads()
        elif command in ["play song", "play music", "isha play song"]:
            self.play_song()
        elif command in ["youtube", "isha youtube", "manoranjan suru kiya jaaye"]:
            self.open_youtube()
        elif command in ["google", "isha open google", "google open now", "open google"]:
            self.open_google()
        elif command in ["instagram", "isha open instagram", "instagram chalu karo", "gili gili chu", "gili gili chhu", "gili gili suit"]:
            self.open_instagram()
        elif command in ["download photo", "download picture", "isha download photo", "isha download picture", "dd photo", "dd picture"]:
            self.download_picture()
        elif command in ["download reel", "download storie", "download instagram reel", "instagram reel download", "isha download instagram reel", "download instagram stories", "download instagram storie", "isha downloas instagram storie", "isha instagram storie download", "isha instagram stories download", "ist reel"]:
            self.download_instagram_reel()
        elif command in ["whatsapp", "isha whatsapp"]:
            self.open_whatsapp()
        elif command in ["hello", "hello isha", "hi", "hi isha"]:
            self.hello()
        elif command in ["thank you isha", "thank you", "thanks isha"]:
            self.thank_you_reply()
        elif command in ["what you mane", "what is your name"]:
            self.what_is_your_name()
        elif command in ["good morning", "morning", "good morning isha", "isha good morning"]:
            self.morningtime()
        elif command in ["stop song", "stop", "stop music", "isha song band karo"]:
            self.stop_song()
        elif command in ["weather", "isha what is weather", "aaj ka mausam kya hai"]:
            self.get_weather()
        elif command in ["find now", "give me a answer", "isha find now", "search", "search now", "isha search now"]:
            self.find_now()
        elif command == "greet me":
            self.wish_me()
        elif command == "exit":
            print("Output: Exiting Isha Assistant")
            self.speak("Goodbye")
            return False
        else:
            self.query_gemini_api(command)
        return True

    def run(self):
        """Main loop for the assistant."""
        print("Isha Assistant is running. Type 'exit' to quit.")
        while True:
            command = self.listen()
            if not self.process_command(command):
                break

    def get_time(self):
        """Display the current time."""
        try:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            response = f"The current time is {current_time}"
            print(f"Output: {response}")
            self.speak(response)
        except Exception as e:
            print(f"Output: Error retrieving time: {str(e)}")
            self.speak("Error retrieving time")

    def get_date(self):
        """Display the current date."""
        try:
            current_date = datetime.datetime.now().strftime("%B %d, %Y")
            response = f"Today's date is {current_date}"
            print(f"Output: {response}")
            self.speak(response)
        except Exception as e:
            print(f"Output: Error retrieving date: {str(e)}")
            self.speak("Error retrieving date")

    def solve_math(self, expression):
        """Solve a mathematical expression using sympy."""
        try:
            expression = expression.strip().replace(" ", "")
            expr = sympify(expression, locals={"sin": sin, "cos": cos, "tan": tan, "sqrt": sqrt, "pi": pi})
            result = expr.evalf()
            response = f"The result is {result}"
            print(f"Output: {response}")
            self.speak(response)
        except Exception as e:
            print(f"Output: Sorry, I couldn't solve that math problem: {str(e)}")
            self.speak("Sorry, I couldn't solve that math problem")

    def open_file_explorer(self):
        """Open Termux file explorer."""
        try:
            subprocess.run(["termux-open", os.path.expanduser("~")], check=True)
            print("Output: Opening file explorer")
            self.speak("Opening file explorer")
        except subprocess.CalledProcessError as e:
            print(f"Output: Failed to open file explorer: {str(e)}")
            self.speak("Failed to open file explorer")

    def open_downloads(self):
        """Open the Downloads folder."""
        try:
            downloads_path = os.path.join(os.path.expanduser("~"), "downloads")
            subprocess.run(["termux-open", downloads_path], check=True)
            print("Output: Opening Downloads folder")
            self.speak("Opening Downloads folder")
        except subprocess.CalledProcessError as e:
            print(f"Output: Failed to open Downloads folder: {str(e)}")
            self.speak("Failed to open Downloads folder")

    def play_song(self):
        """Play a song from YouTube or a local file."""
        if self.check_internet():
            playlist_links = [
                "https://youtu.be/bzSTpdcs-EI?si=TPrjRhE4pRVjO0Hh",
                "https://youtu.be/j9GxZ6MtJSU?si=jQM2uGAnbxt356MO",
                "https://youtu.be/AbkEmIgJMcU?si=nCsq6FjQCoE9mfMH",
                "https://youtu.be/tNc2coVC2aw?si=XHFQpaQnOD0fOzOc",
                "https://youtu.be/xPfzx5F-8aw?si=GvwUrqZY7nclNN2M",
            ]
            url = random.choice(playlist_links)
            subprocess.run(["termux-open-url", url], check=True)
            print("Output: Playing a song from YouTube")
            self.speak("Playing a song from YouTube")
        else:
            music_dir = os.path.join(os.path.expanduser("~"), "music")
            music_files = glob.glob(os.path.join(music_dir, "*.mp3")) + glob.glob(os.path.join(music_dir, "*.wav"))
            if music_files:
                music_file = random.choice(music_files)
                subprocess.run(["termux-open", music_file], check=True)
                print(f"Output: Playing local music file: {os.path.basename(music_file)}")
                self.speak("Playing a local music file")
            else:
                print("Output: No internet connection and no local music files found")
                self.speak("No internet connection and no local music files found")

    def open_youtube(self):
        """Open YouTube and optionally search for a query."""
        if self.check_internet():
            print("What do you want to search on YouTube? (or type 'none' to open YouTube)")
            self.speak("What do you want to search on YouTube?")
            query = self.listen()
            if query and query not in ["none", "cancel", "no"]:
                url = f"https://www.youtube.com/results?search_query={query}"
                subprocess.run(["termux-open-url", url], check=True)
                print(f"Output: Searching for {query} on YouTube")
                self.speak(f"Searching for {query} on YouTube")
            else:
                subprocess.run(["termux-open-url", "https://www.youtube.com"], check=True)
                print("Output: Opening YouTube")
                self.speak("Opening YouTube")
        else:
            print("Output: No internet connection. Opening local video folder.")
            self.speak("No internet connection. Opening local video folder.")
            video_dir = os.path.join(os.path.expanduser("~"), "videos")
            subprocess.run(["termux-open", video_dir], check=True)

    def open_google(self):
        """Open Google and optionally search for a query."""
        if self.check_internet():
            print("What do you want to search? (or type 'none' to open Google)")
            self.speak("What do you want to search?")
            query = self.listen()
            if query and query not in ["none", "cancel", "no"]:
                url = f"https://www.google.com/search?q={query}"
                subprocess.run(["termux-open-url", url], check=True)
                print(f"Output: Searching for {query} on Google")
                self.speak(f"Searching for {query} on Google")
            else:
                subprocess.run(["termux-open-url", "https://www.google.com"], check=True)
                print("Output: Opening Google")
                self.speak("Opening Google")
        else:
            print("Output: No internet connection. Opening local file explorer.")
            self.speak("No internet connection. Opening local file explorer.")
            subprocess.run(["termux-open", os.path.expanduser("~")], check=True)

    def open_instagram(self):
        """Open Instagram."""
        if self.check_internet():
            subprocess.run(["termux-open-url", "https://www.instagram.com"], check=True)
            print("Output: Opening Instagram")
            self.speak("Opening Instagram")
        else:
            print("Output: Instagram requires an internet connection.")
            self.speak("Instagram requires an internet connection.")

    def download_picture(self):
        """Open Pixabay for downloading pictures."""
        if self.check_internet():
            subprocess.run(["termux-open-url", "https://pixabay.com/"], check=True)
            print("Output: Opening Pixabay to download pictures")
            self.speak("Opening Pixabay to download pictures")
        else:
            print("Output: Downloading pictures requires an internet connection.")
            self.speak("Downloading pictures requires an internet connection.")

    def download_instagram_reel(self):
        """Open a website to download Instagram reels."""
        if self.check_internet():
            subprocess.run(["termux-open-url", "https://igram.world/reels-downloader/"], check=True)
            print("Output: Opening Instagram reel downloader")
            self.speak("Opening Instagram reel downloader")
        else:
            print("Output: Downloading reels requires an internet connection.")
            self.speak("Downloading reels requires an internet connection.")

    def open_whatsapp(self):
        """Open WhatsApp and send a message if specified."""
        if not self.check_internet():
            print("Output: WhatsApp requires an internet connection.")
            self.speak("WhatsApp requires an internet connection.")
            return

        print("Please provide a phone number with country code (e.g., +1234567890):")
        self.speak("Please provide a phone number with country code.")
        contact = self.listen()
        if contact and re.match(r"^\+\d{10,15}$", contact):
            print("What message should I send?")
            self.speak("What message should I send?")
            message = self.listen()
            if message and message not in ["none", "cancel", "no"]:
                try:
                    pywhatkit.sendwhatmsg_instantly(contact, message, wait_time=20, tab_close=True)
                    print(f"Output: Message sent to {contact}")
                    self.speak(f"Message sent to {contact}")
                except Exception as e:
                    print(f"Output: Failed to send WhatsApp message: {str(e)}")
                    self.speak(f"Failed to send WhatsApp message")
            else:
                print("Output: No message provided")
                self.speak("No message provided")
        else:
            print("Output: Invalid or no contact provided")
            self.speak("Invalid or no contact provided")

    def hello(self):
        """Respond to a greeting."""
        responses = ["Hi!", "Kaise ho?"]
        response = random.choice(responses)
        print(f"Output: {response}")
        self.speak(response)

    def thank_you_reply(self):
        """Respond to a thank you."""
        responses = ["Welcome, I can help you!", "Welcome!"]
        response = random.choice(responses)
        print(f"Output: {response}")
        self.speak(response)

    def what_is_your_name(self):
        """Respond with the assistant's name."""
        responses = ["I am Isha", "My name is Isha"]
        response = random.choice(responses)
        print(f"Output: {response}")
        self.speak(response)

    def morningtime(self):
        """Respond to a morning greeting."""
        responses = ["Good morning", "Morning there, kaise ho?"]
        response = random.choice(responses)
        print(f"Output: {response}")
        self.speak(response)

    def stop_song(self):
        """Stop media playback (limited functionality in Termux)."""
        print("Output: Stopping media (not fully supported in Termux)")
        self.speak("Stopping media")

    def get_weather(self):
        """Fetch weather information for a specified city."""
        if self.check_internet():
            print("Which city's weather do you want to check?")
            self.speak("Which city's weather do you want to check?")
            city = self.listen()
            if not city or city in ["none", "cancel", "no"]:
                print("Output: No city provided. Please try again.")
                self.speak("No city provided. Please try again.")
                return
            try:
                response = requests.get(f"https://wttr.in/{city}?format=3")
                response.raise_for_status()
                weather_info = response.text
                with open("weather_cache.txt", "w") as f:
                    f.write(f"{city}:{weather_info}:{int(time.time())}")
                print(f"Output: {weather_info}")
                self.speak(weather_info)
            except Exception as e:
                print(f"Output: Failed to fetch weather for {city}: {str(e)}")
                self.speak(f"Failed to fetch weather for {city}")
        else:
            try:
                with open("weather_cache.txt", "r") as f:
                    city, weather_info, timestamp = f.read().split(":", 2)
                    age = int(time.time()) - int(timestamp)
                    if age < 3600:
                        print(f"Output: Cached weather for {city}: {weather_info}")
                        self.speak(f"No internet. Showing cached weather for {city}: {weather_info}")
                    else:
                        print("Output: No internet and cached weather is too old.")
                        self.speak("No internet and cached weather is too old.")
            except FileNotFoundError:
                print("Output: No internet and no cached weather available.")
                self.speak("No internet and no cached weather available.")

    def find_now(self):
        """Search for a query on Google."""
        if self.check_internet():
            print("Tell me what to search:")
            self.speak("Tell me what to search")
            search_query = self.listen()
            if search_query and search_query not in ["none", "cancel", "no"]:
                subprocess.run(["termux-open-url", f"https://www.google.com/search?q={search_query}"], check=True)
                print(f"Output: Searching for {search_query} on Google")
                self.speak(f"Searching for {search_query} on Google")
            else:
                print("Output: No search query provided")
                self.speak("No search query provided")
        else:
            print("Output: No internet connection. Opening local file explorer.")
            self.speak("No internet connection. Opening local file explorer.")
            subprocess.run(["termux-open", os.path.expanduser("~")], check=True)

if __name__ == "__main__":
    IshaAssistant()
```

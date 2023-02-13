import pyttsx3 
import datetime 
import speech_recognition as sr
import webbrowser as wb
import os

# Code send and return message from chatGPT of openai with api


Home=pyttsx3.init()
voices = Home.getProperty('voices')
Home.setProperty('voice', voices[1].id) 

def speak(audio):
    print('Greenwich: ' + audio)
    Home.say(audio)
    Home.runAndWait()
   
def time():
    Time=datetime.datetime.now().strftime("%I:%M:%p") 
    speak("It is")
    speak(Time)

def welcome():
        hour=datetime.datetime.now().hour
        if hour >= 6 and hour<12:
            speak("Good Morning Sir!")
        elif hour>=12 and hour<18:
            speak("Good Afternoon Sir!")
        elif hour>=18 and hour<24:
            speak("Good Evening Sir!")
        speak("How can I help you, Brian?") 

def command():
    c=sr.Recognizer()
    with sr.Microphone() as source:
        c.pause_threshold=1             
        audio=c.listen(source)
    try:
        query = c.recognize_google(audio, language='en-US')
        print("Brian: " + query)
    except sr.UnknownValueError:
        print('Sorry Brian! I didn\'t get that! Try typing the command!')
        query = str(input("Brian: "))
    return query

if __name__  =="__main__":
    welcome()
    while True:
        query=command().lower()
        #All the command will store in lower case for easy recognition
        if "google" in query:
            speak("What should I search, Brian?")
            search=command().lower()
            url = f"https://google.com/search?q={search}"
            wb.get().open(url)
            speak(f'Here is your {search} on google')
        elif "hello" in query:
            speak("Hi Brian, How can I help You?")
        elif "youtube" in query:
            speak("What should I search, Brian?")
            search=command().lower()
            url = f"https://youtube.com/search?q={search}"
            wb.get().open(url)
            speak(f'Here is your {search} on youtube')
        elif "video" in query:
            video =r"D:\Video.mp4"
            os.startfile(video)
        elif 'time' in query:
            time()
        elif "turn on the light" in query:
            speak("The light is turn on")
        elif "turn off the light" in query:
            speak("The light is turn off")
        elif "goodbye" in query:
            speak("Greenwich is off. Goodbye Brian")
            quit()
        else:
            speak("Sorry Brian! I didn't get that! Please try again")
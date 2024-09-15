import speech_recognition as sr


def takeCommand():
    r = sr.Recognizer()

    with sr.Microphone() as source:

        r.pause_threshold = 0.7
        audio = r.listen(source)

        try:
            print("Recognizing")

            Query = r.recognize_google(audio)
            print("the command is printed=", Query)

        except Exception as e:
            print(e)
            print("Say that again sir")
            return "None"

        return Query


takeCommand()

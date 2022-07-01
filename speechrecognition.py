import speech_recognition as sr

r = sr.Recognizer()


try:
    with sr.Microphone() as source:
        print('Speak Anything : ')
        r.adjust_for_ambient_noise(source, duration=0.2)
        audio = r.listen(source)
        print('Listened')
        print('Loading...')
        text = r.recognize_google(audio)
        text = text.lower()
        print("You said: " + text)
except sr.RequestError as e:
    print("Sorry could not hear; {0}".format(e))
except sr.UnknownValueError:
    print("Sorry could not hear")
import speech_recognition as sr

# Use SpeechRecognition to record 使用语音识别包录制音频
def my_record(rate=16000):
    r = sr.Recognizer()
    with sr.Microphone(sample_rate=rate) as source:
        print("please say something")
        audio = r.listen(source)

    with open("D:\\VS-Python\\voices\\myvoices.wav", "wb") as f:
        f.write(audio.get_wav_data())
    print("录音完成！")

my_record()
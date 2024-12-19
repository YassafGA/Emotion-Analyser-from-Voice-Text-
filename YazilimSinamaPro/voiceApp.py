from flask import Flask, render_template, request, redirect, url_for
import speech_recognition as sr
from bidi.algorithm import get_display
import pyaudio
import wave
from textblob import TextBlob

app = Flask(__name__)

# إعدادات تسجيل الصوت
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5
OUTPUT_FILENAME = "recorded_audio.wav"

def record_audio():
    """
    تسجيل الصوت من المايكروفون وحفظه كملف WAV.
    """
    audio = pyaudio.PyAudio()

    # بدء التسجيل
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    print("Recording...")
    frames = []

    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Recording finished.")

    # إنهاء التسجيل
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # حفظ الصوت إلى ملف
    with wave.open(OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_audio', methods=['POST'])
def process_audio():
    record_audio()  # تسجيل الصوت

    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(OUTPUT_FILENAME) as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.record(source)

            # التعرف على النص
            text = recognizer.recognize_google(audio, language='tr-TR')
            bidi_text = get_display(text)  # معالجة النص ثنائي الاتجاه
            dosya_adi = "transcription.txt"
            with open(dosya_adi, "w", encoding="utf-8") as dosya:
                dosya.write(bidi_text)
            return render_template('index.html', transcription=bidi_text)
    except sr.UnknownValueError:
        return render_template('index.html', error="Could not understand the audio.")
    except sr.RequestError as e:
        return render_template('index.html', error=f"Speech recognition service error: {e}")


def analyze_text_sentiment(text):
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0:
        return "Positive"
    elif analysis.sentiment.polarity < 0:
        return "Negative"
    else:
        return "Neutral"

    
if __name__ == '__main__':
    app.run(debug=True)

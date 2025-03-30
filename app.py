from flask import Flask, request, jsonify, render_template, send_from_directory
import requests
import whisper
import pyttsx3
import tempfile
import os
import threading
import time

app = Flask(__name__)
RASA_SERVER = "http://localhost:5005/webhooks/rest/webhook"

# Load Whisper model
whisper_model = whisper.load_model("base")

# Initialize pyttsx3 for text-to-speech
engine = pyttsx3.init()

# Global lock for speech synthesis
speech_lock = threading.Lock()


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")  # Load chat UI


@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = None
        is_audio = "audio" in request.files

        # If an audio file is received
        if is_audio:
            audio_file = request.files["audio"]
            user_message = speech_to_text(audio_file)

            if not user_message or user_message.strip() == "":
                return jsonify({"text": "I couldn't understand the audio. Please try again."})

        else:
            user_message = request.json.get("message")  # Text message

        if user_message:
            rasa_response = get_rasa_response(user_message)

            if isinstance(rasa_response, list) and rasa_response:
                response = rasa_response[0].get("text")

                # Process text-to-speech only for voice queries
                if is_audio:
                    text_to_speech(response)

                return jsonify({"text": response, "audio": f"/static/output.mp3?t={int(time.time())}" if is_audio else None})

        return jsonify({"text": "Sorry, I didn't understand that."})

    except Exception as e:
        return jsonify({"text": f"Error: {str(e)}"})


def get_rasa_response(message):
    response = requests.post(RASA_SERVER, json={"sender": "user", "message": message})
    return response.json()


def speech_to_text(audio_file):
    with tempfile.NamedTemporaryFile(delete=False) as temp_audio:
        temp_audio.write(audio_file.read())
        temp_audio.close()
        result = whisper_model.transcribe(temp_audio.name)
        os.remove(temp_audio.name)
        return result["text"]


def text_to_speech(text):
    """ Converts text to speech and saves it as an MP3 file """
    with speech_lock:
        engine.save_to_file(text, "static/output.mp3")
        engine.runAndWait()  # Ensure the file is fully written before serving


@app.route("/static/<path:filename>")
def serve_static(filename):
    """ Serve the latest audio file """
    return send_from_directory("static", filename)


if __name__ == "__main__":
    app.run(debug=True, port=5001)

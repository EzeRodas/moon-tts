import os

def synthesize_text():
    """Synthesizes speech from the input string of text."""
    from google.cloud import texttospeech

    text = "Hello there."
    
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'client_auth_demotts.json'

    client = texttospeech.TextToSpeechClient()

    input_text = texttospeech.SynthesisInput(text=text)

    # Note: the voice can also be specified by name.
    # Names of voices can be retrieved with client.list_voices().
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Chirp3-HD-Leda",
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1,
        pitch=1
    )

    response = client.synthesize_speech(
        input=input_text,
        voice=voice,
        audio_config=audio_config,
    )

    # The response's audio_content is binary.
    with open("output.mp3", "wb") as output:
        output.write(response.audio_content)
        print('Audio content written to file "output.mp3"')
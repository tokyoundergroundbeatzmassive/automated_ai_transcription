import os
from deepgram import DeepgramClient, PrerecordedOptions, FileSource

output_path = "/tmp/transcription.txt"
deepgram_api_key = os.getenv('DEEPGRAM_API_KEY')

def format_time(seconds):
    """Convert seconds to HH:MM:SS format"""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

def speech_to_text(audio_input_path):
    try:
        deepgram_client = DeepgramClient(deepgram_api_key)

        with open(audio_input_path, "rb") as file:
            buffer_data = file.read()

        source: FileSource = {"buffer": buffer_data}

        options = PrerecordedOptions(
            model="nova-2-meeting",
            detect_language=True,
            diarize=True,
            utterances=True,
            smart_format=True,
            paragraphs=True,
            utt_split=3
        )
        
        response = deepgram_client.listen.rest.v("1").transcribe_file(source, options)

        with open(output_path, "w", encoding="utf-8") as txtfile:
            for utterance in response.results.utterances:
                start_time = format_time(utterance.start)
                end_time = format_time(utterance.end)
                txtfile.write(f"[{start_time} - {end_time}] [Speaker:{utterance.speaker}] {utterance.transcript}\n")

        print(f"Results have been saved to the text file: {output_path}")
        return output_path, 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

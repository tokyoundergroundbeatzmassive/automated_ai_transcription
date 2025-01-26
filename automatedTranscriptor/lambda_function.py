import os
import json
from dropbox_update import DropboxUpdateNotificationAPI
from dropbox_file_handler import DropboxFileHandler
from stt_deepgram import speech_to_text
from analyze import analyzer
from slack_notifier import send_slack_notification

MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024
SUPPORTED_AUDIO_FORMATS = ('.mp3', '.mp4', '.mp2', '.aac', '.wav', '.flac', '.pcm', '.m4a', '.ogg', '.opus', '.webm',
                           '.MP3', '.MP4', '.MP2', '.AAC', '.WAV', '.FLAC', '.PCM', '.M4A', '.OGG', '.OPUS', '.WEBM')

def lambda_handler(event, context):
    if 'queryStringParameters' in event and 'challenge' in event['queryStringParameters']:
        return {
            'statusCode': 200,
            'body': event['queryStringParameters']['challenge']
        }

    pdb = DropboxUpdateNotificationAPI()
    file_handler = DropboxFileHandler(pdb.access_token)

    try:
        update_files = pdb.get_new_files()
        print(f"Update files: {update_files}")
        print(f"Number of updated files: {len(update_files)}")

        if not update_files:
            print('No updates')
            return {
                'statusCode': 200,
                'body': json.dumps('No updates')
            }

        audio_files = [f for f in update_files if f.lower().endswith(SUPPORTED_AUDIO_FORMATS)]
        if not audio_files:
            print('No audio files to process')
            return {
                'statusCode': 200,
                'body': json.dumps('No audio files to process')
            }

        first_audio_file = audio_files[0]
        print(f"Audio files to process: {first_audio_file}")

        file_metadata = file_handler.get_file_metadata(first_audio_file)
        if file_metadata['size'] > MAX_FILE_SIZE:
            print(f"File {first_audio_file} exceeds the maximum size limit of 2GB. Skipping.")
            return {
                'statusCode': 204,
                'body': json.dumps('File size exceeds limit')
            }

        downloaded_file = file_handler.download_file_to_tmp(first_audio_file)
        print(f"Downloaded file: {downloaded_file}")

        if downloaded_file:
            result = speech_to_text(downloaded_file)
            if result and isinstance(result, tuple) and len(result) == 2:
                transcription_file, status_code = result
                if status_code == 200:
                    print(f"Transcription saved to: {transcription_file}")
                    meeting_summary = analyzer(transcription_file)
                    send_slack_notification(meeting_summary, first_audio_file)
                    
                    try:
                        os.remove(transcription_file)
                        print(f"Deleted temporary transcription file: {transcription_file}")
                    except Exception as e:
                        print(f"Error deleting transcription file {transcription_file}: {str(e)}")
                else:
                    print(f"Speech-to-text conversion failed with status code: {status_code}")
            else:
                print("Speech-to-text conversion failed")

            try:
                os.remove(downloaded_file)
                print(f"Deleted temporary audio file: {downloaded_file}")
            except Exception as e:
                print(f"Error deleting audio file {downloaded_file}: {str(e)}")
        else:
            print("No file was downloaded")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise

    print("Lambda function completed successfully")

    return {
        'statusCode': 200,
        'body': json.dumps('Update processed successfully')
    }
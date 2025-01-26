import os
import json
from openai import OpenAI
from typing import List
from openai.types.chat import ChatCompletionMessageParam

model = "gpt-4o"

openai_api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=openai_api_key)

def read_result(transcription_file):
    with open(transcription_file, "r", encoding="utf-8") as file:
        lines = file.readlines()
    
    transcript = []
    for line in lines:
        parts = line.strip().split("] ", 1)
        if len(parts) == 2:
            time_range, text = parts
            transcript.append(f"{time_range}] {text}")
    
    return "\n".join(transcript)

def analyze_transcript(prompt):
    messages: List[ChatCompletionMessageParam] = [
        {"role": "system", "content": "You are a helpful assistant that analyzes meeting transcripts."},
        {"role": "user", "content": prompt}
    ]
    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0.0,
            messages=messages,
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "get_attendees",
                        "description": "Get the list of attendees from the meeting transcript",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "attendees": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of attendees in the meeting"
                                }
                            },
                            "required": ["attendees"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "get_meeting_summary",
                        "description": "Get a detailed recap of the meeting",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "meeting_summary": {
                                    "type": "string",
                                    "description": "Detailed recap of the meeting"
                                }
                            },
                            "required": ["meeting_summary"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "get_action_items",
                        "description": "Get the list of action items from the meeting",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "action_items": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of action items from the meeting"
                                }
                            },
                            "required": ["action_items"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "get_quote_updates",
                        "description": "Get updates to quotes or proposals mentioned in the meeting",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "quote_updates": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Updates to quotes or proposals mentioned in the meeting"
                                }
                            },
                            "required": ["quote_updates"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "get_pricing_and_dates",
                        "description": "Get pricing updates or key dates mentioned in the meeting",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "pricing_and_dates": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Pricing updates or key dates mentioned in the meeting"
                                }
                            },
                            "required": ["pricing_and_dates"]
                        }
                    }
                }
            ],
            tool_choice="auto"
        )
        
        result = {}
        if response.choices and response.choices[0].message.tool_calls:
            for tool_call in response.choices[0].message.tool_calls:
                function_args = json.loads(tool_call.function.arguments)
                result.update(function_args)
        
        return result
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None 

def analyzer(transcription_file):
    full_text = read_result(transcription_file)
    prompt = f"""
Analyze the following meeting transcript and extract the following information:

1. List of attendees
    - Identify the name of each speakers
        For example:
        - John Smith (Speaker0)
        - Unknown (Speaker1)
        - Sarah Johnson (Speaker2)

2. Detailed recap of the meeting
3. Action items
4. Updates to quotes or proposals
5. Pricing updates or key dates mentioned


Meeting transcript:
{full_text}
"""
    
    result = analyze_transcript(prompt)

    meeting_summary = {
        "List of attendees": "\n".join(result["attendees"]),
        "Meeting Summary": result["meeting_summary"],
        "Action Items": "\n".join(result["action_items"]),
        "Quote/Proposal Updates": "\n".join(result["quote_updates"]),
        "Pricing Updates/Key Dates": "\n".join(result["pricing_and_dates"])
    }

    return meeting_summary

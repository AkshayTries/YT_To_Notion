from flask import Flask, request, jsonify
from langchain_groq import ChatGroq
import requests
import os
import re
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv

app = Flask(__name__)
@app.route('/summarize', methods=['POST'])
def summarize_video():
    data = request.get_json()
    video_id = data.get('video_id')
    transcript = extract_transcript(video_id)
    summary = summarise(transcript)
    extracted_title, extracted_summary = extract_fields(summary)
    response = create_page(extracted_title, extracted_summary)
    print(response.text)
    return jsonify({"status": "done", "notion_response": response.status_code})

load_dotenv()

model = ChatGroq(model="llama-3.3-70b-versatile",temperature=0)


NOTION_TOKEN = os.getenv('NOTION_INTEGRATION_KEY')


PARENT_PAGE_ID = os.getenv('PARENT_PAGE_ID')

headers = {
  "Authorization": f"Bearer {NOTION_TOKEN}",
  "Notion-Version": "2022-06-28",
  "Content-Type": "application/json",
}

#function to create a new child page with content
def create_page(extracted_title,extracted_summary):
    payload = {
    "parent": { "page_id": PARENT_PAGE_ID },
    "properties": {
        "title": [
            {
                "type": "text",
                "text": {
                    "content": extracted_title,
                },
            }
        ]
    },
    "icon": {
    "type": "emoji",
    "emoji": "🥑"
  },
  "cover": {
    "type": "external",
    "external": {
      "url": "https://images.unsplash.com/photo-1533551268962-824e232f7ee1?q=80&w=1932&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
    }
  },
    "children": [
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": extracted_title,
                        },
                    }
                ]
            }
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": extracted_summary,
                        }
                    }
                ]
            }
        }
    ]
}
    response = requests.post("https://api.notion.com/v1/pages", headers=headers, json=payload)
    return response
    
#extract the transcript of the YT video 
def extract_transcript(video_id):
    ytt_api = YouTubeTranscriptApi()
    total_transcript = ytt_api.fetch(video_id)
    transcript = ""
    for snippet in total_transcript:
        transcript+=snippet.text
    return transcript

#summarise the transcript using llama2
def summarise(transcript):
    url = "http://localhost:11434/api/generate"
    prompt ="Give a title for the text below, and summarise it in great detail but in short that is in less than 600 words please, in the following format Title: Summary: "
    prompt +=transcript
    # response = requests.post(url,json={
    #     "model":"llama2",
    #     "prompt":prompt,
    #     "stream":False
    # })

    # summary = response.json()
    # return summary['response']
    response = model.invoke(prompt).content
    return response

#extract the title, and, summary of the text from the model (llama2)
def extract_fields(summary):
  match = re.search(r"\**Title:\**\s*(.*?)\s*\**Summary:\**\s*(.*)", summary, re.DOTALL)
  if match:
    extracted_title = match.group(1)
    extracted_summary = match.group(2)
    return extracted_title,extracted_summary
  else:
    print("No match")
    print("ABORTING......")
    exit()
  
#main function to run everything
def run():
  video_id = "Fv2Y1odMjvE"
  transcript = extract_transcript(video_id)
  summary = summarise(transcript)
  extracted_title,extracted_summary = extract_fields(summary)
  response = create_page(extracted_title,extracted_summary)
  print("rser")
  print(response.status_code)
  print(response.text)




if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

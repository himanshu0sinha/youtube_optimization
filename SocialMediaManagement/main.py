import pandas as pd
import os
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import datetime
import requests
import facebook
from linkedin_api import Linkedin
# Replace 'data.xlsx' with the name of your Excel file
df = pd.read_excel('data.xlsx')

# Extract the columns you need
columns = ['Title', 'Description', 'File_Path', 'Platform',
           'Date_Time', 'Tags', 'Thumbnail', 'Privacy', 'Comments']
data = df[columns]

# Print the data
print(f"We're Uploading on ",df["Platform"][0])

if df["Platform"][0] == "Youtube":

    # Set up credentials
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/youtube.upload'])
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = google.auth.OAuth2FlowFromClientSecrets('token.json',
                                                           ['https://www.googleapis.com/auth/youtube.upload'])
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Build the YouTube API client
    youtube = build('youtube', 'v3', credentials=creds)

    # Set up metadata for the video
    scheduled_time = datetime.datetime(df["Date_Time"][0])
    body = {
        'snippet': {
            'title': df["Title"][0],
            'description': df["Description"][0],
            'tags': df["Tags"][0]
        },
        'status': {
            'privacyStatus': df["Privacy"][0],
            'publishAt': scheduled_time.isoformat() + '.000Z',  # Convert scheduled time to ISO 8601 format
            'commentingEnabled': df["Comments"][0]  # Set to True or False to enable or disable comments, respectively
        }
    }

    # Set up the video file to upload
    video_file = MediaFileUpload('video.mp4')
    thumbnail_file = MediaFileUpload('image.jpg')

    # Call the API to upload the video
    try:
        video_response = youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=video_file
        ).execute()

        # Set up metadata for the thumbnail
        thumbnail_body = {
            'videoId': video_response['id'],
            'media_object': thumbnail_file
        }

        # Call the API to upload the thumbnail
        thumbnail_response = youtube.thumbnails().set(
            videoId=video_response['id'],
            media_body=thumbnail_file
        ).execute()

        print(f'Successful upload! Video ID: {video_response["id"]}')
    except HttpError as e:
        print(f'An error occurred: {e}')

if df["Platform"][1] == "LinkedIn":
    # Set up the LinkedIn API client
    linkedin_username = ""
    linkedin_password = ""
    linkedin = Linkedin(linkedin_username, linkedin_password)

    # Define the video upload properties
    video_title = df["Title"][1]
    video_description = df["Description"][1]
    video_path = "video.mp4"
    video_tags = df["Tags"][1]
    enable_comments = df['Comments'][1]  # set to False to disable comments
    thumbnail_path = "image.jpg"
    privacy = df["Privacy"][1] # set to 'anyone' or 'connections'
    date_time = df["Date_Time"][1]

    # Upload the video
    try:
        # Set up the video properties
        video_properties = {
            'title': video_title,
            'description': video_description,
            'tags': video_tags,
            'commentaryEnabled': enable_comments,
            'thumbnail': thumbnail_path,
            'visibility': {
                'com.linkedin.ugc.MemberNetworkVisibility': privacy
            },
            'specificContent': {
                'com.linkedin.ugc.ShareContent': {
                    'media': [
                        {
                            'status': 'READY',
                            'description': {
                                'text': video_description
                            },
                            'originalUrl': video_path,
                            'title': {
                                'text': video_title
                            },
                            'thumbnails': [
                                {
                                    'resolvedUrl': thumbnail_path
                                }
                            ],
                            'publishingTimestamp': date_time
                        }
                    ],
                    'shareCommentary': {
                        'text': video_description
                    }
                }
            }
        }

        # Upload the video to LinkedIn
        response = linkedin.post_video(video_properties)

        if response:
            print('Video uploaded successfully!')
        else:
            print('Error uploading video.')
    except Exception as e:
        print('Error:', e)


if df["Platform"][2] == "Facebook":
    # Define Facebook access token
    access_token = "<your_access_token>"

    # Define Facebook Graph API version
    api_version = "v11.0"

    # Define video file path
    video_file_path = "video.mp4"

    # Define video metadata
    video_title = df["Title"][2]
    video_description = df["Description"][2]
    video_tags = df["Tags"][2]
    video_privacy = df["Privacy"][2]
    video_enable_comments = df['Comments'][2]
    video_publish_date = df["Date_Time"][2]

    # Create a Facebook Graph API object
    graph = facebook.GraphAPI(access_token=access_token, version=api_version)

    # Upload the video
    with open(video_file_path, "rb") as video_file:
        video_id = graph.put_video(
            video_file,
            title=video_title,
            description=video_description,
            tags=video_tags,
            privacy=video_privacy,
            allow_comments=video_enable_comments,
            published=video_publish_date
        )

    # Print the video ID
    print(f"Video uploaded successfully. Video ID: {video_id}")


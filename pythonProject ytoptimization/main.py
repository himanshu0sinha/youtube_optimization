import os
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Set up YouTube Data API credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "cred.json"

# Define YouTube Data API service
api_service_name = "youtube"
api_version = "v3"
credentials, _ = google.auth.default()
youtube = build(api_service_name, api_version, credentials=credentials)

# Function to fetch video metadata
def fetch_video_metadata(video_id):
    try:
        # Call the YouTube Data API to fetch video details
        video_response = youtube.videos().list(
            part="snippet,statistics",
            id=video_id
        ).execute()

        # Extract relevant metadata from the response
        video_metadata = {}
        if video_response["items"]:
            video = video_response["items"][0]
            video_metadata["title"] = video["snippet"]["title"]
            video_metadata["description"] = video["snippet"]["description"]
            video_metadata["tags"] = video["snippet"]["tags"]
            video_metadata["views"] = int(video["statistics"]["viewCount"])
            return video_metadata

    except HttpError as e:
        print(f"An error occurred: {e}")
        return None

# Function to analyze video tags
def analyze_video_tags(video_metadata):
    if video_metadata:
        # Fetch the tags of the given video
        video_tags = video_metadata["tags"]
        print(f"Tags of the given video: {video_tags}")

        # Call the YouTube Data API to fetch the top videos for comparison
        top_videos_response = youtube.search().list(
            part="snippet",
            type="video",
            q=video_metadata["title"],
            maxResults=5,  # Fetch top 5 videos for comparison
            fields="items(id(videoId),snippet(tags))",
            order="viewCount"
        ).execute()

        top_video_tags = []
        for top_video in top_videos_response["items"]:
            top_video_tags.extend(top_video["snippet"]["tags"])

        # Find the differences between video tags and top video tags
        tag_differences = list(set(video_tags) - set(top_video_tags))

        if tag_differences:
            print(f"Tags that can be changed: {tag_differences}")
        else:
            print("No tag changes suggested.")

    else:
        print("Unable to fetch video metadata.")

# Function to update video tags
def update_video_tags(video_id, new_tags):
    try:
        # Call the YouTube Data API to update the video tags
        youtube.videos().update(
            part="snippet",
            body={
                "id": video_id,
                "snippet": {
                    "tags": new_tags
                }
            }
        ).execute()

        print("Video tags updated successfully.")
    except HttpError as e:
        print(f"An error occurred: {e}")

# Take input for YouTube video URL
video_url = input("Enter YouTube video URL: ")
# Extract video ID from the URL
video_id = video_url.split("v=")[1]

# Fetch video metadata by video ID
video_metadata = fetch_video_metadata(video_id)

# Analyze video tags
analyze_video_tags(video_metadata)

# Suggest tag changes (you can modify this list as needed)
suggested_tags = ["suggested_tag_1", "suggested_tag_2"]

# Update video tags
update_video_tags(video_id, suggested_tags)
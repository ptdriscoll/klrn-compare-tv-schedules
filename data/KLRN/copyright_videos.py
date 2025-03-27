'''
conda create --name youtube-api python=3.8
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
pip install requests
'''

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Path to your client_secret.json file
CLIENT_SECRETS_FILE = 'path/to/your/client_secret.json'

# Stored refresh token
REFRESH_TOKEN = 'your_refresh_token_here'

# Scopes required for YouTube Data API
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

def get_authenticated_service():
    credentials = Credentials.from_authorized_user_info(
        {
            "refresh_token": REFRESH_TOKEN,
            "client_id": "YOUR_CLIENT_ID",
            "client_secret": "YOUR_CLIENT_SECRET",
            "token": "YOUR_ACCESS_TOKEN"  # Optional, can be left out if not used
        },
        scopes=SCOPES
    )
    return build('youtube', 'v3', credentials=credentials)

def get_video_ids(youtube):
    request = youtube.search().list(
        part="id",
        channelId='YOUR_CHANNEL_ID',
        maxResults=50,
        order='date'
    )
    response = request.execute()
    return [item['id']['videoId'] for item in response.get('items', []) if item['id']['kind'] == 'youtube#video']

def get_video_details(youtube, video_ids):
    request = youtube.videos().list(
        part="id,snippet,contentDetails,status",
        id=','.join(video_ids)
    )
    response = request.execute()
    return response.get('items', [])

def get_videos_with_claims():
    youtube = get_authenticated_service()
    video_ids = get_video_ids(youtube)
    if not video_ids:
        return []
    video_details = get_video_details(youtube, video_ids)
    claimed_videos = []
    for item in video_details:
        if 'contentDetails' in item and 'contentRating' in item['contentDetails']:
            if 'ytRating' in item['contentDetails']['contentRating']:
                claimed_videos.append({
                    'id': item['id'],
                    'title': item['snippet']['title'],
                    'status': item['status']['privacyStatus']
                })
    return claimed_videos

# Fetch and print videos with claims
videos = get_videos_with_claims()
for video in videos:
    print(f"Video ID: {video['id']}, Title: {video['title']}, Status: {video['status']}")

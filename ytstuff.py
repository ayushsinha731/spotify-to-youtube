import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Load or refresh credentials
credentials = None

def update_token_file(credentials):
    with open("token.pickle", "wb") as f:
        print("Saving credentials for future use...")
        pickle.dump(credentials, f)

# Load the credentials from the token.pickle file if it exists
if os.path.exists("token.pickle"):
    print("Loading credentials from pickle file...")
    with open("token.pickle", "rb") as token:
        credentials = pickle.load(token)

# Refresh the token if it has expired
if credentials and credentials.expired and credentials.refresh_token:
    print("Refreshing access token...")
    credentials.refresh(Request())
    update_token_file(credentials)

# If no credentials, prompt the user to log in
if not credentials:
    print("Fetching new tokens...")
    flow = InstalledAppFlow.from_client_secrets_file("yt_secrets.json", scopes=["https://www.googleapis.com/auth/youtube.force-ssl"])
    flow.run_local_server(port=8080, prompt='consent', authorization_prompt_message="")
    credentials = flow.credentials
    update_token_file(credentials)

# Build the YouTube service object
youtube = build("youtube", 'v3', credentials=credentials)

def create_youtube_playlist(playlist_name):
    """Create a new YouTube playlist."""
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": playlist_name,
                "description": "A playlist created with the API",
                "tags": ["API", "Playlist"],
                "defaultLanguage": "en"
            },
            "status": {
                "privacyStatus": "private"
            }
        }
    )
    response = request.execute()
    return response['id']

def search_video_id(song_name):
    """Search for a video ID on YouTube by song name."""
    request = youtube.search().list(
        part="snippet",
        q=song_name,
        type="video",
        maxResults=1
    )
    response = request.execute()
    items = response.get("items")
    if items:
        return items[0]["id"]["videoId"]
    return None

def add_video_to_playlist(playlist_id, video_id):
    """Add a video to a YouTube playlist."""
    request = youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
    )
    request.execute()

list_of_playlists_and_songs = None
with open('playlist_details.pickle','rb') as f:
    list_of_playlists_and_songs=pickle.load(f)

for playlist_name, songs in list_of_playlists_and_songs:
    playlist_id = create_youtube_playlist(playlist_name)
    for song in songs:
        video_id = search_video_id(song)
        if video_id:
            add_video_to_playlist(playlist_id, video_id)
            print(f"Added {song} to {playlist_name}")
        else:
            print(f"Could not find {song} on YouTube")


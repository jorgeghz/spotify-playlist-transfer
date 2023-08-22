import spotipy
from spotipy.oauth2 import SpotifyOAuth
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
import json

# Load configuration from JSON file
with open('config.json') as config_file:
    config = json.load(config_file)

# Spotify API credentials
SPOTIPY_CLIENT_ID = config['spotify']['client_id']
SPOTIPY_CLIENT_SECRET = config['spotify']['client_secret']
SPOTIPY_REDIRECT_URI = 'http://localhost'
SCOPE = 'user-library-read playlist-read-private'

# YouTube API credentials
YOUTUBE_API_KEY = config['youtube']['api_key']
YOUTUBE_CLIENT_SECRET_JSON_FILE = config['youtube']['client_secret_json_file']
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'


def print_spotify_playlists(sp,playlists):
    print("Your Spotify playlists:")
    print("=========================")
    
    for idx, playlist in enumerate(playlists['items'], start=1):
        print(f"{idx}. {playlist['name']} - {playlist['tracks']['total']} tracks")
        
        playlist_tracks = sp.playlist_tracks(playlist['id'])
        for track_idx, track in enumerate(playlist_tracks['items'], start=1):
            track_name = track['track']['name']
            track_artist = track['track']['artists'][0]['name']
            print(f"  {track_idx}. {track_name} by {track_artist}")

# Function to create or retrieve YouTube playlist video IDs
def get_youtube_video_ids(youtube, playlist_id):
    video_ids = []

    # Retrieve existing videos in the YouTube playlist
    playlist_items = youtube.playlistItems().list(
        part='snippet',
        playlistId=playlist_id,
        maxResults=50  # Adjust as needed
    ).execute()

    for item in playlist_items['items']:
        video_ids.append(item['snippet']['resourceId']['videoId'])

    return video_ids

def create_youtube_playlist(youtube, title, description):
    # Create a new playlist on YouTube
    playlist_insert_response = youtube.playlists().insert(
        part='snippet,status',
        body={
            'snippet': {
                'title': title,
                'description': description,
            },
            'status': {
                'privacyStatus': 'private',  # You can adjust privacy settings
            },
        }
    ).execute()

    return playlist_insert_response['id']

def get_authenticated_youtube_service():
    flow = InstalledAppFlow.from_client_secrets_file(
        YOUTUBE_CLIENT_SECRET_JSON_FILE,
        scopes=['https://www.googleapis.com/auth/youtube']
    )
    flow.redirect_uri='http://localhost/'
    credentials = flow.run_local_server(port=0)
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=credentials)
    return youtube

def create_youtube_playlist_if_not_exist(youtube, playlist_name):
    try:
        # Create a YouTube playlist if it doesn't exist
        youtube_playlist_id = create_youtube_playlist(youtube, playlist_name, "Created from Spotify")
        return youtube_playlist_id
    except HttpError as e:
        print(f"An error occurred: {e}")
        return None

def add_track_to_youtube_playlist(youtube, youtube_playlist_id, video_id, track_name, track_artist):
    try:
        # Add the video to the YouTube playlist
        youtube.playlistItems().insert(
            part='snippet',
            body={
                'snippet': {
                    'playlistId': youtube_playlist_id,
                    'position': 0,
                    'resourceId': {
                        'kind': 'youtube#video',
                        'videoId': video_id
                    }
                }
            }
        ).execute()
        print(f"Added {track_name} by {track_artist} to YouTube playlist")
    except HttpError as e:
        print(f"An error occurred: {e}")

def check_youtube_quota(youtube):
    try:
        # Make a minimal request to check quota availability
        youtube.videos().list(
            part='id',
            id='dummy_id',
            maxResults=1
        ).execute()

    except HttpError as e:
        if "quotaExceeded" in str(e):
            print("YouTube API quota exceeded. Aborting the process.")
            return False
        else:
            print(f"An error occurred while checking YouTube API quota: {e}")
            return True

    return True


def main():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=SPOTIPY_REDIRECT_URI, scope=SCOPE))

    youtube = get_authenticated_youtube_service()

    # Retrieve user's Spotify playlists
    playlists = sp.current_user_playlists()

    print_spotify_playlists(sp, playlists)

    if not check_youtube_quota(youtube):
        return

    # Loop through Spotify playlists
    for playlist in playlists['items']:
        playlist_name = playlist['name']
        playlist_tracks = sp.playlist_tracks(playlist['id'])

        # Create a similar playlist on YouTube if it doesn't exist
        youtube_playlist_id = create_youtube_playlist_if_not_exist(youtube, playlist_name)

        if youtube_playlist_id:
            # Get YouTube video IDs in the playlist
            youtube_video_ids = get_youtube_video_ids(youtube, youtube_playlist_id)

            # Loop through tracks in the playlist
            for track in playlist_tracks['items']:
                track_name = track['track']['name']
                track_artist = track['track']['artists'][0]['name']

                # Search for the track on YouTube using its name and artist
                search_response = youtube.search().list(
                    q=f"{track_name} {track_artist}",
                    part='id',
                    maxResults=1
                ).execute()

                if search_response.get('items'):
                    video_id = search_response['items'][0]['id']['videoId']

                    # Check if the video ID is already in the YouTube playlist
                    if video_id not in youtube_video_ids:
                        add_track_to_youtube_playlist(youtube, youtube_playlist_id, video_id, track_name, track_artist)
                else:
                    print(f"No video found for track: {track_name} by {track_artist}")


if __name__ == '__main__':
    main()
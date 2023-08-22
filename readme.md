vbnet
Copy code
# Spotify to YouTube Playlist Transfer

This script allows you to transfer your Spotify playlists to YouTube by creating similar playlists and adding the tracks to them.

## Prerequisites

- Python 3.x
- Pip (Python package manager)

## Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/spotify-to-youtube-playlist-transfer.git
cd spotify-to-youtube-playlist-transfer
```


Create a config.json file in the root directory with your API credentials. Example structure:

```json
{
    "spotify": {
        "client_id": "your_spotify_client_id",
        "client_secret": "your_spotify_client_secret"
    },
    "youtube": {
        "api_key": "your_youtube_api_key",
        "client_secret_json_file": "path_to_youtube_client_secret_json_file.json"
    }
}
```
Usage
Run the script:

```bash
Copy code
python spotify_playlist_transfer.py
```

The script will prompt you to authorize Spotify and YouTube. Follow the prompts to complete the authorization process.

The script will list your Spotify playlists. It will then create similar playlists on YouTube and add the tracks.

If your YouTube API quota is exceeded, the script will abort and print a message.

Notes:

    The SPOTIPY_REDIRECT_URI in the script should match the redirect URI set for your Spotify app.
    The SCOPE variable defines the permissions the script requests from Spotify. Adjust as needed.
    The maxResults parameter in get_youtube_video_ids controls how many videos are retrieved from YouTube.
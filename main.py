from uuid import uuid4
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from youtubesearchpython import (
    VideosSearch, Playlist, Suggestions, PlaylistsSearch)
from database import insert_file, get_file
from youtubevideo import YoutubeVideo
from dotenv import load_dotenv
from pydrive import upload_file

app = FastAPI()

load_dotenv()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get('/')
async def index():
    return "welcome to pytvd api"


@app.get('/suggestions')
async def get_suggestions(term: str):
    suggestions = Suggestions(language='en', region='US')
    results = suggestions.get(term)['result']
    return results


@app.get('/search/videos')
async def search_video(term: str):
    search = VideosSearch(term, limit=20)
    results = search.result()['result']
    return results


@app.get("/search/playlists")
async def search_for_playlists(term: str):
    search = PlaylistsSearch(term, limit=20)
    results = search.result()['result']
    return results


@app.get('/playlist/{id}')
async def get_playlist(id: str):
    playlist_videos = Playlist.getVideos(
        f"https://www.youtube.com/playlist?list={id}", limit=20)
    return playlist_videos


@app.get("/info/{id}")
async def get_video_info(id: str):
    url = f"https://youtube.com/watch?v={id}"
    yt = YoutubeVideo(url)
    videoDetails = yt.get_details()
    streams = yt.get_streams()
    return {"videoDetails": videoDetails, "formats": streams}


@app.get("/download/{id}/{itag}")
async def download(id: str, itag: str):
    # check if file has been downloaded already
    file = await get_file(id, itag)
    if file:
        return f"https://pytvdd.herokuapp.com/download?file={file['_id']}"

    url = f"https://youtube.com/watch?v={id}"
    yt = YoutubeVideo(url)
    title = yt.video.title
    file = yt.download(itag)
    file_id = upload_file(file.get("path"))
    file_size = os.path.getsize(file.get("path"))
    file_ext = "mp3" if file.get("type") == "audio" else "mp4"

    inserted_id = await insert_file({"title": title, "itag": itag, "file_id": file_id, "video_id": id, "file_size": file_size, "ext": file_ext})

    return f"https://pytvdd.herokuapp.com/download?file={inserted_id}"


@app.get("/stream/{id}")
async def get_stream(id: str):
    url = f"https://youtube.com/watch?v={id}"
    yt = YoutubeVideo(url)
    streaming_data = yt.streaming_data()
    return streaming_data

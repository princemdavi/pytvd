from uuid import uuid4
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from youtubesearchpython import (VideosSearch, Playlist, Suggestions)
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


@app.get('/search')
async def search_video(term: str):
    search = VideosSearch(term, limit=20)
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
        return f"https://pytvdd.herokuapp.com/dl/file?{file['file_id']}&title={file['title']}"

    url = f"https://youtube.com/watch?v={id}"
    yt = YoutubeVideo(url)
    title = yt.video.title
    file = yt.download(itag)
    file_id = file['path'].split("/")[1]
    upload_file(file.get("path"), file_id)
    inserted_file = await insert_file(title, itag, file_id, id)
    return f"https://dl.pytvd.com/file?{inserted_file}"

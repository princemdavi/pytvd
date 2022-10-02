import uvicorn
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
from pytube import YouTube, Playlist, Search
from youtubevideo import YoutubeVideo

app = FastAPI()

app.add_middleware(
    CORSMiddleware, 
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]    
)

@app.get('/')
async def index():
   return "welcome to pytvd api"

@app.get("/search")
async def search(q: str):
  search = Search(q)
  return search.results
  
@app.get("/video")
async def get_video(url: str):
  yt = YoutubeVideo(url)
  videoDetails = yt.get_details()
  streams = yt.get_streams()
  
  return {"videoDetails": videoDetails, "formats": streams}
  
def remove_file(path: str):
  os.remove(path)

@app.get("/download")
async def download(url: str, media: str, background_tasks=BackgroundTasks, itag: str | None = None):
  
  if media == "video": 
    if not itag: return "please provide itag of the video to be downloaded"
    
  yt = YoutubeVideo(url)
  title = yt.video.title
  
  if media == "audio":
    audio_path = yt.download_audio()
    # background_tasks.add_task(remove_file, path=audio_path)
    return FileResponse(path = audio_path, filename = f"{title}.mp3")
  elif media == "video":
    video_path = yt.download_video(itag)
    # background_tasks.add_task(remove_file, path=video_path)
    return FileResponse(path = video_path, filename = f"{title}.mp4")
  else:
    return "media query parameter can only be audio or video"

@app.get("/playlist")
async def get_playlist(url: str):
  p = Playlist(url)
  video_urls = p.video_urls.gen
  return video_urls
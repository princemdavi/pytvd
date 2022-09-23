import uvicorn
from fastapi import FastAPI
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

@app.get("/search"):
async def search(q: str):
  search = Search(q)
  return search.results
  
@app.get("/video")
async def get_video(url: str):
  yt = YoutubeVideo(url)
  videoDetails = yt.get_details()
  streams = yt.get_streams()
  
  return {"videoDetails": videoDetails, "formats": streams}

@app.get("/download")
async def download(url: str, media: str, itag: str | None = None):
  
  if media == "video": 
    if not itag: return "please provide itag of the video to be downloaded"
    
  yt = YoutubeVideo(url)
  title = yt.title
  
  if media == "audio":
    audio_path = yt.download_audio()
    
    return FileResponse(path = audio_path, filename = f"{title}.mp3")
  elif media == "video":
    video_path = yt.download_video(itag)
    return FileResponse(path = video_path, filename = f"{title}.mp4")
  else:
    return "media query parameter can only be audio or video"

@app.get("/playlist")
async def get_playlist(url: str):
  p = Playlist(url)
  video_urls = p.video_urls.gen
  
  videos = []
  
  for video_url in video_urls:
    yt = YoutubeVideo(video_url)
    videoDetails = yt.get_details()
    streams = yt.get_streams()
    
    videos.append({"videoDetails": videoDetails, "formats": streams})
    
  return video_urls
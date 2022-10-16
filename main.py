from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
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
  
@app.get("/info/{id}")
async def get_video_info(id: str):
  url = f"https://youtube.com/watch?v={id}"
  yt = YoutubeVideo(url)
  videoDetails = yt.get_details()
  streams = yt.get_streams()
  
  return {"videoDetails": videoDetails, "formats": streams}

@app.get("/download/{id}/{itag}")
async def download(id: str, itag: str):
  url = f"https://youtube.com/watch?v={id}"
  yt = YoutubeVideo(url)
  title = yt.video.title
  file = yt.download(itag)
  
  return file.path
 
import subprocess
import requests
from fastapi.encoders import jsonable_encoder
from pytube import YouTube
import ffmpeg
from datetime import datetime
import os
from math import floor, ceil
import uuid
import time
from db import File

class YoutubeVideo():
  def __init__(self, url):
        self.url = url
        self.video = YouTube(self.url)
        
  def convert_bytes(self, size):
      for i in ['bytes', 'KB', 'MB', 'GB', 'TB']:
          if size < 1024.0:
              return "%3.1f %s" % (size, i)
          size /= 1024.0

      return filesize
      
  def num_formatter(self, num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])
    
  def seconds_to_time(self, secs):
    hours = floor(secs / (60 * 60))
    minutes = floor((secs % (60 * 60)) / 60)
    seconds = ceil((secs % (60 * 60)) % 60)
  
    return f"{ f'{hours}:' if hours else ''}{ f'{minutes}:' if minutes else ''}{ seconds if seconds else '00'}"
    
  def get_details(self):
    title = self.video.title
    thumbnail = self.video.thumbnail_url
    duration = self.seconds_to_time(self.video.length)
    publish_date = datetime.strftime(self.video.publish_date, '%d.%m.%Y')
    views = self.num_formatter(self.video.views)
    author = self.video.author
    video_url = self.url
    
    video_details = {
      "title": title, 
      "author": author,
      "publish_date": publish_date,
      "duration": duration,
      "views": views,
      "thumbnail": thumbnail,
      "video_url": video_url
    }
    return video_details
    
  def get_streams(self):
    vstreams = jsonable_encoder(self.video.streams.filter(subtype='mp4', only_video=True).order_by("resolution").desc())["fmt_streams"] #video streams with no audio
    
    astream = jsonable_encoder(self.video.streams.get_audio_only()) #best audio stream
    
    fvstreams = [] #filtered video streams
    mastream = {"itag": astream["itag"], "formatted_size": self.convert_bytes(astream["_filesize"]), "raw_size": astream["_filesize"]} #modified audio stream
    
    for vstream in vstreams:
      #extract res property from vstreams dicts
      resolutions = list(map(lambda e : e["res"], fvstreams))
      #if the vstream res is already in the fvstreams, we skip appending it to the list
      if not vstream["resolution"] or vstream["resolution"] in resolutions or not vstream["_filesize"] or "avc1." not in vstream["codecs"][0]: continue
      
      fvstreams.append({"itag": vstream["itag"], "res": vstream["resolution"], "formatted_size": self.convert_bytes(vstream["_filesize"] + astream["_filesize"]), "raw_size": vstream["_filesize"] + astream["_filesize"]})
   
    return {"video": fvstreams, "audio": mastream}
    
  def download_audio(self):
    filename = f"{uuid.uuid4()}.mp3"
    
    audio_stream = self.video.streams.get_audio_only()
    audio_path = audio_stream.download(output_path="downloads/", filename=filename)
   
    return audio_path
  
  def download_video(self, itag):
    audio_filename = f"{uuid.uuid4()}.mp4"
    video_filename = f"{uuid.uuid4()}.mp4"
    combined = f"downloads/{uuid.uuid4()}.mp4"
    
    video_stream = self.video.streams.get_by_itag(itag)
    audio_stream = self.video.streams.get_audio_only()
    
    video_path = video_stream.download(output_path="downloads/", filename=video_filename)
    audio_path = audio_stream.download(output_path="downloads/", filename=audio_filename)
    
    input_video = ffmpeg.input(video_path)
    input_audio = ffmpeg.input(audio_path)
    
    ffmpeg.output(input_video, input_audio, combined, vcodec='copy', acodec="copy").run()
    
    #cmd = f"ffmpeg -i {video_path} -i {audio_path} -map 0:v -map 1:a -c copy {combined}"
    #subprocess.call(cmd, shell=True)
    
    os.remove(video_path)
    os.remove(audio_path)
    
    return combined
    
  def download_thumb(self, url):
    file_name = f"downloads/{uuid.uuid4()}.jpg"
    res = requests.get(url)
    
    if res.status_code != 200: return
  
    with open(file_name, "wb") as f:
            f.write(res.content)
    return file_name
    
  async def upload_file(self, app, chat_id, file_path, upload_type, itag=None):
    yturl = self.url
    url = self.video.thumbnail_url
    duration = self.video.length
    title = self.video.title
    author = self.video.author
    thumbnail = self.download_thumb(url)# un processed thumb
    
    if upload_type == "video":
      message = await app.send_video(chat_id, file_path, file_name=title + ".mp4", duration=duration, thumb=thumbnail)
      
      file_id = message.video.file_id
      await File.insert_one({"video_url": yturl, "itag": itag, "file_id": file_id, "type": "video"})
    else:
      message = await app.send_audio(chat_id, file_path, file_name=title + ".mp3", title=title, performer=author, duration=duration, thumb=thumbnail)
      
      file_id = message.audio.file_id
      await File.insert_one({"video_url": yturl, "type": "audio", "file_id": file_id})
    
    os.remove(thumbnail)
from pytube import YouTube
import ffmpeg
from fastapi.encoders import jsonable_encoder
import os
from datetime import datetime
from math import floor, ceil
import uuid

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
    
    video_details = {
      "title": title, 
      "author": author,
      "publish_date": publish_date,
      "duration": duration,
      "views": views,
      "thumbnail": thumbnail,
      "video_url": self.url,
    }
    return video_details
  def get_streams(self):
    vstreams = jsonable_encoder(self.video.streams.filter(subtype='mp4', only_video=True).order_by("resolution").desc())["fmt_streams"] #video streams with no audio
    
    astream = jsonable_encoder(self.video.streams.get_audio_only()) #best audio stream
    
    fvstreams = [] #filtered video streams
    mastream = {"itag": astream["itag"], "size": self.convert_bytes(astream["_filesize"])} #modified audio stream
    
    for vstream in vstreams:
      #extract res property from vstreams dicts
      resolutions = list(map(lambda e : e["res"], fvstreams))
      #if the vstream res is already in the fvstreams, we skip appending it to the list
      if not vstream["resolution"] or vstream["resolution"] in resolutions or not vstream["_filesize"] or "avc1." not in vstream["codecs"][0]: continue
      
      fvstreams.append({"itag": vstream["itag"], "res": vstream["resolution"], "size": self.convert_bytes(vstream["_filesize"] + astream["_filesize"])})
   
    return {"video": fvstreams, "audio": mastream}
    
  def download(self, itag):
    stream = self.video.streams.get_by_itag(itag)
    return jsonable_encoder(stream)
    if stream.only_audio:
      filename = f"{uuid.uuid4()}.mp3"
    
      audio_path = stream.download(output_path="downloads/", filename=filename)
      return {"type": "audio", "path": audio_path}
      
    elif stream.only_video:
      audio_filename = f"{uuid.uuid4()}.mp4"
      video_filename = f"{uuid.uuid4()}.mp4"
      audio_video_path = f"downloads/{uuid.uuid4()}.mp4"
    
      audio_stream = self.video.streams.get_audio_only()
    
      video_path = stream.download(output_path="downloads/", filename=video_filename)
      audio_path = audio_stream.download(output_path="downloads/", filename=audio_filename)
    
      input_video = ffmpeg.input(video_path).video
      input_audio = ffmpeg.input(audio_path).audio
    
      ffmpeg.output(input_video, input_audio, audio_video_path, vcodec='copy', acodec="copy").run()
    
      os.remove(video_path)
      os.remove(audio_path)
      
      return {"type": "video", "path": audio_video_path}
      
    else:
      return {"type": null, "path": ""}
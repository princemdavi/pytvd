import os
import motor.motor_asyncio

DB_URL = os.getenv("DB_URL")

client = motor.motor_asyncio.AsyncIOMotorClient(DB_URL)

database = client.pytvd

File = database.get_collection("files")

async def insert_file(title: str, itag: str, file_id: str, video_id: str):
    new_file = await File.insert_one({"title": title, "video_id": video_id, "itag": itag, "file_id": file_id})
    return new_file.inserted_id

async def get_file(video_id: str, itag: str):
    file = await File.find_one({"video_id": video_id, "itag": itag})
    return file

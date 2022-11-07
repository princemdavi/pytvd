import os
import motor.motor_asyncio

DB_URL = os.getenv("DB_URL")

client = motor.motor_asyncio.AsyncIOMotorClient(DB_URL)

database = client.pytvd

File = database.get_collection("files")


async def insert_file(file):
    new_file = await File.insert_one({"title": file.get("title"), "video_id": file.get("video_id"), "itag": file.get("itag"), "file_id": file.get("file_id"), "file_size": file.get("file_size"), "ext": file.get("ext")})
    return new_file.inserted_id


async def get_file(video_id: str, itag: str):
    file = await File.find_one({"video_id": video_id, "itag": itag})
    return file

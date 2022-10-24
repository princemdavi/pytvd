import os
import motor.motor_asyncio

DB_URL = os.getenv("DB_URL")

client = motor.motor_asyncio.AsyncIOMotorClient(DB_URL)

database = client.pytvd

File = database.get_collection("files")

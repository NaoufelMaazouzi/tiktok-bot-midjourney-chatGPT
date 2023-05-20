from moviepy.editor import VideoFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import pytube
import json
import discord
import os

def downloadVideo(url):
    youtube = pytube.YouTube(url, use_oauth=True, allow_oauth_cache=True)
    video = youtube.streams.get_highest_resolution()
    file_name = video.default_filename
    video.download()
    return file_name

async def cutVideo(ctx, video_path, passages):
    for passage in passages:
        start = passage['start'] / 1000
        end = passage['end'] / 1000
        output_path = f"passage_{start}_{end}.mp4"
        ffmpeg_extract_subclip(video_path, start, end, targetname=output_path)
        await ctx.send(file=discord.File(os.path.abspath(output_path)))
        os.remove(output_path)

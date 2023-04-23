
import discord
from discord.ext import commands
from pytube import YouTube
import os
import pytube
from googletrans import Translator
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from youtube_transcript_api.formatters import WebVTTFormatter
from concurrent.futures import ThreadPoolExecutor
import asyncio

discord_token = "MTA5Njk2NTc0MzgzNDMwODYxOA.GN4ojj.2yGfvXjhtCtBe7X0sZw1R-Vf31dltfeLl5rMeU"

def connectToDiscord():
    try:
        intents = discord.Intents.all()
        global bot
        bot = commands.Bot(command_prefix='/', intents=intents)
    except Exception as e:
        print(f"Error connectToDiscord: {e}")


def getVideoId(url):
    index_debut_id = url.find('=') + 1
    index_fin_id = url.find('&')
    return str(url[index_debut_id:index_fin_id])

def downloadVideo(url):
    youtube = pytube.YouTube(url, use_oauth=True, allow_oauth_cache=True)
    video = youtube.streams.get_highest_resolution()
    file_name = video.default_filename
    video.download()
    return file_name

def format_subtitles(subtitles):
    formatted_subs = []
    for sub in subtitles:
        start_time = sub['start']
        end_time = start_time + sub['duration']
        text = sub['text']
        formatted_subs.append(((start_time, end_time), text))
    return formatted_subs


def addSubtitles(subtitles, file_name, output_file):
    subtitles = format_subtitles(subtitles)
    generator = lambda txt: TextClip(txt, font='Arial', fontsize=28, color='white')
    subtitles_clip = SubtitlesClip(subtitles, generator)
    video = VideoFileClip(file_name)
    result = CompositeVideoClip([video, subtitles_clip.set_pos(('center',video.size[1]-100))])
    result.write_videofile(output_file, fps=video.fps, temp_audiofile="temp-audio.m4a", remove_temp=True, codec="libx264", audio_codec="aac")

def getTranscripts(videoId):
    base_lang = "en"
    wanted_lang = "fr"
    transcripts = YouTubeTranscriptApi.list_transcripts(videoId)
    base_obj = transcripts.find_transcript([base_lang])
    if base_obj.is_translatable:
            return base_obj.translate(wanted_lang).fetch()
    else:
        print(f"CAN NOT translate transcript to {wanted_lang}")
        quit()



connectToDiscord()


@bot.command()
async def dl_youtube(ctx, url):
    base_lang = "en"
    wanted_lang = "fr"
    # await ctx.send("25%...")
    # loop = asyncio.get_event_loop()
    # file_name = await loop.run_in_executor(ThreadPoolExecutor(), downloadVideo, url)
    file_name = downloadVideo(url)
    # videoId = await loop.run_in_executor(ThreadPoolExecutor(), getVideoId, url)
    videoId = getVideoId(url)
    # await ctx.send("50%...")
    # videoId = await loop.run_in_executor(ThreadPoolExecutor(), getVideoId, url)

    # transcript = await loop.run_in_executor(ThreadPoolExecutor(), getTranscripts, videoId)
    transcripts = YouTubeTranscriptApi.list_transcripts(videoId)
    base_obj = transcripts.find_transcript([base_lang])

    # translate to another language
    if base_obj.is_translatable:
        wanted_tran = base_obj.translate(wanted_lang).fetch()
    else:
        print(f"CAN NOT translate transcript to {wanted_lang}")
        quit()

    addSubtitles(wanted_tran, file_name, 'test.mp4')
    # await ctx.send("75%...")
    # await loop.run_in_executor(ThreadPoolExecutor(), addSubtitles, transcript, file_name, 'test.mp4')
    # await ctx.send("Votre vidéo est téléchargée !")


bot.run(discord_token)
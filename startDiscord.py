
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
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from mutagen.mp4 import MP4
import numpy as np
import uuid
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
# from moviepy.video.io.VideoFileClip import VideoFileClip
import json
import cv2
from moviepy.editor import VideoFileClip
from chatGPT import askChatGPT
from youtube import search

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

def cutVideo(video_path, parts):
    video = VideoFileClip(video_path)
    for i, part in enumerate(json.loads(parts.replace("'",'"'))):
        start_time = part['start']
        end_time = part['end']
        if isinstance(start_time, float):
            start_time = int(start_time // 1) * 60 + start_time % 1 * 100
        if isinstance(end_time, float):
            end_time = int(end_time // 1) * 60 + end_time % 1 * 100
        clip = video.subclip(start_time, end_time)
        file_name = f"part_{i + 1}.mp4"
        clip.write_videofile(file_name)
    video.close()
    # os.remove(video_path)

def goToNewLine(string):
    mots = string.split()  # sépare la chaîne en une liste de mots
    return "".join(" ".join(mots[i:i+8]) + "\n" for i in range(0, len(mots), 8))

def format_subtitles(subtitles):
    formatted_subs = []
    for sub in subtitles:
        start_time = sub['start']
        end_time = start_time + sub['duration']
        text = sub['text']
        text = goToNewLine(text)
        formatted_subs.append(((start_time, end_time), text))
    return formatted_subs

def addGreenFilter(file_name):
    try:
        new_uuid = uuid.uuid4()
        output_filename = f"{new_uuid}.mp4"
        audio_file_name = "audio.wav"

        # Ouverture de la vidéo
        video_clip = VideoFileClip(file_name)
        # Extraction de l'audio de la vidéo
        audio = video_clip.audio
        audio.write_audiofile(audio_file_name)
        # Application du filtre vert à la vidéo
        final_clip = video_clip.fl_image(addGreenFrame)
        final_clip.write_videofile(output_filename, codec='libx264', audio_codec='aac', temp_audiofile='temp-audio.m4a', remove_temp=True, fps=30)

        # os.remove(file_name)
        # os.remove(audio_file_name)

        return output_filename
    except Exception as e:
        print(f"Error addGreenFilter: {e}")

def addGreenFrame(frame):
    try:
        # Copie du tableau
        new_frame = np.copy(frame)

        red = new_frame[:, :, 2].astype(np.int16)
        blue = new_frame[:, :, 0].astype(np.int16)
        green = new_frame[:, :, 1].astype(np.int16) + np.minimum(red, blue) // 6 #Modifier le 4 pour modifier la quantité de vert
        green = np.clip(green, 0, 255).astype(np.uint8)
        new_frame[:, :, 1] = green

        return new_frame
    except Exception as e:
        print(f"Error addGreenFrame: {e}")

def changeMetaData(file_name):
    try:
        video_file = MP4(file_name)

        # Supprimer les metadata et enregistrer les modifications dans le fichier vidéo
        video_file.delete()
        video_file.save()
    except Exception as e:
        print(f"Error changeMetaData: {e}")

def addSubtitles(subtitles, file_name, output_filename):
    subtitles = format_subtitles(subtitles)
    generator = lambda txt: TextClip(txt, font='Arial', fontsize=96, color='white', stroke_color='black', stroke_width=2.4).resize(0.5)
    subtitles_clip = SubtitlesClip(subtitles, generator)
    video = VideoFileClip(file_name)
    result = CompositeVideoClip([video, subtitles_clip.set_pos(('center',video.size[1]-250))])
    result.write_videofile(output_filename, fps=video.fps, temp_audiofile="temp-audio.m4a", remove_temp=True, codec="libx264", audio_codec="aac")
    # os.remove(file_name)

# def flouter_zone_centrale(video_path, output_path):
#     cap = cv2.VideoCapture(video_path)
#     width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#     height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

#     # Définition de la région centrale à flouter
#     zone_centrale = [0, height - 36, width, height // 2]

#     # Définition du codec et des paramètres de sortie vidéo
#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     fps = int(cap.get(cv2.CAP_PROP_FPS))
#     out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

#     while (cap.isOpened()):
#         ret, frame = cap.read()
#         if ret != True:
#             break

#         # Flou gaussien sur la zone centrale
#         x, y, w, h = zone_centrale
#         frame[y:y+h, x:x+w] = cv2.GaussianBlur(frame[y:y+h, x:x+w], (37, 37), 0)

#         out.write(frame)

#     out.release()
#     cv2.destroyAllWindows()

def flouter_zone_centrale(video_path, output_path):
    clip = VideoFileClip(video_path)
    # Définition de la région centrale à flouter
    x, y, w, h = [0, clip.h - 36, clip.w, clip.h // 2]
    # Application du flou gaussien sur la zone centrale
    def flouter_frame(frame):
        frame_copie = frame.copy()
        frame_copie[y:y+h, x:x+w] = cv2.GaussianBlur(frame_copie[y:y+h, x:x+w], (75, 75), 0)
        frame = cv2.addWeighted(frame_copie, 0.8, frame, 0.2, 0)
        return frame
    clip = clip.fl_image(flouter_frame)
    # Écriture de la vidéo résultante avec la piste audio d'origine
    clip.write_videofile(output_path, audio=True)

def getTranscripts(videoId, base_lang="fr", wanted_lang="fr"):
    print(videoId)
    transcripts = YouTubeTranscriptApi.list_transcripts(videoId)
    base_obj = transcripts.find_transcript([base_lang])
    if base_obj.is_translatable:
        return base_obj.translate(wanted_lang).fetch()
    print(f"CAN NOT translate transcript to {wanted_lang}")
    quit()

def sendVideoToDrive(file_name):
    # Paramètres de configuration
    file_mime_type = "video/mp4"  # Type MIME du fichier à télécharger
    folder_id = "15rGKrKZKEXKi1q6xytL-cucAZ_tJ3oDs"  # ID du dossier cible sur Google Drive

    # Authentification à l'API Google Drive
    creds = Credentials.from_authorized_user_file("client_secrets.json", ["https://www.googleapis.com/auth/drive"])
    service = build("drive", "v3", credentials=creds)

    # Création de l'objet MediaFileUpload pour le téléchargement du fichier
    media = MediaFileUpload(file_name, mimetype=file_mime_type, resumable=True)

    # Paramètres du fichier à télécharger
    file_metadata = {"name": file_name, "parents": [folder_id]}

    try:
        # Téléchargement du fichier sur Google Drive
        file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()

        # Affichage du lien de téléchargement du fichier
        file_id = file.get("id")
        link = f"https://drive.google.com/file/d/{file_id}"
        print(f"Voici le lien pour télécharger la vidéo : {link}")

    except HttpError as error:
        print(f"Une erreur s'est produite : {error}")
    # try:
    #     gfile = drive.CreateFile({'mimetype': 'video/mp4', 'parents': [{'id': '15rGKrKZKEXKi1q6xytL-cucAZ_tJ3oDs'}]})
    #     print('aaaaaa')
    #     gfile.SetContentFile(file_name)
    #     print('bbbbbb')
    #     gfile.Upload() # Upload the file.
    #     print('cccccc')
    #     file_id = gfile['id']
    #     link = f"https://drive.google.com/file/d/{file_id}"
    #     return f"Voici le lien pour télécharger la vidéo : {link}"
    # except Exception as e:
    #     print(f"Error sendVideoToDrive: {e}")

def authGDrive():
    try:
        # Authentification Google
        gauth = GoogleAuth()
        # Create local webserver and auto handles authentication.
        gauth.LocalWebserverAuth()
        global drive
        drive = GoogleDrive(gauth)
    except Exception as e:
        print(f"Error authGDrive: {e}")

def modifVideo(file_name):
    output_filename = addGreenFilter(file_name)
    # Retirer les métadatas
    changeMetaData(output_filename)
    return output_filename



connectToDiscord()
# authGDrive()

@bot.command()
async def dl_youtube(ctx, url, parts=None):
    base_lang = "en"
    wanted_lang = "fr"
    await ctx.send("25%...")
    loop = asyncio.get_event_loop()
    file_name = await loop.run_in_executor(ThreadPoolExecutor(), downloadVideo, url)
    # file_name = downloadVideo(url)
    output_filename = f"subtitles_{file_name}"
    # videoId = getVideoId(url)
    await ctx.send("50%...")
    videoId = await loop.run_in_executor(ThreadPoolExecutor(), getVideoId, url)

    transcript = await loop.run_in_executor(ThreadPoolExecutor(), getTranscripts, videoId, "en", "fr")
    # transcripts = YouTubeTranscriptApi.list_transcripts(videoId)
    # base_obj = transcripts.find_transcript([base_lang])

    # translate to another language
    # if base_obj.is_translatable:
    #     wanted_tran = base_obj.translate(wanted_lang).fetch()
    # else:
    #     print(f"CAN NOT translate transcript to {wanted_lang}")
    #     quit()

    # addSubtitles(wanted_tran, file_name, 'test.mp4')
    await ctx.send("75%...")
    await ctx.send("Sous-titres en cours de création...")
    # video_modified = await loop.run_in_executor(ThreadPoolExecutor(), modifVideo, file_name)
    # await loop.run_in_executor(ThreadPoolExecutor(), flouter_zone_centrale, file_name, output_filename)
    # blur_output_filename = f"subtitles_blur_{file_name}"
    await loop.run_in_executor(ThreadPoolExecutor(), addSubtitles, transcript, file_name, output_filename)

    
    if(parts):
        cutVideo(output_filename, parts)

    # result = await loop.run_in_executor(ThreadPoolExecutor(), sendVideoToDrive, output_filename)
    # # os.remove(output_filename)
    # print('result', result)
    # await ctx.send(result)
    
    await ctx.send("Votre vidéo est téléchargée !")



@bot.command()
async def getSubtitles(ctx, url):
    await ctx.send("25%...")
    loop = asyncio.get_event_loop()
    file_name = await loop.run_in_executor(ThreadPoolExecutor(), downloadVideo, url)
    videoId = await loop.run_in_executor(ThreadPoolExecutor(), getVideoId, url)

    transcript = await loop.run_in_executor(ThreadPoolExecutor(), getTranscripts, videoId)
    prompt = f"""Je vous donne une transcription d'une émission télé ou plusieurs personnes racontent leur histoires vous allez l'analyser du début à la fin et vous allez m'identifier dans cette émission les passages captivants et attractifs qui peuvent intéresser des personnes sur TikTok.Je veux que tu me donnes seulement un tableau contenant les valeurs de la variable 'start' de chaque passage captivants que tu as trouvé. Voici le tous les passages: {transcript[:50]}"""
    askChatGPT(prompt)
    # transcripts = YouTubeTranscriptApi.list_transcripts(videoId)
    # base_obj = transcripts.find_transcript([base_lang])

    # translate to another language
    # if base_obj.is_translatable:
    #     wanted_tran = base_obj.translate(wanted_lang).fetch()
    # else:
    #     print(f"CAN NOT translate transcript to {wanted_lang}")
    #     quit()

    await ctx.send("Sous-titres créés !")

@bot.command()
async def search_yt(ctx, url):
    # loop = asyncio.get_event_loop()
    # await loop.run_in_executor(ThreadPoolExecutor(), search, ctx, url)
    await search(ctx, url)


bot.run(discord_token)
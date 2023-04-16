# from revChatGPT.V1 import Chatbot

# chatbot = Chatbot(config={
#   "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1UaEVOVUpHTkVNMVFURTRNMEZCTWpkQ05UZzVNRFUxUlRVd1FVSkRNRU13UmtGRVFrRXpSZyJ9.eyJodHRwczovL2FwaS5vcGVuYWkuY29tL3Byb2ZpbGUiOnsiZW1haWwiOiJuYW91ZmVsLm1hYXpvdXppQGxpdmUuZnIiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZX0sImh0dHBzOi8vYXBpLm9wZW5haS5jb20vYXV0aCI6eyJ1c2VyX2lkIjoidXNlci05NFZxSTV6T1JVYUtLTHNqU2J2eXNvMUgifSwiaXNzIjoiaHR0cHM6Ly9hdXRoMC5vcGVuYWkuY29tLyIsInN1YiI6ImF1dGgwfDYyNGU5MmYwMjM1YmFjMDA2ZWJjNDU3MyIsImF1ZCI6WyJodHRwczovL2FwaS5vcGVuYWkuY29tL3YxIiwiaHR0cHM6Ly9vcGVuYWkub3BlbmFpLmF1dGgwYXBwLmNvbS91c2VyaW5mbyJdLCJpYXQiOjE2ODA4OTczOTcsImV4cCI6MTY4MjEwNjk5NywiYXpwIjoiVGRKSWNiZTE2V29USHROOTVueXl3aDVFNHlPbzZJdEciLCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIG1vZGVsLnJlYWQgbW9kZWwucmVxdWVzdCBvcmdhbml6YXRpb24ucmVhZCBvZmZsaW5lX2FjY2VzcyJ9.YJiS3XEURraCcMhop1sb7lEr3MNsefUnIQZpQd9WaGNCkmEaAfQ29-neyIx5aM5jhVUdfcrTdOvSVD6qjdU3bOzTa4p4Dvj9DU76ANclWuKM5jxbCCCSWlEzdzNU9dp0Mky6I3l1fzZZJIib9GaDtVHB5xiVO3btOM_TlFaH0HM5eqvqAMCvfu428Wx4opXgvjqRktDLozkPUXokt6rUO7BpK2TJQx28oz768NfxLAevMq_j0kXiAnpf0L_jnWwLJzfe-9_8_slQkCcxqus8bQEViX5q8dh8dppw-B-6m_MsOS8lPD0PDWHN5wC808npPQOjCt37a6BP6WLDan_EGA"
# })

# print("Chatbot: ")
# prev_text = ""
# for data in chatbot.ask(
#     "Hello world",
# ):
#     message = data["message"][len(prev_text) :]
#     print(message, end="", flush=True)
#     prev_text = data["message"]
# print()

import time
import discord
from discord.ext import commands
from dotenv import load_dotenv
import pyautogui as pg
import requests
from dotenv import load_dotenv
from PIL import Image
import os
import pyperclip

discord_token = "MTA5Njk2NTc0MzgzNDMwODYxOA.GN4ojj.2yGfvXjhtCtBe7X0sZw1R-Vf31dltfeLl5rMeU"

# Using readlines()
prompt_file = open('prompts.txt', 'r')
prompts = prompt_file.readlines()

prompt_counter = 0

load_dotenv()
client = commands.Bot(command_prefix="*", intents=discord.Intents.all())

directory = os.getcwd()
print(directory)

@client.event
async def on_ready():
    print("Bot connected")


def split_image(image_file):
   with Image.open(image_file) as im:
       # Get the width and height of the original image
       width, height = im.size
       # Calculate the middle points along the horizontal and vertical axes
       mid_x = width // 2
       mid_y = height // 2
       # Split the image into four equal parts
       top_left = im.crop((0, 0, mid_x, mid_y))
       top_right = im.crop((mid_x, 0, width, mid_y))
       bottom_left = im.crop((0, mid_y, mid_x, height))
       bottom_right = im.crop((mid_x, mid_y, width, height))

       return top_left, top_right, bottom_left, bottom_right


async def download_image(url, filename):
    response = requests.get(url)
    if response.status_code == 200:

        # Define the input and output folder paths
        input_folder = "input"
        output_folder = "output"

        # Check if the output folder exists, and create it if necessary
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        # Check if the input folder exists, and create it if necessary
        if not os.path.exists(input_folder):
            os.makedirs(input_folder)

        with open(f"{directory}/{input_folder}/{filename}", "wb") as f:
            f.write(response.content)
        print(f"Image downloaded: {filename}")

        input_file = os.path.join(input_folder, filename)

        if "UPSCALED_" not in filename:
            file_prefix = os.path.splitext(filename)[0]
            # Split the image
            top_left, top_right, bottom_left, bottom_right = split_image(input_file)
            # Save the output images with dynamic names in the output folder
            top_left.save(os.path.join(output_folder, f"{file_prefix}_top_left.jpg"))
            top_right.save(os.path.join(output_folder, f"{file_prefix}_top_right.jpg"))
            bottom_left.save(os.path.join(output_folder, f"{file_prefix}_bottom_left.jpg"))
            bottom_right.save(
                os.path.join(output_folder, f"{file_prefix}_bottom_right.jpg")
            )

    else:
        os.rename(f"{directory}/{input_folder}/{filename}", f"{directory}/{output_folder}/{filename}")
       # Delete the input file
        os.remove(f"{directory}/{input_folder}/{filename}")

def _workaround_write(text):
    """
    This is a work-around for the bug in pyautogui.write() with non-QWERTY keyboards
    It copies the text to clipboard and pastes it, instead of typing it.
    """
    pyperclip.copy(text)
    pg.hotkey('ctrl', 'v')
    pyperclip.copy('')

@client.event
async def on_message(message):
    global prompt_counter

    msg = message.content

    while prompt_counter < len(prompts):
        # Start Automation by typing "automation" in the discord channel
        if msg == 'automation':
            print(prompts[prompt_counter])
            time.sleep(3)
            pg.press('tab')
            for _ in range(1):
                time.sleep(3)
                pg.write('/imagine')
                time.sleep(5)
                pg.press('tab')
                _workaround_write(prompts[prompt_counter])
                time.sleep(3)
                pg.press('enter')
                time.sleep(5)
                prompt_counter += 1

        # continue Automation as soon Midjourney bot sends a message with attachment.
        for _ in message.attachments:
            time.sleep(3)
            pg.write('/imagine')
            time.sleep(5)
            pg.press('tab')
            pg.write(prompts[prompt_counter])
            time.sleep(3)
            pg.press('enter')
            time.sleep(5)
            prompt_counter += 1

    for attachment in message.attachments:
        file_prefix = 'UPSCALED_' if "Upscaled by" in message.content else ''
        if attachment.filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
            await download_image(attachment.url, f"{file_prefix}{attachment.filename}")
    # Stop Automation once all prompts are completed
    # quit()

client.run(discord_token)
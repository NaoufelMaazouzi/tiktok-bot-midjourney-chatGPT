import time
from dotenv import load_dotenv
import pyautogui as pg
import requests
from dotenv import load_dotenv
from PIL import Image
import os
import pyperclip


load_dotenv()

directory = os.getcwd()


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
    print(response.status_code)
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

async def generateImages(message):
    global prompt_counter

    if os.path.exists('prompts.txt'):
        prompt_file = open('prompts.txt', 'r')
        prompts = prompt_file.readlines()
    else:
        prompts = ''

    prompt_counter = 0

    msg = message.content

    try:
        while prompt_counter < len(prompts):
            # Start Automation by typing "automation" in the discord channel
            if msg == 'automation':
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
    except Exception as err:
        print("Error generate /imagine command:", err)

    try:
        for attachment in message.attachments:
            file_prefix = 'UPSCALED_' if "Upscaled by" in message.content else ''
            if attachment.filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
                await download_image(attachment.url, f"{file_prefix}{attachment.filename}")
            # Stop Automation once all prompts are completed
            # quit()
    except Exception as err:
        print("Error download images:", err)
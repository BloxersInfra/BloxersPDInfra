import os
import discord
import requests
from dotenv import load_dotenv
from datetime import datetime
from discord.ext import commands, tasks

# Load environment variables from the .env file
load_dotenv(dotenv_path='/Users/alexrichey/Desktop/PDINfra/BloxersPDInfra/apis.env')

# Fetch the API keys from environment variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
PAGERDUTY_API_KEY = os.getenv('PAGERDUTY_API_KEY')
PAGERDUTY_SERVICE_ID = os.getenv('PAGERDUTY_SERVICE_ID')
PAGERDUTY_USER_EMAIL = os.getenv('PAGERDUTY_USER_EMAIL')  # Ensure this is set in your .env file

# Check if the DISCORD_TOKEN is properly loaded
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN is not set in the environment variables.")

intents = discord.Intents.default()
intents.message_content = True

# Initialize bot with commands extension
bot = commands.Bot(command_prefix='/', intents=intents)

# Cooldown settings
COOLDOWN_SECONDS = 300  # Cooldown period in seconds
last_trigger_time = None  # Variable to store the last trigger time

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    # Start the background task
    ping_task.start()

@bot.command()
async def pagepteam(ctx):
    global last_trigger_time  # Declare as global to modify inside the function

    # Ignore messages from the bot itself
    if ctx.author == bot.user:
        return

    # Command to trigger PagerDuty alert
    current_time = datetime.utcnow()
    
    # Check if the command is on cooldown
    if last_trigger_time:
        elapsed_time = (current_time - last_trigger_time).total_seconds()
        if elapsed_time < COOLDOWN_SECONDS:
            remaining_time = int(COOLDOWN_SECONDS - elapsed_time)
            await ctx.send(
                f"⚠️ This command is on cooldown. Please wait {remaining_time} seconds before trying again."
            )
            return
    
    # Trigger the PagerDuty alert
    success, response_message = trigger_pagerduty_alert()

    if success:
        await ctx.send("✅ Corporate Escalations team has been paged successfully.")
        last_trigger_time = current_time  # Update the last trigger time
    else:
        await ctx.send(
            f"❌ Failed to page Corporate Escalations team. Error: {response_message}"
        )

# Command to make the bot go offline
@bot.command()
async def offline(ctx):
    # Check if the command is issued in the specific guild and channel
    if ctx.guild.id == 1193296724811337748 and ctx.channel.id == 1193297503387398184:
        await ctx.send("Bot is going offline... 👋")
        await bot.close()
    else:
        await ctx.send("You cannot use this command in this channel.")

def trigger_pagerduty_alert():
    url = 'https://api.pagerduty.com/incidents'
    headers = {
        'Authorization': f'Token token={PAGERDUTY_API_KEY}',
        'Content-Type': 'application/json',
        'Accept': 'application/vnd.pagerduty+json;version=2',
        'From': PAGERDUTY_USER_EMAIL  # Use the email specified in the .env file
    }
    payload = {
        "incident": {
            "type": "incident",
            "title": "Corporate Escalations: Discord Paged Alert",
            "service": {
                "id": PAGERDUTY_SERVICE_ID,
                "type": "service_reference"
            },
            "urgency": "high",
            "body": {
                "type": "incident_body",
                "details": "This incident was triggered from a Discord command."
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 201:
            print("PagerDuty alert triggered successfully.")
            return True, None
        else:
            error_message = f"{response.status_code} - {response.text}"
            print(f"Failed to trigger PagerDuty alert: {error_message}")
            return False, error_message
    except requests.exceptions.RequestException as e:
        print(f"Exception occurred while triggering PagerDuty alert: {e}")
        return False, str(e)

# Background task to send a "Ping! I'm alive." message every 60 seconds
@tasks.loop(seconds=60)
async def ping_task():
    channel = bot.get_channel(1277486534706204776)
    if channel:
        await channel.send("Ping! I'm alive.")

# Run the bot
bot.run(DISCORD_TOKEN)

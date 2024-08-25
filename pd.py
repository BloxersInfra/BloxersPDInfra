import os
import discord
import requests
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv(dotenv_path='/Users/alexrichey/Desktop/PDINfra/BloxersPDInfra/api.env')

# Fetch the API keys from environment variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
PAGERDUTY_API_KEY = os.getenv('PAGERDUTY_API_KEY')
PAGERDUTY_SERVICE_ID = os.getenv('PAGERDUTY_SERVICE_ID')
PAGERDUTY_USER_EMAIL = os.getenv('PAGERDUTY_USER_EMAIL')  # Add this to your .env file

# Check if the DISCORD_TOKEN is properly loaded
print(f'DISCORD_TOKEN: {DISCORD_TOKEN}')  # Should print the token or None

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.content == '/pagePTeam':
        trigger_pagerduty_alert()
        await message.channel.send("Corporate Escalations team has been paged.")

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

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 201:
        print("PagerDuty alert triggered successfully.")
    else:
        print(f"Failed to trigger PagerDuty alert: {response.status_code} - {response.text}")

# This is the correct way to run the bot
client.run(DISCORD_TOKEN)

#Hi
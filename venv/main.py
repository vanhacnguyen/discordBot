from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message, Interaction
from discord.ext import commands

# import sympy as smp
# import numpy as np

#find api, dm joshiro for setting up get response

load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = # place channel ID
# Bot setup
bot_intents: Intents = Intents.default()
bot_intents.message_content = True
client = commands.Bot(command_prefix = '!', intents = bot_intents) # Can change the command_prefix, this is just what goes in front of a command like !ping

# Handling the startup for bot
@client.event
async def on_ready() -> None:
    print(f'{client.user} is now running!')
    channel = client.get_channel(CHANNEL_ID)
    await channel.send("Hello! Mad_Scientist is ready!")

@client.command()
async def add(ctx, *arr):
    result = 0
    for i in arr:
        if i.isdigit():
            result += int(i)
    await ctx.send(f"Answer: {result}")


@client.command()
async def subtract(ctx, *arr):
    result = 0
    for i in arr:
        if i.isdigit():
            result -= int(i)
    await ctx.send(f"Answer: {result}")

# Main entry point
def main() -> None:
    client.run(token = TOKEN)

if __name__ == '__main__':
    main()
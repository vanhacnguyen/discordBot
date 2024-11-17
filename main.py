from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message, Interaction
from discord.ext import commands

from sympy import *
import numpy as np

#find api, dm joshiro for setting up get response and getting help

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
# *equation is a tuple of strings
async def solve(ctx, *equation):
    try:
        eq_str = " ".join(equation) # combine into a single string

        x_index = eq_str.index("x")
        char_before_x = eq_str[x_index - 1]

        # second replace in case user already input 2*x instead of 2x
        if char_before_x != "/" and x_index != 0:
            eq_str = eq_str.replace("x", "*x").replace("* *", "*")

        x = symbols('x')

        if "=" in eq_str:
            left, right = eq_str.split("=")
            # sympify parses left, right into mathematical expression
            eq = Eq(sympify(left), sympify(right))
        else:
            await ctx.send("Please input a valid equation!")
            return
        answer = solve(eq, x) # solve eq for x
        await ctx.send(f"Answer: {answer}")
    except Exception as e:
        await ctx.send(f"Error solving the equation: {str(e)}")

@client.command()
async def factor(ctx, *expr):
    try:
        eq_str = " ".join(expr)
        eq_str = eq_str.replace("x^", "x**")

        x_index = eq_str.index("x")
        second = eq_str.find("x", x_index + 1)

        eq_str = eq_str.replace("x", "*x").replace("* *", "*")
        eq = Eq(sympify(eq_str))
        answer = eq.factor()
        await ctx.send(f"Answer: {answer}")
    except Exception as e:
        await ctx.send(f"Error factoring the equation: {str(e)}")

# Main entry point
def main() -> None:
    client.run(token = TOKEN)

if __name__ == '__main__':
    main()
from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message, Interaction
from discord.ext import commands

import sympy as smp
import numpy as np
import matplotlib.pyplot as plt

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

# Helper method to insert '*' to x
def insertTimeX(eq):
    # Process each occurrence of 'x'
    x_index = eq.find("x")  # Find the first occurrence
    while x_index != -1: 
        # Check the character before 'x'
        if x_index > 0:  # Ensure it's not the first character
            char_before = eq[x_index - 1]
            if char_before.isdigit():  # If a digit is in front of x, add '*'
                eq = eq[:x_index] + "*x" + eq[x_index + 1:]
                x_index += 1  # Move index forward to account for inserted '*'
        # Find the next occurrence of 'x'
        x_index = eq.find("x", x_index + 1)
    return eq

@client.command()
# *equation is a tuple of strings
async def solve(ctx, *equation):
    try:
        eq_str = " ".join(equation).replace("^", "**") # combine into a single string

        eq_str = insertTimeX(eq_str)
        x = smp.symbols('x', real = True)

        if "=" in eq_str:
            left, right = eq_str.split("=")
            # parse_expr parses variable left, right into mathematical expression
            eq = smp.Eq(smp.parse_expr(left), smp.parse_expr(right))
        else:
            await ctx.send("Please input a valid equation!")
            return
        answer = smp.solve(eq, x) # solve eq for x
        await ctx.send("Answer: " + str(answer))
    except Exception as e:
        await ctx.send(f"Error solving the equation: {str(e)}")

@client.command()
async def factor(ctx, *expr):
    try:
        eq_str = " ".join(expr).replace("^", "**")

        eq_str = insertTimeX(eq_str)
        eq = smp.parse_expr(eq_str)
        answer = smp.factor(eq)
        answer = answer.replace("**", "^")
        await ctx.send(f"Factor of {eq_str}: " + str(answer))
    except Exception as e:
        await ctx.send(f"Error factoring the equation: {str(e)}")

@client.command()
async def limit(ctx, *expr):
    try:
        eq_str = " ".join(expr).replace("^", "**")
        x = smp.symbols('x', real = True)

        eq_str = insertTimeX(eq_str)

        # Find the arrow to find limit point
        arrow_index = eq_str.index(">")
        limit_expr_str = eq_str[:arrow_index].strip() # Get the expression before arrow
        limit_point = eq_str[arrow_index + 1:].strip() # Get the limit point 
        if '+' in limit_point:
            limit_expr = smp.limit(smp.parse_expr(limit_expr_str), x, limit_point.replace("+", ""), "+")
        elif '-' in limit_point:
            limit_expr = smp.limit(smp.parse_expr(limit_expr_str), x, limit_point.replace("-", ""), "-")
        else:
            limit_expr = smp.limit(smp.parse_expr(limit_expr_str), x, limit_point)

        limit_expr_str = limit_expr_str.replace("**", "^")
        limit_expr = limit_expr.replace("**", "^")
        await ctx.send(f"Limit of {limit_expr_str} as x -> {limit_point}: " + str(limit_expr))
    except Exception as e:
        await ctx.send(f"Error finding limit: {str(e)}")

@client.command()
async def derivative(ctx, *expr):
    try:
        x = smp.symbols('x')
        eq_str = " ".join(expr).replace("^", "**")
        eq_str = insertTimeX(eq_str)
        expr_diff = smp.Derivative(smp.parse_expr(eq_str), x)
        answer = expr_diff.doit()
        answer = answer.replace("**", "^")
        eq_str = eq_str.replace("**", "^")
        await ctx.send(f"{eq_str}: " + str(answer))
    except Exception as e:  
        await ctx.send(f"Error finding derivative: {str(e)}")

# Main entry point
def main():
    client.run(TOKEN)

if __name__ == '__main__':
    main()
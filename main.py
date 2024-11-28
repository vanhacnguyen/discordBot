from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message, Interaction
from discord.ext import commands
import discord

import io
import sympy as smp
import numpy as np
import matplotlib.pyplot as plt

load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = # place channel ID here
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

# helper method to convert tuple to a string and insert '*' to x
def convert_eq_str(eq):
    eq_str = " ".join(eq).replace("sinx", "sin(x)").replace("cosx", "cos(x)").replace("tanx", "tan(x)").replace("^", "**")
    #process each occurrence of 'x'
    x_index = eq_str.find("x")  #find the first occurrence
    while x_index != -1: 
        #check the character before 'x'
        if x_index > 0:  #not the first character
            char_before = eq_str[x_index - 1]
            if char_before.isdigit():  #if a digit is in front of x, add '*'
                eq_str = eq_str[:x_index] + "*x" + eq_str[x_index + 1:]
                x_index += 1  #move index forward to account for inserted '*'
        #find the next occurrence of 'x'
        x_index = eq_str.find("x", x_index + 1)
    return eq_str

@client.command()
# *equation is a tuple of strings
async def solve(ctx, *equation):
    try:
        eq_str = convert_eq_str(equation) # combine into a single string
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
        eq_str = convert_eq_str(expr)
        eq = smp.parse_expr(eq_str)
        answer = smp.factor(eq)
        answer = answer.replace("**", "^")
        await ctx.send(f"Factor of {eq_str}: " + str(answer))
    except Exception as e:
        await ctx.send(f"Error factoring the equation: {str(e)}")

@client.command()
async def limit(ctx, *expr):
    try:
        eq_str = convert_eq_str(expr)
        x = smp.symbols('x', real = True)

        #find the arrow to find limit point
        arrow_index = eq_str.index(">")
        limit_expr_str = eq_str[:arrow_index].strip() #get the expression before arrow
        limit_point = eq_str[arrow_index + 1:].strip() #get the limit point 
        parsed_expr = smp.parse_expr(limit_expr_str, {"sin": smp.sin, "cos": smp.cos, "tan": smp.tan})
        if '+' in limit_point:
            limit_expr = smp.limit(parsed_expr, x, limit_point.replace("+", ""), "+")
        elif '-' in limit_point:
            limit_expr = smp.limit(parsed_expr, x, limit_point.replace("-", ""), "-")
        else:
            limit_expr = smp.limit(parsed_expr, x, limit_point)

        limit_expr_str = limit_expr_str.replace("**", "^")
        limit_expr = limit_expr.replace("**", "^")
        await ctx.send(f"Limit of {limit_expr_str} as x -> {limit_point}: " + str(limit_expr))
    except Exception as e:
        await ctx.send(f"Error finding limit: {str(e)}")

@client.command()
async def derivative(ctx, *expr):
    try:
        x = smp.symbols('x')
        eq_str = convert_eq_str(expr)
        #parse sin(x), cos(x), tan(x) into sympy expression
        parsed_expr = smp.parse_expr(eq_str, {"sin": smp.sin, "cos": smp.cos, "tan": smp.tan})

        expr_diff = smp.Derivative(parsed_expr, x)
        answer = expr_diff.doit()
        eq_str = eq_str.replace("**", "^").replace("*","")
        pretty_answer = smp.pretty(answer).replace("*", "") #pretty print to read

        #back-tick for discord code format
        await ctx.send(f"Derivative of {eq_str}: \n```{pretty_answer}```")
    except Exception as e:  
        await ctx.send(f"Error finding derivative: {str(e)}")

@client.command()
async def integrate(ctx, *expr):
    try:
        x = smp.symbols('x')
        expr_str = convert_eq_str(expr)
        parsed_expr = smp.parse_expr(expr_str, {"sin": smp.sin, "cos": smp.cos, "tan": smp.tan})
        expr_integral = smp.integrate(parsed_expr, x)
        pretty_answer = smp.pretty(expr_integral).replace("*", "")
        expr_str = expr_str.replace("**", "^").replace("*","")
        await ctx.send(f"Integrals of {expr_str}: \n```{pretty_answer}```")
    except Exception as e:
        await ctx.send(f"Error finding integrals: {str(e)}")
@client.command()     
async def graphEquation(ctx, *equation):
    try:
        eq_str = convert_eq_str(equation)
        try: 
            parsed_expr = smp.parse_expr(eq_str)
        except smp.SympifyError as e:
            await ctx.send(f"Invalid equation. Error {str(e)}")
            return
        x = smp.symbols('x')
        x_vals = np.linspace(-10, 10, 100)

        expr_f = smp.lambdify(x, parsed_expr) #convert sympy expressions into python functions
        y_vals = expr_f(x_vals) #evaluate each x_vals for plotting y

        plt.figure()
        plt.plot(x_vals, y_vals, label=f"${eq_str}$")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.axhline(0, color = "black", linewidth = 0.5, linestyle = "--")
        plt.axvline(0, color = "black", linewidth = 0.5, linestyle = "--")
        plt.grid(True)
        plt.legend()

        buffer = io.BytesIO() #hold image data in memory temporarily instead of saving file
        plt.savefig(buffer, format='png') #hold image data into the buffer
        buffer.seek(0) #reset the cursor to the beginning
        #send image
        await ctx.send(file=discord.File(fp=buffer, filename='graph.png'))
        buffer.close()
        plt.close()
    except Exception as e:
        await ctx.send("Error graphing:" + str(e))
# Main entry point
def main():
    client.run(TOKEN)

if __name__ == '__main__':
    main()
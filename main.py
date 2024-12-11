from typing import Final
import os
from dotenv import load_dotenv
from discord import app_commands, Intents
from discord.ext import commands
import discord

import io
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
    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} commands: {[cmd.name for cmd in synced]}")
    except Exception as e:
        print("Failed to sync commands: " + str(e))
    await channel.send("Hello! Mad_Scientist is ready!")

# helper method to convert tuple to a string and insert '*' to x
def convert_eq_str(eq: str) -> str:
    eq_str = "".join(eq).replace("sinx", "sin(x)").replace("cosx", "cos(x)").replace("tanx", "tan(x)").replace("^", "**")
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

@client.tree.command(name="solve", description="Solve the equation")
@app_commands.describe(
    equation="The equation to evaluate",
    term="The term after the =")
async def solve_command(interaction, equation: str, term: str):
    try:
        eq_str = convert_eq_str(equation) # combine into a single string
        x = smp.symbols('x')

        # parse_expr parses variable left, right into mathematical expression
        eq = smp.Eq(smp.parse_expr(eq_str), smp.parse_expr(term))
        
        answer = smp.solve(eq, x) # solve eq for x
        displayed_answer = answer.replace("**", "^")
        await interaction.response.send_message(f"Solve {equation} = {term}: " + str(displayed_answer))
    except Exception as e:
        await interaction.response.send_message(f"Error solving the equation: {str(e)}", ephemeral = True)

@client.tree.command(name="factor", description="Factor the expression")
@app_commands.describe(
    expression="The expression to evaluate")
async def factor_command(interaction, expression: str):
    try:
        eq_str = convert_eq_str(expression)
        eq = smp.parse_expr(eq_str)
        answer = smp.factor(eq)
        display_expr = eq_str.replace("**", "^")
        display_answer = str(answer).replace("**", "^")
        await interaction.response.send_message(f"Factor of {display_expr}: " + str(display_answer))
    except Exception as e:
        await interaction.response.send_message(f"Error factoring the equation: {str(e)}", ephemeral=True)

# Define the 'limit' slash command
@client.tree.command(name="limit", description="Calculate the limit")
@app_commands.describe(
    expression="The expression to evaluate",
    limit_point="The point to which x approaches")
async def limit_command(interaction, expression: str, limit_point: str):
    try:
        x = smp.symbols('x')

        expression_str = convert_eq_str(expression) #get the expression
        parsed_expr = smp.parse_expr(expression_str, {"sin": smp.sin, "cos": smp.cos, "tan": smp.tan})
        parsed_expr = smp.simplify(parsed_expr)  # Simplify the expression

        direction = None
        if limit_point.endswith('+'):
            direction = '+'
            limit_point = limit_point[:-1]  # Remove '+' for numeric conversion
        elif limit_point.endswith('-'):
            direction = '-'
            limit_point = limit_point[:-1]  # Remove '-' for numeric conversion

        point = smp.parse_expr(limit_point)  #parse the limit point 

        # Compute the limit
        if direction:
            limit_result = smp.limit(parsed_expr, x, point, dir=direction)
        else:
            limit_result = smp.limit(parsed_expr, x, point)

        display_expr = expression_str.replace("**", "^")
        await interaction.response.send_message(f"Limit of {display_expr} as x -> {limit_point}: " + str(limit_result))
    except Exception as e:
        await interaction.response.send_message(f"Error finding limit: {str(e)}", ephemeral=True)

@client.tree.command(name="derivative", description="Find derivative of the expression")
@app_commands.describe(
    expression="The expression to evaluate")
async def derivative_command(interaction, expression: str):
    try:
        x = smp.symbols('x')
        eq_str = convert_eq_str(expression)
        #parse sin(x), cos(x), tan(x) into sympy expression
        parsed_expr = smp.parse_expr(eq_str, {"sin": smp.sin, "cos": smp.cos, "tan": smp.tan})

        expr_diff = smp.Derivative(parsed_expr, x)
        answer = expr_diff.doit()
        eq_str = eq_str.replace("**", "^").replace("*","")
        pretty_answer = smp.pretty(answer).replace("*", "") #pretty print to read

        #back-tick for discord code format
        await interaction.response.send_message(f"Derivative of {eq_str}: \n```{pretty_answer}```")
    except Exception as e:  
        await interaction.response.send_message(f"Error finding derivative: {str(e)}")

@client.tree.command(name="integrate", description="Find integral of the expression")
@app_commands.describe(
    expression="The expression to evaluate")
async def integrate(interaction, expression: str):
    try:
        x = smp.symbols('x')
        expr_str = convert_eq_str(expression)
        parsed_expr = smp.parse_expr(expr_str, {"sin": smp.sin, "cos": smp.cos, "tan": smp.tan})
        expr_integral = smp.integrate(parsed_expr, x)
        pretty_answer = smp.pretty(expr_integral).replace("*", "")
        expr_str = expr_str.replace("**", "^").replace("*","")
        await interaction.response.send_message(f"Integrals of {expr_str}: \n```{pretty_answer}```")
    except Exception as e:
        await interaction.response.send_message(f"Error finding integrals: {str(e)}")

@client.tree.command(name="graph", description="Graph the equation")
@app_commands.describe(
    expression="The expression to evaluate") 
async def graphEquation(interaction, expression: str):
    try:
        eq_str = convert_eq_str(expression)
        try: 
            parsed_expr = smp.parse_expr(eq_str)
        except smp.SympifyError as e:
            await interaction.response.send_message(f"Invalid equation. Error {str(e)}")
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
        await interaction.response.send_message(file=discord.File(fp=buffer, filename='graph.png'))
        buffer.close()
        plt.close()
    except Exception as e:
        await interaction.response.send_message("Error graphing:" + str(e))
# Main entry point
def main():
    client.run(TOKEN)

if __name__ == '__main__':
    main()
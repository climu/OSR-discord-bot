import discord
from discord.ext import commands
import datetime
from datetime import datetime

bot = commands.Bot(command_prefix='@')
users = {}

@bot.command()
async def looking(ctx):
    users[ctx.message.author.name] = str(datetime.now())
    for k,v in users.items():
        await ctx.send("As of " + v + ",  " + str(k) + " is looking for a game.")

@bot.command()
async def not_looking(ctx):
    del users[ctx.message.author.name]
    await ctx.send(str(ctx.message.author.name) + "is no longer looking for a game.")

@bot.command()
async def whos_looking(ctx):
    for k,v in users.items():
        await ctx.send(str(k) + " is looking for a game.")

@bot.command()
async def info(ctx):
    embed = discord.Embed(title="Looking For Game Bot", description="Keeps track of who is currently looking for a game.", color=0xeee657)
    embed.add_field(name="Author", value="FluffM")
    await ctx.send(embed=embed)

bot.remove_command('help')

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Looking For Game Bot", description="Keeps track of who is currently looking for a game. The following commands are available:", color=0xeee657)

    embed.add_field(name="@looking", value="Sets your status to looking.", inline=False)
    embed.add_field(name="@not_looking", value="Sets your status to not looking.", inline=False)
    embed.add_field(name="@whos_looking", value="Tells you who is currently looking.", inline=False)
    embed.add_field(name="@info", value="Gives a little info about the bot.", inline=False)
    embed.add_field(name="@help", value="Gives this message.", inline=False)

    await ctx.send(embed=embed)

bot.run('NDI5MjY3Nzc0NTk0ODc1Mzkz.DZ_XrA.DmS3hEHTAJju95TnsQJt1YxDAfg')

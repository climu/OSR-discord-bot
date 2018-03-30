import discord
from discord.ext import commands
import datetime
from datetime import datetime

bot = commands.Bot(command_prefix='@')
users = {}

@bot.command()
async def LFG(ctx):
    role = discord.utils.get(ctx.message.guild.roles, name="LFG")
    if role in ctx.message.author.roles:
        del users[ctx.message.author.name]
        await ctx.send(str(ctx.message.author.name) + "is no longer looking for a game.")
    else:
        users[ctx.message.author.name] = str(datetime.now())
        await ctx.message.author.add_roles(role)
        for k,v in users.items():
            await ctx.send("As of " + v + ",  " + str(k) + " is looking for a game.")

@bot.command()
async def whos_LFG(ctx):
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

    embed.add_field(name="@LFG", value="Toggles your role for LFG.", inline=False)
    embed.add_field(name="@whos_LFG", value="Tells you who is currently looking.", inline=False)
    embed.add_field(name="@info", value="Gives a little info about the bot.", inline=False)
    embed.add_field(name="@help", value="Gives this message.", inline=False)

    await ctx.send(embed=embed)

bot.run('NDI5MjY3Nzc0NTk0ODc1Mzkz.DZ_XrA.DmS3hEHTAJju95TnsQJt1YxDAfg')

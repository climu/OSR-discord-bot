import os
import discord
from discord.ext import commands
import datetime
from datetime import datetime
from datetime import timedelta
import asyncio
import requests

bot = commands.Bot(command_prefix='&')
guild_id = 287487891003932672

id = {
    'LFG': 433023079183286282,
    'tusmegoers': 462186851747233793,
    'reviewers': 462187005602955266,
    'dan': 462186943221071872,
    'sdk': 462186975240388620,
    'ddk': 462187620156309514
}

# For the following commands, the calling message will be deleted
del_commands = [
    "whos_lfg",
    "whos_LFG",
    "lfg",
    "game",
    "LFG",
    "no_LFG",
    "no_lfg",
    "no_game"
]

minutes_in_a_day = 1440
expiration_times = {}
role = 0


async def get_role():
    global role
    if role == 0:
        role = discord.utils.get(bot.get_guild(guild_id).roles, name="LFG")

@bot.event
async def on_message(message):
    if any("!" + item == message.content for item in del_commands):
        await message.delete()
    await bot.process_commands(message)

@bot.command(pass_context=True)
async def cho(ctx):
    embed = discord.Embed()
    embed.set_image(url="https://cdn.discordapp.com/attachments/456532168370290695/461802038276390923/cho.png")
    await ctx.send(embed=embed)

@bot.command(pass_context=True)
async def cho_hug(ctx):
    embed = discord.Embed()
    embed.set_image(url="https://cdn.discordapp.com/attachments/430062036903395329/444192620504416268/WroCzKKKj7o.png")
    await ctx.send(embed=embed)

@bot.command(pass_context=True)
async def chang_ho(ctx):
    embed = discord.Embed()
    embed.set_image(url="https://cdn.discordapp.com/attachments/430062036903395329/432619582054858806/153746110828-nong01.png")
    await ctx.send(embed=embed)

@bot.command(pass_context=True)
async def yuta(ctx):
    embed = discord.Embed()
    embed.set_image(url="https://cdn.discordapp.com/attachments/430062036903395329/432619582054858806/153746110828-nong01.png")
    await ctx.send(embed=embed)

@bot.command(pass_context=True)
async def kj_facepalm(ctx):
    embed = discord.Embed()
    embed.set_image(url="https://cdn.discordapp.com/attachments/366870031285616651/461813881900236821/iozlnkjg.png")
    await ctx.send(embed=embed)


@bot.command(pass_context=True, aliases=["lfg", "game", "go", "play"])
async def LFG(ctx, minutes=minutes_in_a_day):
    if not str(ctx.message.channel) == "game_request":
        await ctx.send("Please " + ctx.message.author.mention + ", use the appropriate channel for this command.")
    else:
        if role in ctx.message.author.roles:
            await ctx.message.author.remove_roles(role)
            await ctx.send(str(ctx.message.author.name) + " is no longer looking for a game.")
        else:
            expiration_time = datetime.now() + timedelta(minutes=minutes)
            expiration_times[ctx.author.id] = expiration_time
            await ctx.message.author.add_roles(role)
            await ctx.send("Hey, <@&" + str(id["LFG"]) + ">! " + str(ctx.message.author.name) + " is looking for a game.")


@bot.command(pass_context=True, aliases=["no_lfg", "no_game", "remove_lfg"])
async def no_LFG(ctx, minutes=minutes_in_a_day):
    if not str(ctx.message.channel) == "game_request":
        await ctx.send("Please " + ctx.message.author.mention + ", use the appropriate channel for this command.")
    else:
        if role in ctx.message.author.roles:
            await ctx.message.author.remove_roles(role)
            await ctx.send(str(ctx.message.author.name) + " is no longer looking for a game.")


@bot.command(pass_context=True, aliases=["whos_lfg"])
async def whos_LFG(ctx):
    if not str(ctx.message.channel) == "game_request":
        await ctx.send("Please " + ctx.message.author.mention + ", use the appropriate channel for this command.")
    else:
        currently_looking = []
        role = discord.utils.get(ctx.message.guild.roles, name="LFG")
        for member in ctx.message.guild.members:
            if role in member.roles:
                if str(member.status) == "online":
                    currently_looking.append(member)
        if len(currently_looking) > 0:
            uids = [member.id for member in currently_looking]
            infos = requests.get("https://openstudyroom.org/league/discord-api/", params={'uids': uids}).json()
            message = ctx.message.author.mention + ": The following users are looking for a game:\n"
            for user in currently_looking:
                message += '**' + user.name + '**'
                info = infos.get(str(user.id))
                if info is not None:
                    kgs_username = info.get('kgs_username')
                    kgs_rank = info.get('kgs_rank')
                    ogs_username = info.get('ogs_username')
                    ogs_rank = info.get('ogs_rank')
                    if kgs_username is not None or ogs_username is not None:
                        message += ':'
                        if ogs_username is not None:
                            message += ' OGS - ' + ogs_username + ' (' + ogs_rank + ') |'
                        if kgs_username is not None:
                            message += ' KGS - ' + kgs_username + ' (' + kgs_rank + ')'
                message += ' \n'
            await ctx.send(message)
        else:
            await ctx.send(ctx.message.author.mention + ": Nobody is looking for a game. :(")


@bot.command(pass_context=True)
async def info(ctx):
    embed = discord.Embed(title="Looking For Game Bot", description="Keeps track of who is currently looking for a game.", color=0xeee657)
    await ctx.send(embed=embed)

bot.remove_command('help')

@bot.command(pass_context=True)
async def testing(ctx):
    r = requests.get("https://openstudyroom.org/league/discord-api/", params={'uids': uids}).json()
    print(r)

@bot.command(pass_context=True)
async def help(ctx):
    embed = discord.Embed(title="Looking For Game Bot", description="Keeps track of who is currently looking for a game. The following commands are available:", color=0xeee657)

    embed.add_field(name="!LFG [minutes]", value="Toggles your role for LFG. You can limit the length of time you will be LFG by entering a number of minutes after the command.", inline=False)
    embed.add_field(name="!whos_LFG", value="Tells you who is currently looking.", inline=False)
    embed.add_field(name="!info", value="Gives a little info about the bot.", inline=False)
    embed.add_field(name="!help", value="Gives this message.", inline=False)

    await ctx.send(embed=embed)


async def check_LFG():
    await bot.wait_until_ready()
    await get_role()
    while not bot.is_closed:
        for uid, expiration_time in expiration_times.items():
            if datetime.now() > expiration_time:
                await discord.utils.get(bot.get_all_members(), id=uid).remove_roles(role)

        await asyncio.sleep(60)

bot.loop.create_task(check_LFG())
bot.run(os.environ["LFG_TOKEN"])

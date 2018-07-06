import os
import discord
from discord.ext import commands
import datetime
from datetime import datetime
from datetime import timedelta
import asyncio
import requests

from config import roles_dict, del_commands, minutes_in_a_day, guild_id, expiration_times, prefix
from utils import *

bot = commands.Bot(command_prefix=prefix)
roles_are_set = False

async def get_roles():
    global roles_are_set
    if not roles_are_set:
        for name, role_dict in roles_dict.items():
            role = discord.utils.get(bot.get_guild(guild_id).roles, id=role_dict['id'])
            roles_dict[name].update({"role": role})
        roles_are_set = True


@bot.event
async def on_ready():
    """Display a message for which time was bot last updated."""
    channel = bot.get_channel(463639475751354368)
    msg = "<@" + str(461792018843172866) + "> was just deployed."
    await channel.send(msg)


@bot.event
async def on_message(message):
    cmd = message.content[1:].split(" ")[0]
    if message.content.startswith(prefix) and cmd in del_commands:
        await message.delete()
    try:
        await bot.process_commands(message)
    except commands.CommandNotFound:
        pass



# Here are the pictures commands. That's just for fun.


@bot.command(pass_context=True)
async def cho(ctx):
    embed = discord.Embed(description="Requested by: " + ctx.author.mention)
    embed.set_thumbnail(url=ctx.author.avatar_url)
    embed.set_image(url="https://cdn.discordapp.com/attachments/456532168370290695/461802038276390923/cho.png")
    await ctx.send(embed=embed)


@bot.command(pass_context=True)
async def cho_hug(ctx):
    embed = discord.Embed(description="Requested by: " + ctx.author.mention)
    embed.set_thumbnail(url=ctx.author.avatar_url)
    embed.set_image(url="https://cdn.discordapp.com/attachments/430062036903395329/444192620504416268/WroCzKKKj7o.png")
    await ctx.send(embed=embed)


@bot.command(pass_context=True)
async def chang_ho(ctx):
    embed = discord.Embed(description="Requested by: " + ctx.author.mention)
    embed.set_thumbnail(url=ctx.author.avatar_url)
    embed.set_image(url="https://cdn.discordapp.com/attachments/430062036903395329/432619582054858806/153746110828-nong01.png")
    await ctx.send(embed=embed)


@bot.command(pass_context=True)
async def yuta(ctx):
    embed = discord.Embed(description="Requested by: " + ctx.author.mention)
    embed.set_thumbnail(url=ctx.author.avatar_url)
    embed.set_image(url="https://cdn.discordapp.com/attachments/430062036903395329/432619582054858806/153746110828-nong01.png")
    await ctx.send(embed=embed)


@bot.command(pass_context=True)
async def kj_facepalm(ctx):
    embed = discord.Embed(description="Requested by: " + ctx.author.mention)
    embed.set_thumbnail(url=ctx.author.avatar_url)
    embed.set_image(url="https://cdn.discordapp.com/attachments/366870031285616651/461813881900236821/iozlnkjg.png")
    await ctx.send(embed=embed)

# Roles managment start here


@bot.command(pass_context=True, aliases=["lfg", "game", "LFG", "play", "GO", "PLAY", "GAME"])
async def go(ctx, minutes=minutes_in_a_day):
    role_dict = roles_dict['go']

    if str(ctx.message.channel) not in role_dict['allowed_channels']:
        message = "Please " + ctx.message.author.mention + ", use the appropriate channels for this command: "
        message += ' '.join(role_dict['allowed_channels'])
        await ctx.send(message)
        return

    role = role_dict["role"]
    #no need to call get_user here because ctx.message.author is already a member instance
    user = ctx.message.author
    infos = requests.get("https://openstudyroom.org/league/discord-api/", params={'uids': [user.id]}).json()
    expiration_time = datetime.now() + timedelta(minutes=minutes)
    expiration_times[ctx.author.id] = expiration_time
    if role in ctx.message.author.roles:
        await ctx.send("Hey, <@&" + str(role_dict["id"]) + ">! " + ctx.message.author.mention + user_rank(user, infos) + " is desperately looking for a game.")
    else:
        await ctx.message.author.add_roles(role)
        await ctx.send("Hey, <@&" + str(role_dict["id"]) + ">! " + ctx.message.author.mention + user_rank(user, infos) + " is looking for a game.")


@bot.command(pass_context=True)
async def dan(ctx):
    await add_role(ctx, 'dan')


@bot.command(pass_context=True)
async def sdk(ctx):
    await add_role(ctx, 'sdk')


@bot.command(pass_context=True)
async def ddk(ctx):
    await add_role(ctx, 'ddk')


@bot.command(pass_context=True)
async def tsumego(ctx):
    await add_role(ctx, 'tsumego')


@bot.command(pass_context=True)
async def review(ctx):
    await add_role(ctx, 'review')

@bot.command(pass_context=True)
async def no(ctx, role_name):
    role_dict = roles_dict.get(role_name)
    if role_dict is None:
        return
    if str(ctx.message.channel) not in role_dict['allowed_channels']:
        message = "Please " + ctx.message.author.mention + ", use the appropriate channels for this command: "
        message += ', '.join(role_dict['allowed_channels'])
        await ctx.send(message)
        return
    role = role_dict["role"]

    await ctx.message.author.remove_roles(role)
    await ctx.send(ctx.message.author.mention + " is no longer " + role_dict["verbose"] + ".")



@bot.command(pass_context=True, aliases=["user"])
async def who(ctx, username):
    user = get_user(username, bot)
    if user is not None:
        infos = requests.get("https://openstudyroom.org/league/discord-api/", params={'uids': [user.id]}).json()
        if not infos:
            message = user.mention + ' was too lazy to link their OSR account with their discord. They just have to folow this [link](https://openstudyroom.org/discord/)!'
            embed = discord.Embed(title="Lazy " + user.name, description=message, color=0xeee657)
            await ctx.send(embed=embed)
        else:
            message = user_info_message(user, infos)
            await ctx.send(message)
    else:
        await ctx.send("We have no such user in here. Sorry.")


@bot.command(pass_context=True, aliases=["list"])
async def whos(ctx, role_name):
    role_dict = roles_dict.get(role_name)
    if role_dict is None:
        return
    if str(ctx.message.channel) not in role_dict['allowed_channels']:
        message = "Please " + ctx.message.author.mention + ", use the appropriate channels for this command: "
        message += ' '.join(role_dict['allowed_channels'])
        await ctx.send(message)
        return
    role = role_dict["role"]

    users = [x for x in role.members if str(x.status) == "online"]
    if len(users) > 0:
        uids = [member.id for member in users]
        infos = requests.get("https://openstudyroom.org/league/discord-api/", params={'uids': uids}).json()
        message = ctx.message.author.mention + ": The following users are " + role_dict['verbose'] + ":\n"
        for user in users:
            message += user_info_message(user, infos)
        await ctx.send(message)
    else:
        await ctx.send("Sorry " + ctx.message.author.mention + ". Unfortunately, nobody is " + role_dict['verbose'] + " right now. :(")

@bot.command(pass_context=True)
async def info(ctx):
    desc = "Keeps track of who is currently looking for a game.\nhttps://github.com/climu/OSR-discord-bot"
    embed = discord.Embed(title="OSR bot", description=desc, color=0xeee657)
    await ctx.send(embed=embed)

bot.remove_command('help')


@bot.command(pass_context=True)
async def help(ctx):
    desc = "Help organise this discord channel. The following commands are available:"
    embed = discord.Embed(title="OSR Bot", description=desc, color=0xeee657)
    value = "To avoid using `@here`, users can choose to be in groups of interest:\n\n"
    value += "- **!go**: will assign you the ``@player` role. This is for people who are interested in playing OSR games. Tag `@player` when you are looking for a game.\n\n"
    value += "- **!tsumego**: will assign you the `@tsumegoer` role. This is for people who are interested in tsumego study. Tag `@tsumegoer` when you post a new tsumego or have a related question.\n\n"
    value += "- **!review**: will assign you the `@reviewer` role. This is for people who are available to give game reviews. Tag `@reviewer` to ask for a game review.\n\n"
    value += "- **!dan/sdk/ddk**: will assign you the `@dan`, `@sdk` or `@ddk` role. By saying your approximate level, it will allow users to tag the appropriate group when lookinSg for game or help. Feel free to sign up to more than one groups.\n\n"
    embed.add_field(name="Add a role", value=value, inline=False)
    embed.add_field(name="Remove a role", value="**!no [role]**: will remove the role. For instance, `!no go` will remove you from the `@player` role", inline=False)
    embed.add_field(name="List all online users in with a specific role", value="**!list [role]**: will list all online users with the said role. For instance `!list tsumego` will list all online users of the `@tsumego` role.", inline=False)
    embed.add_field(name="Get one user info", value="**!who [username or #discriminator]**: will give informations about a user given his nickname or discriminator. For instance, my discriminator is `#9501`.", inline=False)
    embed.add_field(name="!info", value="Gives a little info about the bot.", inline=False)
    embed.add_field(name="!help", value="Gives this message.", inline=False)
    await ctx.send(embed=embed)


async def check_LFG():
    await bot.wait_until_ready()
    await get_roles()
    while not bot.is_closed():
        to_clear = []
        for uid, expiration_time in expiration_times.items():
            if datetime.now() > expiration_time:
                to_clear.append(uid)
                await discord.utils.get(bot.get_all_members(), id=uid).remove_roles(roles_dict['go']['role'])

        for uid in to_clear:
            del expiration_times[uid]
        await asyncio.sleep(60)

bot.loop.create_task(check_LFG())
bot.run(os.environ["LFG_TOKEN"])

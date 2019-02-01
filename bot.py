import os
import discord
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio
import requests
import aiohttp
import re
import kgs
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
from typing import Dict, List, Tuple  # noqa

from config import roles_dict, guild_id, prefix, channels
from utils import add_footer, add_role, get_user
from utils import user_info_message, user_info_embed, user_rank


bot = commands.Bot(command_prefix=prefix)
roles_are_set = False
kgs_to_send = []
SPECIAL_MESSAGES = {}  # type: Dict[int, SpecialMessage]


class UnsentMessage():
    def __init__(self, message: str, embed: discord.Embed) -> None:
        self.message = message
        self.embed = embed

    async def send(self, ctx: commands.Context) -> None:
        await ctx.send(self.message, embed=self.embed)


class SpecialMessage():
    def __init__(self, message: discord.Message, originator: discord.User) -> None:
        self.message = message
        self.originator = originator

    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User) -> None:
        pass


class WhoMessage(SpecialMessage):
    def __init__(self, message: discord.Message, originator: discord.User, matches: List[discord.User]) -> None:
        super().__init__(message, originator)
        self.matches = matches

    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User) -> None:
        if user != self.originator:
            return

        try:
            idx = int(reaction.emoji[0]) - 1

            info = get_user_info(self.matches[idx])
            add_footer(info.embed, self.originator)
            await self.message.clear_reactions()
            # This needs to be here for some reason, else we get an extra name after edit...
            await self.message.edit(embed=None)
            await self.message.edit(content=info.message, embed=info.embed)
            del SPECIAL_MESSAGES[self.message.id]
        except (ValueError, IndexError):
            # Wrong emoji
            return


async def get_roles():
    global roles_are_set
    if not roles_are_set:
        for name, role_dict in roles_dict.items():
            role = discord.utils.get(bot.get_guild(guild_id).roles, id=role_dict['id'])
            roles_dict[name].update({"role": role})
        roles_are_set = True


# When a new member joins, tag them in "welcome" channel and let them know of our bot
@bot.event
async def on_member_join(member):
    """On member join, display welcome message and add the player role."""
    if bot.user.name != "OSR Bot":
        welcome_ch = bot.get_channel(channels["welcome"])
        general_ch = bot.get_channel(channels["general"])
        bot_commands_ch = bot.get_channel(channels["bot-commands"])
        msg = """Welcome to OSR {member}! We are delighted to have you with us.\n
    I am here to assist you. You can either send me a private message or invoke my commands in the correct channels.
    Try, for example, to send `!help` to me, or type it in {bot_commands} to see what I can do for you.
    Otherwise, simply introduce yourself in {general} or talk to any of our team members.\n
    You have been assigned the "player" role meaning you are interested in playing go games.
    If you don't like that, you can always remove yourself the role byt typing `!no go`.\n
    Finally, you can find out more about Open Study Room at https://openstudyroom.org/
    We hope that you enjoy your time with us! :  )""".format(member=member.mention,
                                                             bot_commands=bot_commands_ch.mention,
                                                             general=general_ch.mention)
        await welcome_ch.send(msg)
        role_dict = roles_dict['go']
        role = role_dict["role"]
        await member.add_roles(role)


@bot.event
async def on_message(message):
    ctx = await bot.get_context(message)
    if ctx.command is None:
        # Not a valid command (Normal message or invalid command)
        #If it's in kgs channel we add it in the kgs_to_send queue
        if message.channel == bot.get_channel(channels["kgs"]):
            if ctx.author != bot.user:
                text = str(ctx.author.display_name) + ": " + message.content
                kgs_to_send.append(text)

        if message.content.startswith(prefix):
            await message.delete()
            cmd = message.content.split(" ")[0][1:]
            desc = "I am not currently programmed for the command: " + cmd + "\n\n"
            desc += "Please see the available commands by typing `!help`."
            embed = discord.Embed(title="Command " + cmd + " not found.", description=desc, color=0xeee657)
            embed.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/464175979406032897/464915353382813698/error.png")
            add_footer(embed, ctx.author)
            await message.channel.send(embed=embed)
        return

    await bot.process_commands(message)


# Here are the pictures commands. That's just for fun.

PICTURE_COMMANDS = {
        "cho": "https://cdn.discordapp.com/attachments/456532168370290695/461802038276390923/cho.png",
        "cho_hug": "https://cdn.discordapp.com/attachments/430062036903395329/444192620504416268/WroCzKKKj7o.png",
        "chang_ho": "https://cdn.discordapp.com/attachments/430062036903395329/432619582054858806/153746110828-nong01.png",
        "yuta": "https://cdn.discordapp.com/attachments/287487891003932672/461811731359072259/vfcp43js2.png",
        "kj_facepalm": "https://cdn.discordapp.com/attachments/366870031285616651/461813881900236821/iozlnkjg.png",
        "scary": "https://cdn.discordapp.com/attachments/463639475751354368/467077666298789908/Head.png"
        }


@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User) -> None:
    if reaction.message.id in SPECIAL_MESSAGES:
        await SPECIAL_MESSAGES[reaction.message.id].on_reaction_add(reaction, user)


def picture_command(url):
    async def inner(ctx):
        embed = discord.Embed(description="Requested by: " + ctx.author.mention)
        embed.set_thumbnail(url=ctx.author.avatar_url)
        embed.set_image(url=url)
        await ctx.send(embed=embed)
    return inner


for name, url in PICTURE_COMMANDS.items():
    bot.command(pass_context=True, name=name)(picture_command(url))

# Roles managment start here

@bot.command(pass_context=True)
async def go(ctx):
    await add_role(ctx, 'go')


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
async def rengo(ctx):
    await add_role(ctx, 'rengo')


@bot.command(pass_context=True)
async def goquest(ctx):
    await add_role(ctx, 'goquest')


@bot.command(pass_context=True)
async def nine(ctx):
    await add_role(ctx, 'nine')


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


def get_user_info(user: discord.User) -> UnsentMessage:
    infos = requests.get("https://dev.openstudyroom.org/league/discord-api/", params={'uids': [user.id]}).json()
    if not infos:
        message = ('{} was too lazy to link their OSR account with their discord. '
                   'They just have to follow this [link](https://openstudyroom.org/discord/)!').format(user.mention)
        embed = discord.Embed(title="Lazy " + user.name, description=message, color=0xeee657)
        return UnsentMessage("", embed)
    else:
        embed = user_info_embed(user, infos)
        return UnsentMessage("", embed)


@bot.command(pass_context=True)
async def rank(ctx: commands.Context, username: str = None) -> None:

    if username is None:
        last_message = await ctx.message.channel.history(limit=1).flatten()
        user = last_message[0].author
    else:
        user = get_user(username, bot)

    if user is not None:
        infos = requests.get("https://dev.openstudyroom.org/league/discord-api/", params={'uids': [user.id]}).json()
        info = infos.get(str(user.id))
        if info is not None:
            kgs_username = info.get('kgs_username')
            kgs_rank = info.get('kgs_rank')
            ogs_username = info.get('ogs_username')
            ogs_rank = info.get('ogs_rank')
            if kgs_username is not None or ogs_username is not None:
                embed = discord.Embed(title="KGS rank history for " + str(username), color=0xeee657)
                embed.set_image(url="http://www.gokgs.com/servlet/graph/"+kgs_username+"-en_US.png")
                add_footer(embed, ctx.author)
                await ctx.send(embed=embed)
        return
    # Look for nearest matches, if they exist
    users = bot.get_guild(guild_id).members  # type: List[discord.Member]
    # Just using sequencematcher because its simple and no need to install extra Library
    # If keen on better distrance metrics, look at installing Jellyfish or Fuzzy Wuzzy
    similarities = [(member,
                     max(SequenceMatcher(None, username.lower(), member.display_name.lower()).ratio(),
                         SequenceMatcher(None, username.lower(), member.name.lower()).ratio())) for member in users]
    similarities.sort(key=lambda tup: tup[1], reverse=True)

    # unlikely to get 5 with >70% match anyway...
    top_matches = [x for x in similarities[:5] if x[1] > 0.7]  # type: List[Tuple[discord.Member, float]]

    uids = [x[0].id for x in top_matches]
    infos = requests.get("https://dev.openstudyroom.org/league/discord-api/", params={'uids': uids}).json()

    # Split and recombine so that OSR members appear top of list
    osr_members = [x for x in top_matches if infos.get(str(x[0].id)) is not None]
    not_osr_members = [x for x in top_matches if x not in osr_members]
    top_matches = osr_members + not_osr_members

    message = ''
    for _i, x in enumerate(top_matches):
        message += '\n{}\N{COMBINING ENCLOSING KEYCAP}**{}**#{} {}'.format(_i + 1,
                                                                           x[0].display_name,
                                                                           x[0].discriminator,
                                                                           user_rank(x[0], infos))
    if username in roles_dict:
        message += "\n\n However, `" + username + "` is a valid role. Did you mean `!list " + username + "`?"
    nearest_or_sorry = '", nearest matches:' if top_matches else '", sorry'
    embed = discord.Embed(description=message, title='No users by the exact name "' + username + nearest_or_sorry)
    add_footer(embed, ctx.message.author)
    msg = await ctx.send(embed=embed)


@bot.command(pass_context=True, aliases=['user'])
async def who(ctx: commands.Context, username: str = None) -> None:

    if username is None:
        last_message = await ctx.message.channel.history(limit=2).flatten()
        user = last_message[1].author
    elif username is "me":
        last_message = await ctx.message.channel.history(limit=1).flatten()
        user = last_message[0].author
    else:
        user = get_user(username, bot)

    if user is not None:
        info = get_user_info(user)
        add_footer(info.embed, ctx.message.author)
        await info.send(ctx)
        return

    # Look for nearest matches, if they exist
    users = bot.get_guild(guild_id).members  # type: List[discord.Member]
    # Just using sequencematcher because its simple and no need to install extra Library
    # If keen on better distrance metrics, look at installing Jellyfish or Fuzzy Wuzzy
    similarities = [(member,
                     max(SequenceMatcher(None, username.lower(), member.display_name.lower()).ratio(),
                         SequenceMatcher(None, username.lower(), member.name.lower()).ratio())) for member in users]
    similarities.sort(key=lambda tup: tup[1], reverse=True)

    # unlikely to get 5 with >70% match anyway...
    top_matches = [x for x in similarities[:5] if x[1] > 0.7]  # type: List[Tuple[discord.Member, float]]

    uids = [x[0].id for x in top_matches]
    infos = requests.get("https://dev.openstudyroom.org/league/discord-api/", params={'uids': uids}).json()

    # Split and recombine so that OSR members appear top of list
    osr_members = [x for x in top_matches if infos.get(str(x[0].id)) is not None]
    not_osr_members = [x for x in top_matches if x not in osr_members]
    top_matches = osr_members + not_osr_members

    message = ''
    for _i, x in enumerate(top_matches):
        message += '\n{}\N{COMBINING ENCLOSING KEYCAP}**{}**#{} {}'.format(_i + 1,
                                                                           x[0].display_name,
                                                                           x[0].discriminator,
                                                                           user_rank(x[0], infos))
    if username in roles_dict:
        message += "\n\n However, `" + username + "` is a valid role. Did you mean `!list " + username + "`?"
    nearest_or_sorry = '", nearest matches:' if top_matches else '", sorry'
    embed = discord.Embed(description=message, title='No users by the exact name "' + username + nearest_or_sorry)
    add_footer(embed, ctx.message.author)
    msg = await ctx.send(embed=embed)

    for _i, match in enumerate(top_matches):  # type: Tuple[int, Tuple[discord.Member, float]]
        await msg.add_reaction(str(_i + 1) + '\N{COMBINING ENCLOSING KEYCAP}')

    SPECIAL_MESSAGES[msg.id] = WhoMessage(msg, ctx.message.author, [x[0] for x in top_matches])


@bot.command(pass_context=True, aliases=["whos"])
async def list(ctx, role_name):
    role_dict = roles_dict.get(role_name)
    if role_dict is None:
        return

    if str(ctx.message.channel) not in role_dict['allowed_channels']:
        message = "Please " + ctx.message.author.mention + ", use the appropriate channels for this command: "
        message += ' '.join(role_dict['allowed_channels'])
        await ctx.send(message)
        return
    role = role_dict["role"]

    online_users = [x for x in role.members if str(x.status) == "online"]
    idle_users = [y for y in role.members if str(y.status) == "idle"]
    users = online_users
    if len(users) > 0:
        if len(users) > 15:
            message = "Sorry, but there are too many users in the " + role_name + " group to list."
            await ctx.send(message)
            return

        uids = [member.id for member in users]
        infos = requests.get("https://dev.openstudyroom.org/league/discord-api/", params={'uids': uids}).json()
        message = ''
        message2 = ''
        for user in users:
            new_user_message = user_info_message(user, infos)
            if len(message) + len(new_user_message) < 2048:
                message += new_user_message
            else:
                message2 += new_user_message
        if message2 == '':
            message += "*" + str(len(idle_users)) + " more users are idle.*"
        else:
            message2 += "*" + str(len(idle_users)) + " more users are idle.*"

        title = "The following users are " + role_dict['verbose'] + ":"
        embed = discord.Embed(title=title, description=message)
        add_footer(embed, ctx.message.author)
        await ctx.send(embed=embed)

        if message2 != '':
            embed = discord.Embed(description=message2)
            add_footer(embed, ctx.message.author)
            await ctx.send(embed=embed)

    else:
        await ctx.send("Sorry {}. Unfortunately, nobody is {} right now. :(".format(ctx.message.author.mention,
                                                                                    role_dict['verbose']))


@bot.command(pass_context=True)
async def info(ctx):
    desc = "Help manage the OSR discord.\nhttps://github.com/climu/OSR-discord-bot"
    embed = discord.Embed(title="OSR bot", description=desc, color=0xeee657)
    add_footer(embed, ctx.author)
    await ctx.send(embed=embed)

bot.remove_command('help')


@bot.command(pass_context=True)
async def help(ctx, subject=None):
    if subject is None:
        desc = "Help organise this discord channel. The following commands are available:"
        embed = discord.Embed(title="OSR Bot", description=desc, color=0xeee657)
        embed.add_field(name="**!roles**",
                        value="Display help file regarding the Discord OSR roles system.",
                        inline=False)
        embed.add_field(name="**!who [username or #discriminator]**",
                        value=("Get one user info: will give informations about a user given his nickname or "
                               "discriminator. For instance, "
                               "my discriminator is `#{}`.").format(bot.user.discriminator),
                        inline=False)
        embed.add_field(name="**!league**", value="Find out about OSR leagues.", inline=False)
        embed.add_field(name="**!sensei [term]**",
                        value="Display information for a term from Sensei's Library.",
                        inline=False)
        embed.add_field(name="**!rank**", value="Get KGS rank history for a specific user.", inline=False)
        embed.add_field(name="**!info**", value="Gives a little info about the bot.", inline=False)
        embed.add_field(name="**!help**", value="Gives this message.", inline=False)
        embed.add_field(name="**!help osr**",
                        value="Find out how you can help with our community.",
                        inline=False)
        add_footer(embed, ctx.author)
        await ctx.send(embed=embed)
    else:
        if subject == "osr":
            title = "I like this project. How can I help?"
            message = ("There are many ways you can help the OSR project if you like to. "
                       "Those include but are not limited to:\n" +
                       " - Playing in our leagues.\n" +
                       " - Keeping OSR friendly and active.\n" +
                       " - Giving a couple of $/€ so we can pay for the server and set up quality teaching.\n" +
                       " - Help us run the community.\n" +
                       "You can find more details about that [here](https://openstudyroom.org/help-osr/).")
            embed = discord.Embed(title=title, description=message, color=0xeee657)
            add_footer(embed, ctx.author)
            await ctx.send(embed=embed)


@bot.command(pass_context=True)
async def roles(ctx):
    desc = "Help organise the discord channel by self-assigning various roles."
    embed = discord.Embed(title="Roles system", description=desc, color=0xeee657)
    value = "To avoid using `@here`, users can choose to be in groups of interest:\n\n"
    value += "- **!go**: will assign you the `@player` role. This is for people who are interested in playing OSR games. Tag `@player` when you are looking for a game.\n\n"
    value += "- **!nine**: will assign you the `@9x9` role for playing 9x9 games, similar to the `@player` role.\n\n"
    value += "- **!tsumego**: will assign you the `@tsumegoer` role. This is for people who are interested in tsumego study. Tag `@tsumegoer` when you post a new tsumego or have a related question.\n\n"
    value += "- **!review**: will assign you the `@reviewer` role. This is for people who are available to give game reviews. Tag `@reviewer` to ask for a game review.\n\n"
    value += "- **!dan/sdk/ddk**: will assign you the `@dan`, `@sdk` or `@ddk` role. By saying your approximate level, it will allow users to tag the appropriate group when lookinSg for game or help. Feel free to sign up to more than one groups.\n\n"
    value += "- **!goquest**: will assign you the `@GoQuest` role for playing games on that server.\n\n"
    embed.add_field(name="Add a role", value=value, inline=False)
    embed.add_field(name="Remove a role", value="**!no [role]**: will remove the role. For instance, `!no go` will remove you from the `@player` role", inline=False)
    embed.add_field(name="List all online users in with a specific role", value="**!list [role]**: will list all online users with the said role. For instance `!list tsumego` will list all online users of the `@tsumego` role.", inline=False)
    add_footer(embed, ctx.author)
    await ctx.send(embed=embed)


@bot.command(pass_context=True)
async def league(ctx, subject=None):
    if subject is None:
        desc = "Information about the various leagues hosted by OpenStudyRoom."
        embed = discord.Embed(title="OpenStudyRoom Leagues", description=desc, color=0xeee657)
        value = "The OpenStudyRoom hosts four different leagues, more information of which you can find by appending the following to `!league #`:\n\n"
        value += "- **ladder**: The main OSR league, also called the **OSR monthly league**.\n\n"
        value += "- **meijin**: Encompasing all other leagues and games.\n\n"
        value += "- **ddk**: A league dedicated to double digit kyu players.\n\n"
        value += "- **dan**: A league dedicated to dan players.\n\n"
        embed.add_field(name="Overview", value=value, inline=False)
        value = "Further information can be found with the following commands:\n\n"
        embed.add_field(name="Other commands", value=value, inline=False)
        embed.add_field(name="**rules**", value="Global league rules", inline=True)
        embed.add_field(name="**join**", value="Joining our leagues", inline=True)
        embed.add_field(name="**faq**", value="Frequently asked questions", inline=True)
        add_footer(embed, ctx.author)
        await ctx.send(embed=embed)
    elif subject == "rules":
        desc = "The following rules apply to all league games. Individual leagues may have their own rules."
        embed = discord.Embed(title="League rules", description=desc, color=0xeee657, url="https://openstudyroom.org/league/league-rules/")
        value = "The following rules apply in all our leagues:\n\n"
        value += "- Games must be played on the [KGS go server](https://www.gokgs.com/) or on the [Online Go Server](https://online-go.com/).\n"
        value += "- One player needs to **type `#OSR`** in the game chat for that game to count.\n"
        value += "- A game can count for both leagues, just type both tags in the game chat.\n"
        value += "- Games must be played with no handicap.\n"
        value += "- **Komi** must be **6.5**.\n"
        value += "- Game must use **Japanese time setting** with at least **30 minutes main time** and **5x30 seconds byo-yomi**.\n"
        value += "- Game must be **public**.\n"
        value += "- The game can be ranked or unranked, to the convenience of the players.\n"
        value += "- Using a bot such as Leela or Crazy Stone during league game is strictly forbidden. The OSR team checks games from time to time to look for suspicious matching with these go engines.\n\n\n"
        embed.add_field(name="Globar league rules", value=value, inline=False)
        value = "Players are strongly encouraged to review the game afterwards. If the players have similar rank, or if your opponent can't help you reviewing your game, one should feel free to ask stronger players in our Discord channel and/or in our KGS room to help with the review.\n\n"
        value += "Should you have any questions, or you've played a game that doesn't strictly cohere with all the rules, feel free to ask a member of our team for help.\n"
        embed.add_field(name="Additional information", value=value, inline=False)
        add_footer(embed, ctx.author)
        await ctx.send(embed=embed)
    elif subject == "ladder" or subject == "monthly":
        desc = "The following rules apply to the OSR Ladder.\n\n"
        desc += "- Players can play up to 3 games against the same opponent within the group.\n\n"
        desc += "- A win grants 1.5 points and a loss grants 0.5.\n\n"
        desc += "- Players who played at least 1 games will be added to the next league, once this one has ended.\n\n"
        embed = discord.Embed(title="OSR Ladder (Monthly league)",
                              description=desc,
                              color=0xeee657,
                              url="https://openstudyroom.org/league/ladder/")
        add_footer(embed, ctx.author)
        await ctx.send(embed=embed)
    elif subject == "meijin":
        desc = "The following rules apply to the Meijin league.\n\n"
        desc += "- Players can play up to 5 games against the same opponent within the group.\n\n"
        desc += "- A win grants 1.5 points and a loss grants 0.5.\n\n"
        desc += "- Players who played at least 3 games will be automatically added to the next league, once this one has ended.\n\n"
        embed = discord.Embed(title="Meijin League",
                              description=desc,
                              color=0xeee657,
                              url="https://openstudyroom.org/league/meijin/")
        add_footer(embed, ctx.author)
        await ctx.send(embed=embed)
    elif subject == "ddk":
        desc = "The following rules apply to the DDK league.\n\n"
        desc += "- Players can play up to 3 games against the same opponent within the group.\n\n"
        desc += "- A win grants 1.5 points and a loss grants 0.5.\n\n"
        desc += "- Players who played at least 1 games will be added to the next league, once this one has ended.\n\n"
        embed = discord.Embed(title="DDK League", description=desc, color=0xeee657, url="https://openstudyroom.org/league/ddk/")
        add_footer(embed, ctx.author)
        await ctx.send(embed=embed)
    elif subject == "dan":
        desc = "The following rules apply to the Dan league.\n\n"
        desc += "- Players can play up to 3 games against the same opponent within the group.\n\n"
        desc += "- A win grants 1.5 points and a loss grants 0.5.\n\n"
        desc += "- Players who played at least 1 games will be added to the next league, once this one has ended.\n\n"
        embed = discord.Embed(title="Dan League", description=desc, color=0xeee657, url="https://openstudyroom.org/league/dan/")
        add_footer(embed, ctx.author)
        await ctx.send(embed=embed)
    elif subject == "join":
        desc = "With the exception of the **Meijin League**, you need to manually join the league you wish.\n\n"
        desc += "In order to do this, go to our [website](https://openstudyroom.org/league/) and select the league of your choice.\n\n"
        desc += "In the main page of the league, you should see at the right of the top banner a button to join the specific league.\n\n"
        desc += "Press on that, and you have joined!\n\n"
        desc += "An example of this is presented in the image below for the **Dan League**.\n\n"
        embed = discord.Embed(title="Joining any of the OSR Leagues", description=desc, color=0xeee657)
        embed.set_image(url="https://cdn.discordapp.com/attachments/464175979406032897/464909106520522764/join_osr_league_annotated.png")
        add_footer(embed, ctx.author)
        await ctx.send(embed=embed)
    elif subject == "faq":
        desc = "You can always ask one of our team members, but here is a small FAQ."
        embed = discord.Embed(title="Frequently Asked Questions", description=desc, color=0xeee657)
        question = "We forgot to tag `#osr` the game, what can we do?"
        answer = "Contact one of the team members to see if we can manually add your game."
        embed.add_field(name=question, value=answer, inline=False)
        question = "Our game was classified as private, can we still use it for the league?"
        answer = "You need to upload the SGF file in our Discord and notify one of the members to manually add your game."
        embed.add_field(name=question, value=answer, inline=False)
        question = "At the end of the month, can I win a prize as a league player?"
        answer = ("Yes, it is possible to win a prize as a league player. Thanks to the support of our teachers, friends and partners, we are happy to reward our winners with the folowing:\n" +
                  " - Teaching game with [Péter Markó](https://openstudyroom.org/teachers/marko-peter/) (4 dan EGF).\n" +
                  " - Teaching game with with [Alexandre Dinerchtein](http://breakfast.go4go.net/) (3 dan pro).\n" +
                  " - Game commentary with [Justin Teng](https://openstudyroom.org/teachers/justin-teng/) (AGA 6 dan).\n" +
                  " - 5€ gift certificate at [Guo Juan's internet go school](https://internetgoschool.com/).\n\n")
        embed.add_field(name=question, value=answer, inline=False)
        question = "I am having some issues with another OSR member, what can I do?"
        answer = ("In the unfortunate event that you have an issue with" +
                  " another member from OSR, we ask you that you contact" +
                  " one of our team members privately so we can address the " +
                  " issue.\n\n")
        answer += ("Please note that we do not want to insult anyone and the" +
                   " any problem will be dealt with discretly.")
        embed.add_field(name=question, value=answer, inline=False)
        add_footer(embed, ctx.author)
        await ctx.send(embed=embed)
    else:
        desc = "I am not currently programmed for the command: **" + subject + "**"
        embed = discord.Embed(title="Unknown command", description=desc, color=0xeee657)
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/464175979406032897/464915353382813698/error.png")
        add_footer(embed, ctx.author)
        await ctx.send(embed=embed)


@bot.command(pass_context=True, aliases=["Quote"])
async def quote(ctx, msg_id, *resp):
    """Take message ID and response and create a quote."""
    str_resp = ' '.join(resp)
    """Take a message ID as input and convert it to an embed with quoted text."""
    message = await ctx.get_message(msg_id)

    await ctx.send(message.author.mention)
    embed = discord.Embed(description=str_resp, color=0x63b6f3)
    embed.set_author(name=ctx.author.name + " replied:", icon_url=ctx.author.avatar_url)
    embed.set_thumbnail(url='https://www.shareicon.net/data/64x64/2016/07/10/119195_chat_512x512.png')

    embed.add_field(name="In response to:",
                    value=message.author.mention + ": " + message.content,
                    inline=True)
    await ctx.send(embed=embed)


@bot.command(pass_context=True, aliases=["define"])
async def sensei(ctx, term=None):
    """Get information from Sensei's Library."""
    if term is None:
        message = "To search in Sensei's Library, please add a term as: !sensei term"
        embed = discord.Embed(title="Please add a search term",
                              description=message, color=0xeee657)
        embed.set_thumbnail(url="https://senseis.xmp.net/images/stone-hello.png")
        add_footer(embed, ctx.author)
        await ctx.send(embed=embed)
    else:
        s = requests.Session()
        url = "https://senseis.xmp.net/"
        s.headers.update({'referer': url})
        params = {'searchtype': 'title',
                  'search': term
                  }
        # Get all results searching by title
        r = s.get(url, params=params)

        # Separate direct hit
        regex = (r"\<b\>Direct hit\:\<br\>\<a href=\"\/\?(?P<term_url>.*?)\"" +
                 r"\>(?P<term>.*?)\<\/a\>\<\/b\>")
        match = re.search(regex, r.text, re.IGNORECASE)
        if match:
            url = "https://senseis.xmp.net/?" + match.group('term_url')
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            paragraphs = soup.find_all("p")
            title = "**" + soup.title.string + "**"
            message = paragraphs[1].text + "\n"
            message += "[See more online]({}) on Sensei's Library.".format(url)
        else:
            title = "**The term '{}' was not found**".format(term)
            message = ("The exact term {} was not found on".format(term) +
                       " Sensei's Library.")
        embed = discord.Embed(title=title, description=message, color=0xeee657)
        embed.set_thumbnail(url="https://senseis.xmp.net/images/stone-hello.png")

        # Search for non-direct hits containing the words
        regex = (r"\<b\>Title containing word( starting with search term)?" +
                 r"\:\<\/b\>\<br\>\n(?:<img .*?)?(?:<a href=\"" +
                 r"/\?(.*?)\">(.*?)</a>.*?\n){1,5}")
        match = re.search(regex, r.text, re.MULTILINE)

        # If there are alternatives, add them in the embed
        if match:
            groups = match.group(0).split("\n")[1:-1]
            value = ""
            for index in range(0, len(groups)):
                regex = r'<a href=\"/\?(?P<term_url>.*?)\"\>(?P<term>.*?)</a>'
                match = re.search(regex, groups[index])
                if match:
                    value += ("[{}](https://senseis.xmp.net/?" +
                              "{})\n").format(match.group("term"),
                                              match.group("term_url"))

            embed.add_field(name='Alternative search terms:',
                            value=value,
                            inline=False)
        else:
            embed.add_field(name="Alternative search terms",
                            value="No alternative terms found.", inline=False)
        add_footer(embed, ctx.author)
        await ctx.send(embed=embed)

async def check_KGS():
    await bot.wait_until_ready()
    global kgs_to_send
    # Display a message for which time was bot last updated.
    channel = bot.get_channel(channels["testing-bots"])
    msg = "{} was just deployed.".format(bot.user.mention)
    await channel.send(msg)
    await get_roles()
    async with aiohttp.ClientSession() as kgs_session:
        await kgs.login(kgs_session)
        while not bot.is_closed == True:
            await kgs.send_kgs_messages(kgs_session, kgs_to_send)
            kgs_to_send = []
            await kgs.get_messages(kgs_session, bot)
            await asyncio.sleep(1)


bot.loop.create_task(check_KGS())
bot.run(os.environ["OSR_TOKEN"])

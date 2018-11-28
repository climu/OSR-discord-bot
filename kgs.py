import json
import asyncio
import discord
import config

kgs_url = 'http://www.gokgs.com/json/access'
OSR_room = 3627409

# Announced games. Messages will come many time so we need to keep track to prevent
# annoucing those many times. We will only keep the last 20.
kgs_games = {
    'challenges': [],
    'ongoing': [],
    'ended': []
}
with open('/etc/kgs_password.txt') as f:
    kgs_password = f.read().strip()

async def login(session):
    message = {
        "type": "LOGIN",
        "name": "OSRbot",  # change this if you are testing locally
        "password": kgs_password,
        "locale": "de_DE",
    }
    formatted_message = json.dumps(message)
    await session.post(kgs_url, data=formatted_message)



async def logout(session):
    session.post(kgs_url, json.dumps({"type": "LOGOUT"}))

def formated_name(player):
    """Given  a KGS player dict, return a str : username(rank)
    https://www.gokgs.com/json/dataTypes.html#user"""
    text = "**" + player['name'] + "**"
    if 'rank' in player:
        text += " (" + player['rank'] + ")"
    return text

def result(score):
    """Returns a string indicating the result of a game.
    https://www.gokgs.com/json/dataTypes.html#score"""
    if type(score) == float:
        if score > 0:
            out = "Black + " + str(score)
        else:
            out = "White + " + str(-score)
    else:
        out = score
    return out


def add_players_field(embed, players):
    """Return the embed with a  new players field"""
    text = ""
    if "owner" in players:
        text += "Owner: " + formated_name(players['owner'])
    if "challengeCreator" in players:
        text += "Challenger: " + formated_name(players['challengeCreator'])
    if "white" in players:
        text += "\nWhite: " + formated_name(players['white'])
    if "black" in players:
        text += "\nBlack: " + formated_name(players['black'])
    embed.add_field(
        name="Players",
        value=text,
        inline=True
    )
    return embed

def add_settings_field(embed, game):
    """Return the embed with a nex settings field"""
    if "initialProposal" in game:
        rules = game['initialProposal']['rules']
    else:
        rules = game
    text = "Size: " + str(rules['size'])
    text += "\nKomi: " + str(rules['komi'])
    if 'handicap' in rules:
        text += "\nHandicap: " + str(rules['handicap'])
    embed.add_field(
        name="Settings",
        value=text,
        inline=True
    )
    return embed

async def format_and_send_game_embed(bot, game, title, text):
    embed = discord.Embed(title=title, description=text, color=0xeee657)
    embed = add_settings_field(embed, game)
    embed = add_players_field(embed, game['players'])
    embed.set_thumbnail(url="http://files.gokgs.com/images/kgsLogo.png")
    kgs_channel = bot.get_channel(config.channels["kgs"])
    await kgs_channel.send(embed=embed)


async def announce_challenge(bot, game):
    """send an embed to announce a KGS challenge"""
    title = 'Ready to rumble?'
    text =  "New challenge in OSR room from " + formated_name(game['players']['challengeCreator'])
    if 'name' in game:
        text += ": " + game['name']

    await format_and_send_game_embed(bot, game, title, text)


async def announce_ended_game(bot, game):
    """send an embed to announce a KGS game has ended"""
    title = 'Game has ended'
    text =  formated_name(game['players']['white']) + " Vs " + formated_name(game['players']['black'])
    text += " just ended: " + result(game['score'])

    await format_and_send_game_embed(bot, game, title, text)


async def announce_new_game(bot, game):
    """send an embed to announce a KGS game has started"""
    if game['gameType'] in ['free', 'ranked', 'tournament', 'rengo', 'simul']:
        title = 'A ' + game['gameType'] + ' game has started in OSR room!'
        text = "Let's kibitz " + formated_name(game['players']['white'])
        text += " Vs " + formated_name(game['players']['black'])

    elif game['gameType'] in ['review', 'demonstration', 'teaching']:
        title = "Let's learn together!"
        text = "A **" + game['gameType']
        if game['gameType'] == 'teaching':
            text += " game"
        text += "** has started in OSR room."

    await format_and_send_game_embed(bot, game, title, text)


async def handle_messages(session, bot, json):
    if not 'messages' in json:
        return
    for m in json['messages']:
        if m['type'] == 'LOGOUT':
            await login(session)

        if m['type'] == 'CHAT' and m['channelId'] == OSR_room:
            if m['user']['name'] != "OSRbot":
                text = formated_name(m['user']) + ': ' + m['text']
                await send_discord_message(text, bot)

        if m['type'] == 'GAME_LIST' and m['channelId'] == OSR_room:
            for game in m['games']:
                # we need to keep track of announced games not to repeat itself.
                # https://gist.github.com/climu/b276c0457cc5ab9e5558da6209f1e6f6 for exemple message
                if game['gameType'] == 'challenge':
                    if game['channelId'] not in kgs_games['challenges']:
                        await announce_challenge(bot, game)
                        kgs_games['challenges'].append(game['channelId'])
                else:
                    # Not a challenge
                    # have the game ended?
                    if 'score' in game:
                        if game['channelId'] not in kgs_games['ended']:
                            await announce_ended_game(bot, game)
                            kgs_games['ended'].append(game['channelId'])

                    elif game['channelId'] not in kgs_games['ongoing']:
                        #game is not ended
                        await announce_new_game(bot, game)
                        kgs_games['ongoing'].append(game['channelId'])
    # clean the lists of games. We keep the 20 lasts.
    kgs_games['challenges'] = kgs_games['challenges'][-20:]
    kgs_games['ongoing'] = kgs_games['ongoing'][-20:]
    kgs_games['ended'] = kgs_games['ended'][-20:]


async def get_messages(session, bot):
    async with session.get(kgs_url) as r:
        await handle_messages(session, bot, await r.json())

async def send_discord_message(message, bot):
    kgs_channel = bot.get_channel(config.channels["kgs"])
    await kgs_channel.send(message)

async def send_kgs_messages(s, messages):
    for text in messages:
        message = {
            "type": "CHAT",
            "text": text,
            "channelId": OSR_room
        }
        formatted_message = json.dumps(message)
        await s.post(kgs_url, data=formatted_message)

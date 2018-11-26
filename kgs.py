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
    """Given  a KGS player dict, return a str : username[rank]
    https://www.gokgs.com/json/dataTypes.html#user"""
    text = player['name']
    if 'rank' in player:
        text += "[" + player['rank'] + "]"
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

async def handle_messages(session, bot, json):
    if not 'messages' in json:
        return
    for m in json['messages']:
        if m['type'] == 'LOGOUT':
            await login(session)

        if m['type'] == 'CHAT' and m['channelId'] == OSR_room:
            if m['user']['name'] != "OSRbot":
                text = formated_name(m['user']) + m['text']
                await send_discord_message(text, bot)

        if m['type'] == 'GAME_LIST' and m['channelId'] == OSR_room:
            for game in m['games']:
                # we need to keep track of announced games not to repeat itself.
                # https://gist.github.com/climu/b276c0457cc5ab9e5558da6209f1e6f6 for exemple message
                if game['gameType'] == 'challenge':
                    if game['channelId'] not in kgs_games['challenges']:
                        text = "Game offer from " + formated_name(game['players']['challengeCreator'])
                        if 'name' in game:
                            text += ": " + game['name']
                        await send_discord_message(text, bot)
                        kgs_games['challenges'].append(game['channelId'])
                else:
                    # Not a challenge
                    # have the game ended?
                    if 'score' in game:
                        if game['channelId'] not in kgs_games['ended']:
                            text = "Game " + formated_name(game['players']['white']) + "(W) Vs " +\
                                formated_name(game['players']['black']) + " (B): "
                            text += result(game['score'])
                            await send_discord_message(text, bot)
                            kgs_games['ended'].append(game['channelId'])

                    elif game['channelId'] not in kgs_games['ongoing']:
                        #game is not ended
                        text = "Game " + formated_name(game['players']['white']) + "(W) Vs " +\
                            formated_name(game['players']['black']) + " (B) "+ " has started!"
                        await send_discord_message(text, bot)
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
            "text": text,  # change this if you are testing locally
            "channelId": OSR_room
        }
        formatted_message = json.dumps(message)
        await s.post(kgs_url, data=formatted_message)

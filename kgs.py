import requests
import json
import asyncio
import discord
import config

kgs_url = 'http://www.gokgs.com/json/access'
OSR_room = 3627409
s = requests.Session()

with open('/etc/kgs_password.txt') as f:
    kgs_password = f.read().strip()

async def login():
    message = {
        "type": "LOGIN",
        "name": "OSRbot",  # change this if you are testing locally
        "password": kgs_password,
        "locale": "de_DE",
    }
    formatted_message = json.dumps(message)
    r = s.post(kgs_url, formatted_message)


async def logout():
    s.post(kgs_url, json.dumps({"type": "LOGOUT"}))

async def get_messages(bot):
    r = s.get(kgs_url)
    if not 'messages' in json.loads(r.text):
        return
    for m in json.loads(r.text)['messages']:
        if m['type'] == 'LOGOUT':
            await login()

        #if m['type'] == 'GAME_LIST' and m['channelId'] == OSR_room:
            #for game in m['games']:
                # we need to keep track of announced games not to repeat itself.
                # we will pass for now but I keep the code for future use
                # https://gist.github.com/climu/b276c0457cc5ab9e5558da6209f1e6f6 for exemple message
                #if game['channelId'] in config.announced_games:
                #    pass
                #if game['gameType'] == 'challenge':
                #    text = "Game offer from " + game['players']['challengeCreator']['name']
                #    text += ": " + game['name']
                #    await send_message(text, bot)
                #    config.announced_games.append(game['channelId'])

        if m['type'] == 'CHAT' and m['channelId'] == OSR_room:
            if m['user']['name'] != "OSRbot":
                text = m['user']['name'] + "[" + m['user']['rank'] + "]: " + m['text']
                await send_discord_message(text, bot)


async def send_discord_message(message, bot):
    kgs_channel = bot.get_channel(config.channels["kgs"])
    await kgs_channel.send(message)

async def send_kgs_message(text):
    message = {
        "type": "CHAT",
        "text": text,  # change this if you are testing locally
        "channelId": OSR_room
    }
    formatted_message = json.dumps(message)
    r = s.post(kgs_url, formatted_message)

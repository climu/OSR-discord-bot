guild_id = 287487891003932672
prefix = "!"

roles_dict = {
    'go': {
        "id": 433023079183286282,
        "allowed_channels": ["game-request", "bot-commands", "testing-bots"],
        "verbose": "looking for a game"
    },
    'tsumego': {
        "id": 462186851747233793,
        "allowed_channels": ["general", "tsumego", "tsumego_hint", "tsumego_solutions", "bot-commands", "testing-bots"],
        "verbose": "interested in tsumegos"
    },
    'review': {
        "id": 462187005602955266,
        "allowed_channels": ["general", "game_discussion", "bot-commands", "testing-bots"],
        "verbose": "interested in game reviews",
    },
    'dan': {
        "id": 462186943221071872,
        "allowed_channels": ["general", "game_discussion", "bot-commands", "testing-bots"],
        "verbose": "dan player",
    },
    'sdk': {
        "id": 462186975240388620,
        "allowed_channels": ["general", "game_discussion", "bot-commands", "testing-bots"],
        "verbose": "single digit kyu player",
    },
    'ddk': {
        "id": 462187620156309514,
        "allowed_channels": ["general", "game_discussion", "bot-commands", "testing-bots"],
        "verbose": "double digit kyu player",
    },
}

pics = {
    "cho": "https://cdn.discordapp.com/attachments/456532168370290695/461802038276390923/cho.png",
    "cho_hug": "https://cdn.discordapp.com/attachments/430062036903395329/444192620504416268/WroCzKKKj7o.png",
    "chang_ho": "https://cdn.discordapp.com/attachments/430062036903395329/432619582054858806/153746110828-nong01.png",
    "yuta": "https://cdn.discordapp.com/attachments/430062036903395329/432619582054858806/153746110828-nong01.png",
    "kj_facepalm": "https://cdn.discordapp.com/attachments/366870031285616651/461813881900236821/iozlnkjg.png",
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
    "no_game",
    "go",
    "nogo",
    "GO",
    "NOGO",
    "tsumego",
    "review",
    "ddk",
    "sdk",
    "dan",
    "no go",
    "no",
    "whos go",
    "whos_go",
    "cho",
    "cho_hug",
    "chang_ho",
    "yuta",
    "kj_facepalm"
]

# LFG related commands can only be called in the channels below
lfgChannels = [
    "game_request",
    "bot_commands"
]

minutes_in_a_day = 1440
expiration_times = {}

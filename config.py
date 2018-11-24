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
    'rengo': {
        "id": 498902129956618250,
        "allowed_channels": ["general", "game_discussion", "bot-commands", "testing-bots", "go-variants", "rengo"],
        "verbose": "interested in rengo games",
    },
    'goquest': {
        "id": 503493877907587072,
        "allowed_channels": ["general", "game_discussion", "bot-commands", "testing-bots", "go-variants", "go_server_war"],
        "verbose": "interested in GoQuest games",
    },
}

channels = {
    "welcome": 287537238445654016,
    "testing-bots": 463639475751354368,
    "general": 287487891003932672,
    "bot-commands": 287868862559420429,
    "kgs": 515865606923485184
}

member_role_id = 287489624014585866

pics = {
    "cho": "https://cdn.discordapp.com/attachments/456532168370290695/461802038276390923/cho.png",
    "cho_hug": "https://cdn.discordapp.com/attachments/430062036903395329/444192620504416268/WroCzKKKj7o.png",
    "chang_ho": "https://cdn.discordapp.com/attachments/430062036903395329/432619582054858806/153746110828-nong01.png",
    "yuta": "https://cdn.discordapp.com/attachments/287487891003932672/461811731359072259/vfcp43js2.png",
    "kj_facepalm": "https://cdn.discordapp.com/attachments/366870031285616651/461813881900236821/iozlnkjg.png",
}

# For the following commands, the calling message will be deleted
del_commands = [
    "go",
    "GO",
    "tsumego",
    "review",
    "ddk",
    "sdk",
    "dan",
    "no",
    "who",
    "whos",
    "list",
    "cho",
    "cho_hug",
    "chang_ho",
    "yuta",
    "kj_facepalm",
    "info",
    "help",
    "league",
    "roles",
    "sensei",
    "define",
    "scary",
    "quote",
    "rengo",
    "goquest"
]

def init_globals():
    """ init global variables https://stackoverflow.com/a/13034908"""
    global announced_games
    announced_games = []

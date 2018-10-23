from config import roles_dict, member_role_id
import discord
from config import guild_id


async def add_role(ctx, role_name):
    role_dict = roles_dict[role_name]
    if str(ctx.message.channel) not in role_dict['allowed_channels']:
        message = "Please " + ctx.message.author.mention + ", use the appropriate channels for this command: "
        message += ' '.join(role_dict['allowed_channels'])
        await ctx.send(message)
        return

    role = role_dict["role"]
    if role in ctx.message.author.roles:
        await ctx.send("Hey, " + ctx.message.author.mention + " is still " +
                       role_dict["verbose"] + ".")
    else:
        await ctx.message.author.add_roles(role)
        await ctx.send("Hey, " + ctx.message.author.mention + " is " + role_dict["verbose"] + ".")


def user_info_message(user, infos):
    message = '**' + user.name + '**'
    info = infos.get(str(user.id))
    if info is not None:
        osr_username = info.get('osr_username')
        leagues = info.get('leagues')
        kgs_username = info.get('kgs_username')
        kgs_rank = info.get('kgs_rank')
        ogs_username = info.get('ogs_username')
        ogs_rank = info.get('ogs_rank')
        ogs_id = info.get('ogs_id')
        servers = []
        servers.append(' OSR | [{}](https://openstudyroom.org/league/account/{}/)'.format(osr_username,
                                                                                          osr_username))

        if kgs_username is not None or ogs_username is not None:
            message += ':'
            if ogs_username is not None:
                servers.append(' OGS | [{}](https://online-go.com/player/{}) ({})'.format(ogs_username,
                                                                                          ogs_id,
                                                                                          ogs_rank))
            if kgs_username is not None:
                servers.append(' KGS | [{u}](http://www.gokgs.com/graphPage.jsp?user={u}) ({r})'.format(u=kgs_username,
                                                                                                        r=kgs_rank))
        message += ' - '.join(servers)

        if leagues is not None:
            message += '\n\n_Registered leagues_: '
            for league in leagues:
                message += '[{n}](https://openstudyroom.org/league/{id})'.format(n=league['name'],
                                                                                 id=league['id'])

    message += '\n'
    return message


def user_rank(user, infos):
    message = ''
    info = infos.get(str(user.id))
    if info is not None:
        kgs_rank = info.get('kgs_rank')
        ogs_rank = info.get('ogs_rank')
        kgs_username = info.get('kgs_username')
        ogs_id = info.get('ogs_id')
        servers = []
        if kgs_rank is not None or ogs_rank is not None:
            if ogs_rank is not None:
                servers.append('[OGS](https://online-go.com/player/{}): {}'.format(ogs_id, ogs_rank))
            if kgs_rank is not None:
                servers.append('[KGS](http://www.gokgs.com/graphPage.jsp?user={}): {}'.format(kgs_username, kgs_rank))
            message += ' - '.join(servers)
            message = '({0})'.format(message)
    return message


def get_user(username, bot):
    role = discord.utils.get(bot.get_guild(guild_id).roles, id=member_role_id)
    if username[0] == "#":
        user = discord.utils.get(role.members, discriminator=str(username[1:]))
    else:
        user = discord.utils.get(role.members, display_name=username)
    if user is None:
        user = discord.utils.get(role.members, name=username)
    return user


def add_footer(embed, user):
    embed.set_footer(text="Requested by: {}#{}".format(user.name,
                                                       user.discriminator),
                     icon_url=user.avatar_url)

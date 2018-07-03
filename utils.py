from config import roles_dict

async def add_role(ctx, role_name):
    role_dict = roles_dict[role_name]
    if str(ctx.message.channel) not in role_dict['allowed_channels']:
        message = "Please " + ctx.message.author.mention + ", use the appropriate channels for this command:"
        message += ' '.join(role_dict['allowed_channels'])
        await ctx.send(message)
        return

    role = role_dict["role"]
    if role in ctx.message.author.roles:
        await ctx.send(ctx.message.author.mention + "Hey, is still " + role_dict["verbose"] + ".")
    else:
        await ctx.message.author.add_roles(role)
        await ctx.send("Hey, " + ctx.message.author.mention + " is " + role_dict["verbose"] + ".")

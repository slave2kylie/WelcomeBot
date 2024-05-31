from typing import Optional, Union

import discord
import os
from discord import app_commands
from dotenv import load_dotenv
from discord.ext import commands
import db
import WelcomeMessage
import DmWelcomeMessage

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.messages = True
client = commands.Bot(intents=intents,command_prefix='/')
dbi = db.DB()

def is_owner(interaction: discord.Interaction):
    if interaction.user.id == interaction.guild.owner_id:
        return True
    else:
        return False

def check_command_permission(interaction: discord.Interaction):
    cmdrole = dbi.get(str(interaction.guild_id),db.KEYS.CMD_ROLE)
    for role in interaction.user.roles:
        if(role.name == cmdrole):
            return True
    return False

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')
    #print(cmdrole)
    #client.tree = app_commands.CommandTree(client)
    for guild in client.guilds:
        print("id: ",guild.id,"name: ",guild.name)
        client.tree.copy_global_to(guild=guild)
        await client.tree.sync(guild=guild)
    return

@client.event
async def on_guild_join(guild):
    print("on_guild_join")
    client.tree.copy_global_to(guild=guild)
    await client.tree.sync(guild=guild)
    return

@client.tree.command(name='setup')
@app_commands.check(is_owner)
async def setup(interaction: discord.Interaction,embed_color: str,role: discord.Role):
    """Setup bot for this server"""
    print("inside setup")
    embed_color="0x"+embed_color
    embed_color_int=int(embed_color,16)
    role_name=role.name
    guild_id=str(interaction.guild_id)
    dbi.set(guild_id,db.KEYS.EMBED_COLOR,embed_color_int)
    dbi.set(guild_id,db.KEYS.CMD_ROLE,role_name)
    print(dbi.get(guild_id,db.KEYS.CMD_ROLE))
    print(dbi.get(guild_id,db.KEYS.EMBED_COLOR))
    await interaction.response.send_message('welcome setup is done')
    return

@setup.error
async def setup_error(interaction: discord.Interaction,error):
    print("setup_error",error)
    await interaction.response.send_message("Only the server owner can access this command")
    return

@client.tree.command(name='welcome-message')
@app_commands.check(check_command_permission)
async def welcome_message(interaction: discord.Interaction,msg: str,channel: Optional[discord.TextChannel]=None):
    """Set a welcome message"""
    WelcomeMessage.welcome_message(dbi,interaction,msg,channel)
    await interaction.response.send_message('welcome text message is set')
    return

@welcome_message.error
async def welcome_message_error(interaction: discord.Interaction,error):
    print("welcome_message_error",error)
    #cmdrole=dbi.get(str(interaction.guild_id),db.KEYS.CMD_ROLE)
    await interaction.response.send_message("You do not have permission for this command, peasant.")
    return

@client.tree.command(name='welcome-embed')
@app_commands.check(check_command_permission)
async def welcome_embed(interaction: discord.Interaction,msg: str,channel: Optional[discord.TextChannel]=None,image: Optional[discord.Attachment] = None,footer_text: Optional[str] = None,title_message: Optional[str]=None):
    """Set a welcome embed message"""
    WelcomeMessage.welcome_embed(dbi,interaction,msg,channel,image,footer_text,title_message)
    await interaction.response.send_message('welcome-embed is set')
    return

@welcome_embed.error
async def welcome_embed_error(interaction: discord.Interaction,error):
    print("welcome_embed_error",error)
#    cmdrole=dbi.get(str(interaction.guild_id),db.KEYS.CMD_ROLE)
    await interaction.response.send_message("You do not have permission for this command, peasant.")
    return

@client.tree.command(name='dm-welcome-message')
@app_commands.check(check_command_permission)
async def dm_welcome_message(interaction: discord.Interaction,msg: str):
    """Set a welcome message"""
    DmWelcomeMessage.dm_welcome_message(dbi,interaction,msg)
    await interaction.response.send_message('dm welcome text message is set')
    return

@dm_welcome_message.error
async def dm_welcome_message_error(interaction: discord.Interaction,error):
    print("welcome_message_error",error)
#    cmdrole=dbi.get(str(interaction.guild_id),db.KEYS.CMD_ROLE)
    await interaction.response.send_message("You do not have permission for this command, peasant.")
    return

@client.tree.command(name='dm-welcome-embed')
@app_commands.check(check_command_permission)
async def dm_welcome_embed(interaction: discord.Interaction,msg: str,image: Optional[discord.Attachment] = None,footer_text: Optional[str] = None,title_message: Optional[str]=None):
    """Set a welcome embed message"""
    DmWelcomeMessage.dm_welcome_embed(dbi,interaction,msg,image,footer_text,title_message)
    await interaction.response.send_message('dm welcome-embed is set')
    return

@dm_welcome_embed.error
async def dm_welcome_embed_error(interaction: discord.Interaction,error):
    print("welcome_embed_error",error)
#    cmdrole=dbi.get(str(interaction.guild_id),db.KEYS.CMD_ROLE)
    await interaction.response.send_message("You do not have permission for this command, peasant.")
    return


@client.tree.command(name='welcome-stop')
@app_commands.check(check_command_permission)
async def stop_welcome(interaction: discord.Interaction):
    print("inside stop_welcome")
    guild_id=str(interaction.guild_id)
    dbi.set(guild_id,db.KEYS.CAN_SEND_MSG,False)
    dbi.set(guild_id,db.KEYS.CAN_SEND_DM_MSG,False)
    await interaction.response.send_message('Welcome messages stopped')
    return

@stop_welcome.error
async def stop_welcome_error(interaction: discord.Interaction, error):
    print("inside stop_welcome_error",error)
    await interaction.response.send_message("You do not have permission for this command, peasant.")
    return

"""@client.tree.command(name='dm-welcome-stop')
@app_commands.check(check_command_permission)
async def dm_stop_welcome(interaction: discord.Interaction):
    print("inside dm_stop_welcome")
    guild_id=str(interaction.guild_id)
    dbi.set(guild_id,db.KEYS.CAN_SEND_DM_MSG,False)
    await interaction.response.send_message('Welcome dms stopped')
    return

@dm_stop_welcome.error
async def stop_dm_welcome_error(interaction: discord.Interaction, error):
    print("inside dm_stop_welcome_error",error)
    await interaction.response.send_message("You do not have permission for this command, peasant.")
    return
"""

def process_str(st,member_id):
    if st==None:
        return ""
    msg=str(st)
    msg=msg.replace("{","{0.")
    msg=msg.replace("@","<@"+str(member_id)+">")
    return msg

@client.event
async def on_member_join(member):
    print('inside on_member_join')
    guild_id = str(member.guild.id)
    text_msg=dbi.get(guild_id,db.KEYS.TEXT_MSG)
    dm_text_msg=dbi.get(guild_id,db.KEYS.DM_TEXT_MSG)
    msg=process_str(text_msg,member.id)
    dm_msg=process_str(dm_text_msg,member.id)
    print("msg:",msg)
    print("text_msg:",text_msg)
    print("dm_msg:",dm_msg)
    
    send_welcome_message=dbi.get(guild_id,db.KEYS.CAN_SEND_MSG)
    send_welcome_dm_message=dbi.get(guild_id,db.KEYS.CAN_SEND_DM_MSG)

    print("send_welcome_message:",send_welcome_message)
    print("send_welcome_dm_message:",send_welcome_dm_message)


    if send_welcome_message==True:
        embed_set=dbi.get(guild_id,db.KEYS.EMBED_SET)
        if embed_set == True:
            embed=dbi.get(guild_id,db.KEYS.EMBED)
            embed.clear_fields()
            embed.add_field(name='', value=msg.format(member))
            embed_channel=dbi.get(guild_id,db.KEYS.EMBED_CHANNEL)
            await embed_channel.send(embed=embed)
        else:
            text_channel=dbi.get(guild_id,db.KEYS.TEXT_CHANNEL)
            if text_channel != None:
                await text_channel.send(msg.format(member))
    
    if send_welcome_dm_message==True:
        dm_embed_set=dbi.get(guild_id,db.KEYS.DM_EMBED_SET)
        if dm_embed_set == True:
            dm_embed=dbi.get(guild_id,db.KEYS.DM_EMBED)
            dm_embed.clear_fields()
            dm_embed.add_field(name='',value=dm_msg.format(member))
            await member.send(embed=dm_embed)
        else:
            if dm_msg != "":
                await member.send(dm_msg.format(member))


    return




client.run(TOKEN)

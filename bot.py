from typing import Optional, Union, List

import discord
import os
from discord import app_commands
from dotenv import load_dotenv
from discord.ext import commands
import db
import WelcomeMessage
import DmWelcomeMessage
import asyncio
import aiohttp
import AutoFeed
import AIImage

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.messages = True
client = commands.Bot(intents=intents,command_prefix='/')
dbi = db.DB()

async def msg_autocomplete(interaction: discord.Interaction,current: str) -> List[app_commands.Choice[str]]:
    lmsgs=[]
    guild_id=str(interaction.guild_id)
    if AutoFeed.msgs.get(guild_id)!={None:None}:
        for key in AutoFeed.msgs[guild_id]:
            if key != None:
                r=key.split('+++')
                lmsgs.append(r[0])
    print(lmsgs)
    return [
        app_commands.Choice(name=msg, value=msg)
        for msg in lmsgs if current.lower() in msg.lower()
    ]

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


@client.tree.command(name='autofeed')
@app_commands.check(check_command_permission)
async def auto_feed(interaction: discord.Interaction,message: str,time: str,channel: Optional[discord.TextChannel]=None,image: Optional[discord.Attachment] = None,footer_text: Optional[str] = None,title_message: Optional[str]=None):
    """Set an autofeed"""
    msg=message
    c=time[-1]
    a=1
    if c=='d':
        a=a*60*60*24
    elif c=='h':
        a=a*60*60
    elif c=='m':
        a=a*60
    elif c=='s':
        a=a
    else:
        await interaction.response.send_message('please specify s,m,h or d',ephemeral=True)
        return
    a=a*int(time[:-1])
    await AutoFeed.send_auto_feed(client,interaction,dbi,msg,a,channel,image,footer_text,title_message)
    return

@auto_feed.error
async def auto_feed_error(interaction: discord.Interaction,error):
    print("auto_feed_error",error)
    await interaction.response.send_message("You do not have permission for this command, peasant.",ephemeral=True)
    return

@client.tree.command(name='imagine')
async def Imagine(interaction: discord.Interaction,prompt: str):
    guild_id=str(interaction.guild_id)
    await AIImage.Imagine(client,interaction,dbi.get(guild_id,db.KEYS.EMBED_COLOR),prompt)
    return

@client.tree.command(name='autofeed-stop')
@app_commands.autocomplete(message=msg_autocomplete)
@app_commands.check(check_command_permission)
async def auto_feed_stop(interaction: discord.Interaction,message:str,channel: Optional[discord.TextChannel]=None):
    """Stop an autofeed"""
    msg=message
    await AutoFeed.send_auto_feed_stop(interaction,msg,channel)
    return

@auto_feed_stop.error
async def auto_feed_stop_error(interaction: discord.Interaction,error):
    print("auto_feed_stop_error",error)
    await interaction.response.send_message("You do not have permission for this command, peasant.",ephemeral=True)
    return

@client.tree.command(name='setup')
@app_commands.check(is_owner)
async def setup(interaction: discord.Interaction,embed_color: str,role: discord.Role):
    """Set up bot for this server"""
    print("inside setup")
    embed_color="0x"+embed_color
    embed_color_int=int(embed_color,16)
    role_name=role.name
    guild_id=str(interaction.guild_id)
    dbi.set(guild_id,db.KEYS.EMBED_COLOR,embed_color_int)
    dbi.set(guild_id,db.KEYS.CMD_ROLE,role_name)
    print(dbi.get(guild_id,db.KEYS.CMD_ROLE))
    print(dbi.get(guild_id,db.KEYS.EMBED_COLOR))
    await interaction.response.send_message('Set up complete',ephemeral=True)
    return

@setup.error
async def setup_error(interaction: discord.Interaction,error):
    print("setup_error",error)
    await interaction.response.send_message("Only the server owner can access this command",ephemeral=True)
    return

@client.tree.command(name='welcome-message')
@app_commands.check(check_command_permission)
async def welcome_message(interaction: discord.Interaction,message: str,channel: Optional[discord.TextChannel]=None):
    """Set a welcome message"""
    msg=message
    WelcomeMessage.welcome_message(dbi,interaction,msg,channel)
    await interaction.response.send_message('Welcome message is set',ephemeral=True)
    return

@welcome_message.error
async def welcome_message_error(interaction: discord.Interaction,error):
    print("welcome_message_error",error)
    await interaction.response.send_message("You do not have permission for this command, peasant.",ephemeral=True)
    return

@client.tree.command(name='welcome-embed')
@app_commands.check(check_command_permission)
async def welcome_embed(interaction: discord.Interaction,message: str,channel: Optional[discord.TextChannel]=None,image: Optional[discord.Attachment] = None,footer_text: Optional[str] = None,title_message: Optional[str]=None):
    """Set a welcome message embed"""
    msg=message
    WelcomeMessage.welcome_embed(dbi,interaction,msg,channel,image,footer_text,title_message)
    await interaction.response.send_message('welcome embed set',ephemeral=True)
    return

@welcome_embed.error
async def welcome_embed_error(interaction: discord.Interaction,error):
    print("welcome_embed_error",error)
    await interaction.response.send_message("You do not have permission for this command, peasant.",ephemeral=True)
    return

@client.tree.command(name='dm-welcome-message')
@app_commands.check(check_command_permission)
async def dm_welcome_message(interaction: discord.Interaction,message: str):
    """Set a dm welcome message"""
    msg=message
    DmWelcomeMessage.dm_welcome_message(dbi,interaction,msg)
    await interaction.response.send_message('Dm welcome message has been set',ephemeral=True)
    return

@dm_welcome_message.error
async def dm_welcome_message_error(interaction: discord.Interaction,error):
    print("welcome_message_error",error)
    await interaction.response.send_message("You do not have permission for this command, peasant.",ephemeral=True)
    return

@client.tree.command(name='dm-welcome-embed')
@app_commands.check(check_command_permission)
async def dm_welcome_embed(interaction: discord.Interaction,message: str,image: Optional[discord.Attachment] = None,footer_text: Optional[str] = None,title_message: Optional[str]=None):
    """Set a dm welcome embed message"""
    msg=message
    DmWelcomeMessage.dm_welcome_embed(dbi,interaction,msg,image,footer_text,title_message)
    await interaction.response.send_message('Dm welcome embed has been set',ephemeral=True)
    return

@dm_welcome_embed.error
async def dm_welcome_embed_error(interaction: discord.Interaction,error):
    print("welcome_embed_error",error)
    await interaction.response.send_message("You do not have permission for this command, peasant.",ephemeral=True)
    return

@client.tree.command(name='bot-avatar')
@app_commands.check(is_owner)
async def bot_avatar(interaction: discord.Interaction,image: discord.Attachment):
    """Set a new avatar picture for bot"""   
    print('before  image change')
    await image.save(fp='img.png',seek_begin=True,use_cached=False)
    with open('img.png','rb') as img:
        await client.user.edit(avatar=img.read())
    print('after image change')
    await interaction.response.send_message("Changed the bot avatar",ephemeral=True)
    return

@bot_avatar.error
async def bot_avatar_error(interaction: discord.Interaction,error):
    print('bot_avatar_error',error)
    await interaction.response.send_message("Only the server owner can access this command",ephemeral=True)
    return

@client.tree.command(name='welcome-stop')
@app_commands.check(check_command_permission)
async def stop_welcome(interaction: discord.Interaction):
    """Stop all welcome messages"""
    print("inside stop_welcome")
    guild_id=str(interaction.guild_id)
    dbi.set(guild_id,db.KEYS.CAN_SEND_MSG,False)
    dbi.set(guild_id,db.KEYS.CAN_SEND_DM_MSG,False)
    await interaction.response.send_message('Welcome messages stopped',ephemeral=True)
    return

@stop_welcome.error
async def stop_welcome_error(interaction: discord.Interaction, error):
    print("inside stop_welcome_error",error)
    await interaction.response.send_message("You do not have permission for this command, peasant.",ephemeral=True)
    return

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
            embed.description=msg.format(member)
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
            dm_embed.description=dm_msg.format(member)
            await member.send(embed=dm_embed)
        else:
            if dm_msg != "":
                await member.send(dm_msg.format(member))


    return

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




client.run(TOKEN)

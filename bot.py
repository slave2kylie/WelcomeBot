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
import random

import AutoFeed
import AIImage
import Warnings

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

async def genre_autocomplete(interaction: discord.Interaction,current: str) -> List[app_commands.Choice[str]]:
    keys=db.books_keys
    if interaction.command.name=="random-movie": keys=db.movies_keys
    if interaction.command.name=="random-show": keys=db.shows_keys
    return [
        app_commands.Choice(name=msg, value=msg)
        for msg in keys if current.lower() in msg.lower()
    ]

async def criminal_autocomplete(interaction: discord.Interaction,current: str) -> List[app_commands.Choice[str]]:
    keys=[]
    user_id=str(interaction.namespace.user.id)
    guild_id=str(interaction.guild_id)
    if Warnings.warnings.get(guild_id)!=None and Warnings.warnings[guild_id].get(user_id)!=None:
        keys=Warnings.warnings[guild_id][user_id]
    return [
        app_commands.Choice(name=msg, value=msg)
        for msg in keys if current.lower() in msg.lower()
    ]

def is_owner(interaction: discord.Interaction):
    if interaction.user.id == interaction.guild.owner_id:
        return True
    else:
        return False

def check_command_permission(interaction: discord.Interaction):
    cmdrole = dbi.get(str(interaction.guild_id),db.KEYS.CMD_ROLE)
    print(f'cmdrolecheck {cmdrole}')
    for role in interaction.user.roles:
        if(role.name == cmdrole):
            return True
    return False

def convert_to_seconds(time):
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
        return -1
    a=a*int(time[:-1])
    return a


@client.tree.command()
async def remind(interaction:discord.Interaction,time:str,reason:str):
    """Set a reminder"""
    await interaction.response.defer(ephemeral=True)
    print("inside remind")
    t=convert_to_seconds(time)
    if t==-1:
        await interaction.followup.send('please specify s,m,h or d',ephemeral=True)
        return
    await AutoFeed.set_reminder(client, interaction, t, reason, dbi)
    return

@client.tree.command(name='auto-delete')
#@app_commands.check(check_command_permission)
async def auto_delete(interaction: discord.Interaction,time:str,channel: Optional[discord.TextChannel]=None):
    """Set a channel to auto delete after a set time"""
    await interaction.response.defer(ephemeral=True)
    print("inside auto_delete")
    if channel==None:channel=interaction.channel
    key=str(channel.id)
    t=convert_to_seconds(time)
    if t==-1:
        await interaction.followup.send('please specify s,m,h or d',ephemeral=True)
        return
    AutoFeed.delete_tasks[key]=t
    await interaction.followup.send('Auto delete set',ephemeral=True)
    return


@client.tree.command(name='stop-auto-delete')
#@app_commands.check(check_command_permission)
async def auto_delete_stop(interaction: discord.Interaction,channel: Optional[discord.TextChannel]=None):
    """Stop auto deleting in a channel"""
    await interaction.response.defer(ephemeral=True)
    print("inside auto_delete_stop")
    if channel==None:channel=interaction.channel
    key=str(channel.id)
    if AutoFeed.delete_tasks.get(key)==None:
        await interaction.followup.send(f"No Auto delete set for {channel}",ephemeral=True)
        return
    AutoFeed.delete_tasks.pop(key)
    await interaction.followup.send('Auto delete stopped',ephemeral=True)
    return

@client.tree.command()
@app_commands.check(check_command_permission)
async def kick(interaction: discord.Interaction,user: discord.Member,reason: str):
    """Kick a user from guild"""
    await interaction.response.defer()
    print('inside kick')
    if interaction.user.id==user.id:
        await interaction.followup.send("You can't kick yourself")
        return
    await interaction.guild.kick(user,reason=reason)
    guild_id=str(interaction.guild_id)
    embed=discord.Embed(color=dbi.get(guild_id,db.KEYS.EMBED_COLOR),title=f"{user} was kicked")
    
    s=f"> {reason}"
    embed.description=s
    await interaction.followup.send(embed=embed)
    return

@kick.error
async def kick_error(interaction: discord.Interaction,error):
    print(f'inside kick error ',error)
    await interaction.response.send_message("You do not have permission to kick members")
    return

@client.tree.command()
@app_commands.check(check_command_permission)
async def ban(interaction: discord.Interaction,user: discord.Member,reason: str):
    """Ban a user from guild"""
    await interaction.response.defer()
    print('inside ban')
    if interaction.user.id==user.id:
        await interaction.followup.send("You can't ban yourself")
        return
    await interaction.guild.ban(user,reason=reason)
    guild_id=str(interaction.guild_id)
    embed=discord.Embed(color=dbi.get(guild_id,db.KEYS.EMBED_COLOR),title=f"{user} was banned")
    s=f"> {reason}"
    embed.description=s
    await interaction.followup.send(embed=embed)
    return

@ban.error
async def ban_error(interaction: discord.Interaction,error):
    print(f'inside ban error ',error)
    await interaction.response.send_message("You do not have permission to ban members")
    return

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
    """Generate an AI Image"""
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

async def random_items(interaction:discord.Interaction,genre,dbitems):
    guild_id=str(interaction.guild_id)
    if genre==None:
        items=[]
        for k in dbitems:
            items.extend(dbitems[k])
        item=items[random.randint(0,len(items)-1)]
        embed=discord.Embed(color=dbi.get(guild_id,db.KEYS.EMBED_COLOR))
        embed.description=item
        await interaction.followup.send(embed=embed)
        return
    if dbitems.get(genre)==None:
        await interaction.followup.send("Not a valid genre")
        return
    items=dbitems[genre]
    item=items[random.randint(0,len(items)-1)]
    embed=discord.Embed(color=dbi.get(guild_id,db.KEYS.EMBED_COLOR))
    embed.description=item
    await interaction.followup.send(embed=embed)
    return

@client.tree.command(name='random-book')
@app_commands.autocomplete(genre=genre_autocomplete)
async def random_books(interaction: discord.Interaction,genre: Optional[str]=None):
    """Get a random book recommendation"""
    await interaction.response.defer()
    print('inside random_books')
    await random_items(interaction, genre, db.books)
    return

@client.tree.command(name='random-movie')
@app_commands.autocomplete(genre=genre_autocomplete)
async def random_movies(interaction: discord.Interaction,genre: Optional[str]=None):
    """Get a random movie recommendation"""
    await interaction.response.defer()
    print('inside random_movies')
    await random_items(interaction, genre, db.movies)
    return

@client.tree.command(name='random-show')
@app_commands.autocomplete(genre=genre_autocomplete)
async def random_shows(interaction: discord.Interaction,genre: Optional[str]=None):
    """Get a random tv-show recommendation"""
    await interaction.response.defer()
    print('inside random_shows')
    await random_items(interaction, genre, db.shows)
    return

@client.tree.command()
@app_commands.check(check_command_permission)
async def purge(interaction: discord.Interaction,amount: int):
    """Delete messages in bulk"""
    await interaction.response.defer(ephemeral=True)
    print('inside purge')
    channel=interaction.channel
    cnt=0
    async for m in channel.history():
        if m.pinned==False and m.id!=interaction.id:
            await m.delete()
            cnt+=1
        if cnt==amount:break
    await interaction.followup.send(f"Purged {cnt} messages")
    await channel.send(f"Purged {cnt} messages")
    return

@purge.error
async def purge_error(interaction: discord.Interaction,error):
    print('inside purge_error ',error)
    await interaction.response.send_message("You do not have permissions to run this command",ephemeral=True)
    return

@client.tree.command()
@app_commands.check(check_command_permission)
async def warn(interaction: discord.Interaction,user: discord.Member,reason: str):
    """Add a criminal record to a user"""
    await interaction.response.defer()
    print("inside warn")
    await Warnings.warn(interaction,user,reason,dbi)
    return

@warn.error
async def warn_error(interaction: discord.Interaction,error):
    print("inside warn_error",error)
    await interaction.response.send_message("You do not have permissions to run this command",ephemeral=True)
    return

@client.tree.command(name="criminal-record")
@app_commands.check(check_command_permission)
async def criminal_record(interaction: discord.Interaction,user: discord.Member):
    """Display criminal record of a user"""
    await interaction.response.defer(ephemeral=True)
    print("inside criminal_record")
    await Warnings.criminal_record(interaction,user,dbi)
    return

@criminal_record.error
async def criminal_record_error(interaction: discord.Interaction,error):
    print("inside criminal_record_error",error)
    await interaction.response.send_message("You do not have permissions to run this command",ephemeral=True)
    return

@client.tree.command(name="remove-warning")
@app_commands.autocomplete(warning=criminal_autocomplete)
@app_commands.check(check_command_permission)
async def remove_warning(interaction: discord.Interaction,user: discord.Member,warning:str):
    """Remove a criminal record of a user"""
    await interaction.response.defer(ephemeral=True)
    print("inside remove_warning")
    await Warnings.remove_warning(interaction,user,warning)
    return

@remove_warning.error
async def remove_warning_error(interaction: discord.Interaction,error):
    print("inside remove_warning_error",error)
    await interaction.response.send_message("You do not have permissions to run this command",ephemeral=True)
    return

@client.tree.command()
async def afk(interaction: discord.Interaction,reason:str):
    """Set afk"""
    await interaction.response.defer(ephemeral=True)
    print("inside afk")
    guild_id=str(interaction.guild_id)
    user_id=str(interaction.user.id)
    nm=interaction.user.name
    if interaction.user.nick!=None:nm=interaction.user.nick
    if db.afk.get(guild_id)==None:db.afk[guild_id]=dict()
    db.afk[guild_id][user_id]=[reason,nm]
    await interaction.followup.send("afk set",ephemeral=True)
    return

@client.tree.command(name='setup')
@app_commands.check(is_owner)
async def setup(interaction: discord.Interaction,embed_color: str,role: discord.Role):
    """Set up mod bot for this server"""
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

@client.tree.command(name='add-role')
@app_commands.check(check_command_permission)
async def add_role(interaction: discord.Interaction,member: discord.Member,role: discord.Role):
    """Add a role to a member"""
    print("inside add_role")
    await interaction.response.defer()
    await member.add_roles(role)
    guild_id=str(interaction.guild_id)
    embed=discord.Embed(color=dbi.get(guild_id,db.KEYS.EMBED_COLOR))
    embed.description=f'Added role {role.name} to {member.name}'
    await interaction.followup.send(embed=embed)
    return

@add_role.error
async def add_role_error(interaction: discord.Interaction,error):
    print("add_role_error",error)
    await interaction.response.send_message("You do not have permissions to run this command",ephemeral=True)
    return

@client.tree.command(name='remove-role')
@app_commands.check(check_command_permission)
async def remove_role(interaction: discord.Interaction,member: discord.Member,role: discord.Role):
    """Remove a role from a member"""
    print("inside remove role")
    await interaction.response.defer()
    await member.remove_roles(role)
    guild_id=str(interaction.guild_id)
    embed=discord.Embed(color=dbi.get(guild_id,db.KEYS.EMBED_COLOR))
    embed.description=f'Removed role {role.name} from {member.name}'
    await interaction.followup.send(embed=embed)
    return

@remove_role.error
async def remove_role_error(interaction: discord.Interaction,error):
    print('remove_role_error',error)
    await interaction.response.send_message("You do not have permissions to run this command",ephemeral=True)
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
async def on_message(message):
    key=str(message.channel.id)
    guild_id=''
    if message.guild!=None:guild_id=str(message.guild.id)
    if db.afk.get(guild_id)!=None:
        user_id=str(message.author.id)
        if db.afk[guild_id].get(user_id)!=None:
            db.afk[guild_id].pop(user_id)
        if len(message.mentions)>0 or message.reference!=None:
            print(f"message.mentions:{message.mentions}")
            ackmsgs=dict()
            for member in message.mentions:
                if db.afk[guild_id].get(str(member.id))!=None:ackmsgs[str(member.id)]=1
            if message.reference!=None:
                msg=await message.channel.fetch_message(message.reference.message_id)
                user_id=str(msg.author.id)
                if db.afk[guild_id].get(user_id)!=None:ackmsgs[user_id]=1
            for k in ackmsgs:
                await message.channel.send(f"{db.afk[guild_id][k][1]} is currently AFK: {db.afk[guild_id][k][0]}")

    if AutoFeed.delete_tasks.get(key)!=None:
        await asyncio.sleep(AutoFeed.delete_tasks[key])
        if message.pinned==False:
            await message.delete()
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

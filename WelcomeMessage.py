from typing import Optional, Union

import discord
import db

def welcome_message(dbi,interaction: discord.Interaction,msg: str,channel: discord.TextChannel):
    print("inside welcome_message")
    text_channel=channel
    if text_channel==None:
        text_channel=interaction.channel
    guild_id = str(interaction.guild_id)
    dbi.set(guild_id,db.KEYS.TEXT_CHANNEL,text_channel)
    dbi.set(guild_id,db.KEYS.TEXT_MSG,msg)
    dbi.set(guild_id,db.KEYS.EMBED_SET,False)
    dbi.set(guild_id,db.KEYS.CAN_SEND_MSG,True)
    return

def welcome_embed(dbi,interaction: discord.Interaction,msg: str,channel: discord.TextChannel,image: discord.Attachment,footer_text: str,title_message: str):
    print("inside welcome_embed")
    guild_id=str(interaction.guild_id)
    embedcolor=dbi.get(guild_id,db.KEYS.EMBED_COLOR)
    tm = ''
    if title_message != None:
        tm=title_message
    embed = discord.Embed(title=tm,color=embedcolor)
    if image != None:
        embed.set_image(url=image.url)
    if footer_text != None:
        embed.set_footer(text=footer_text)
    embed_channel=channel
    if embed_channel==None:
        embed_channel=interaction.channel
    
    dbi.set(guild_id,db.KEYS.TEXT_MSG,msg)
    dbi.set(guild_id,db.KEYS.EMBED,embed)
    dbi.set(guild_id,db.KEYS.EMBED_CHANNEL,embed_channel)
    dbi.set(guild_id,db.KEYS.EMBED_SET,True)
    dbi.set(guild_id,db.KEYS.CAN_SEND_MSG,True)

    return



from typing import Optional, Union

import discord
import db

def dm_welcome_message(dbi,interaction: discord.Interaction,msg: str):
    print("inside dm_welcome_message")
    guild_id = str(interaction.guild_id)
    dbi.set(guild_id,db.KEYS.DM_TEXT_MSG,msg)
    dbi.set(guild_id,db.KEYS.DM_EMBED_SET,False)
    dbi.set(guild_id,db.KEYS.CAN_SEND_DM_MSG,True)
    return

def dm_welcome_embed(dbi,interaction: discord.Interaction,msg: str,image: discord.Attachment,footer_text: str,title_message: str):
    print("inside dm_welcome_embed")
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
    
    dbi.set(guild_id,db.KEYS.DM_TEXT_MSG,msg)
    dbi.set(guild_id,db.KEYS.DM_EMBED,embed)
    dbi.set(guild_id,db.KEYS.DM_EMBED_SET,True)
    dbi.set(guild_id,db.KEYS.CAN_SEND_DM_MSG,True)

    return


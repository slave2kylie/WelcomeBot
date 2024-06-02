from typing import List

import asyncio
import discord
from discord import app_commands

import db

tasks = {None:None}
msgs = {None:{None:None}}

async def repeat_task(dbi,guild_id,channel,msg,time,image,footer,title_msg):
    while True:
        print('repeat_task')
        await asyncio.sleep(time)
        print(f'msg:{msg},image:{image},footer:{footer},title_msg:{title_msg}')
        if image==None and footer==None and title_msg==None:
            print('no embed')
            await channel.send(msg)
        else:
            print('embed message')
            embedcolor=dbi.get(guild_id,db.KEYS.EMBED_COLOR)
            tm = ''
            if title_msg != None:
                tm=title_msg
            embed = discord.Embed(title=tm,color=embedcolor)
            if image != None:
                embed.set_image(url=image.url)
            if footer != None:
                embed.set_footer(text=footer)
            embed.description=msg
            await channel.send(embed=embed)
    return

async def send_auto_feed(client,interaction,dbi,msg,time,channel,image,footer,title_msg):
    print("inside send_auto_feed")
    if channel==None:
        channel=interaction.channel

    guild_id=str(interaction.guild_id)
    key=guild_id+str(channel.id)+msg
    if tasks.get(key) != None:
        await interaction.response.send_message("This message is already set in this channel",ephemeral=True)
        return
    if msgs.get(guild_id)==None:
        msgs[guild_id]={None:None}
    msgs[guild_id][msg+"+++"+str(channel.id)]=0
    task=client.loop.create_task(repeat_task(dbi,guild_id,channel,msg,time,image,footer,title_msg))
    tasks[key]=task
    await interaction.response.send_message('Auto feed is set',ephemeral=True)
    return

async def send_auto_feed_stop(interaction,msg,channel):
    print("Inside send_auto_feed_stop")
    if channel==None:
        channel=interaction.channel

    guild_id=str(interaction.guild_id)
    key=guild_id+str(channel.id)+msg
    if tasks.get(key)==None:
        await interaction.response.send_message("There is no mentioned task",ephemeral=True)
        return
    msg_key=msg+"+++"+str(channel.id)
    if msgs.get(guild_id) != None:
        if msgs[guild_id].get(msg_key) != None:
            msgs[guild_id].pop(msg_key)

    task=tasks[key]
    task.cancel()
    tasks.pop(key)
    await interaction.response.send_message('Auto feed is stopped',ephemeral=True)
    return

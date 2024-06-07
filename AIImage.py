import asyncio
import discord
import requests

async def Imagine(client,interaction,embedcolor,prompt):
	await interaction.response.defer()
	client.loop.create_task(stablehorde(interaction.channel,embedcolor,prompt))
	await interaction.followup.send("started generating Image. will take a miniute or two. please wait")
	return

async def stablehorde(channel,embedcolor,prompt):
	url="https://stablehorde.net/api/v2/generate/"

	model="ICBINP - I Can't Believe It's Not Photography"
	#model="AlbedoBase XL (SDXL)"


	_jsonbody={"prompt":prompt,"params":{"steps":20,"n":1,"sampler_name":"k_euler_a","width":512,"height":512,"cfg_scale":7,"seed_variation":1000,"seed":"","karras":True,"denoising_strength":0.75,"tiling":False,"hires_fix":False,"clip_skip":1,"post_processing":[]},"nsfw":True,"censor_nsfw":False,"trusted_workers":False,"models":[model],"shared":False,"r2":True,"jobId":"","index":0,"gathered":False,"failed":False}

	_headers={"Apikey":"0000000000"}

	resp=requests.post(url+'async',json=_jsonbody,headers=_headers)
	resp=resp.json()
	print(resp)
	idt=resp['id']
	print(f'id:{idt}')


	vl=True
	while vl==True:
	    resp=requests.get(url+"check/"+idt)
	    resp=resp.json()
	    print(resp)
	    if resp['finished']==1:
	        vl=False
	    else:
	        await asyncio.sleep(3)


	resp=requests.get(url+"status/"+idt)
	resp=resp.json()
	print(resp)
	nexturl=resp['generations'][0]['img']


	embed = discord.Embed(color=embedcolor)
	embed.set_image(url=nexturl)
	await channel.send(embed=embed)

	return
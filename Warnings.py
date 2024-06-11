import discord
import db

warnings=dict()

async def warn(interaction,user,reason,dbi):
	guild_id=str(interaction.guild_id)
	user_id=str(user.id)
	if warnings.get(guild_id)==None: warnings[guild_id]=dict()
	if warnings[guild_id].get(user_id)==None: warnings[guild_id][user_id]=[]
	warnings[guild_id][user_id].append(reason)
	embed=discord.Embed(color=dbi.get(guild_id,db.KEYS.EMBED_COLOR),title=f"{user} was warned")
	s=f"> {reason}"
	embed.description=s
	await interaction.followup.send(embed=embed) 
	return

async def criminal_record(interaction,user,dbi):
	guild_id=str(interaction.guild_id)
	user_id=str(user.id)
	nm=user.name
	if user.nick!=None:nm=user.nick
	if warnings.get(guild_id)!=None and warnings[guild_id].get(user_id)!=None:
		embed=discord.Embed(color=dbi.get(guild_id,db.KEYS.EMBED_COLOR),title=f"**{nm}'s Criminal Record**")
		s=''
		for r in warnings[guild_id][user_id]:
			s+=f"• {r}\n"
		embed.description=s[:-1]
		await interaction.followup.send(embed=embed,ephemeral=True)
	else:
		await interaction.followup.send(f"{nm} has no criminal records")
	return

async def remove_warning(interaction,user,warning):
	guild_id=str(interaction.guild_id)
	user_id=str(user.id)
	if warnings.get(guild_id)!=None and warnings[guild_id].get(user_id)!=None:
		l1=len(warnings[guild_id][user_id])
		warnings[guild_id][user_id]=list(filter(lambda x:x!=warning,warnings[guild_id][user_id]))
		if l1!=len(warnings[guild_id][user_id]):
			await interaction.followup.send("Removed warning")
			return
	await interaction.followup.send("There seems to be no such warnings for this user. Please check /criminal_record")
	return
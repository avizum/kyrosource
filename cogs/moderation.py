import discord
from discord.ext import commands
import os
import time, re
import asyncpg
import asyncio

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h":3600, "s":1, "m":60, "d":86400}

class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for v, k in matches:
            try:
                time += time_dict[k]*float(v)
            except KeyError:
                raise commands.BadArgument("{} is an invalid time-key! h/m/s/d are valid!".format(k))
            except ValueError:
                raise commands.BadArgument("{} is not a number!".format(v))
        return time


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot    

    @commands.command(help='Bans a member from the server')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member=None, *, reason="None"):
        if member == None:
            embed = discord.Embed(title="<:red_cross:844165297538727956> | No Valid member was provided", color=0xff0000)
            return await ctx.send(embed=embed)
        elif member == ctx.author:
          embed = discord.Embed(title="<:red_cross:844165297538727956> | You cannot ban yourself", color=0xff0000)
          return await ctx.send(embed=embed)
        try:
           if ctx.author.top_role.position > member.top_role.position:
            embed = discord.Embed(title="<:green_tick:844165352610725898> | Member Banned", description=f"**Reason:** {reason}\n**Moderator:** {ctx.author.mention}", color=0x00ff82)
            await ctx.send(embed=embed)
            await member.send(f"You were Banned from **{ctx.guild.name}**, Reason: **{reason}**")
            await member.ban(reason=reason)
           else:
             embed=discord.Embed(description=f"**<:red_cross:844165297538727956> | You are not allowed to moderate users that are higher than your highest role**", color=discord.Color.red())
             return await ctx.send(embed=embed)
        except:
            await member.ban(reason=reason)

    
    @commands.command(help='Kicks a member from the server')
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member=None, *, reason="None"):
        if member == None:
            embed = discord.Embed(title="<:red_cross:844165297538727956> | No Valid member was provided", color=0xff0000)
            return await ctx.send(embed=embed)
        elif member == ctx.author:
            embed = discord.Embed(title="<:red_cross:844165297538727956> | You cannot kick yourself", color=0xff0000)
            return await ctx.send(embed=embed)
        try:
          if ctx.author.top_role.position > member.top_role.position:
            embed = discord.Embed(title="<:green_tick:844165352610725898> | Member Kicked", description=f"**Reason:** {reason}\n**Moderator:** {ctx.author.mention}", color=0x00ff82)
            await ctx.send(embed=embed)
            await member.send(f"You were Kicked from **{ctx.guild.name}**, Reason: **{reason}**")
            await member.kick()
          else:
              embed=discord.Embed(description=f"**<:red_cross:844165297538727956> | You are not allowed to moderate users that are higher than your highest role**", color=discord.Color.red())
              return await ctx.send(embed=embed)
        except:
            await member.kick()


    @commands.command(help='Applies slowmode to a channel, note: due to a discord limitation, slowmode cannot be above 6 hours.')
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, slowmode: int=None, channel:discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        slowmode = max(min(slowmode, 21600), 0)
        if slowmode == None:
            embed = discord.Embed(title="<:red_cross:844165297538727956> | You need to mention the channel's slowmode to set", color=0xff0000)
            return await ctx.send(embed=embed)
        await channel.edit(slowmode_delay=slowmode)
        embed = discord.Embed(title=f"<:green_tick:844165352610725898> | Set the channel's slowmode to {slowmode}s", color=0x00ff82)
        await ctx.send(embed=embed)

    @commands.command(help='Adds a role to a member')
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx, member: discord.Member, role: discord.Role=None):
        if role == None:
            embed = discord.Embed(title="<:red_cross:844165297538727956> | No Valid Member/Role was provided")
            await ctx.send(embed=embed)
        await member.add_roles(role)
        embed = discord.Embed(description=f"**Added the role {role.mention} to {member.mention}!**", color=0x00ff82)
        await ctx.send(embed=embed)

    @commands.command(help='Removes a role from a member')
    @commands.has_permissions(manage_roles=True)
    async def removerole(self, ctx, member: discord.Member, role: discord.Role=None):
        if role == None:
            embed = discord.Embed(title="<:red_cross:844165297538727956> | No Valid Member/Role was provided")
            await ctx.send(embed=embed)
        await member.remove_roles(role)
        embed = discord.Embed(description=f"**Removed the role {role.mention} from {member.mention}!**", color=0x00ff82)
        await ctx.send(embed=embed)

    @commands.command(help='Clears the amount of messages provided from a channel')
    @commands.cooldown(1,50,commands.BucketType.guild)
    @commands.max_concurrency(1, commands.BucketType.guild)
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, limit: int =None):
        if limit == None:
            embed = discord.Embed(title="<:red_cross:844165297538727956> | You need to provide the number of messages to clear", color=0xff0000)
            return await ctx.send(embed=embed)
        elif limit > 200:
            embed = discord.Embed(title="<:red_cross:844165297538727956> | Cannot clear more than 200 messages", color=0xff0000)
            return await ctx.send(embed=embed)
        await ctx.channel.purge(limit=limit)
        embed = discord.Embed(title=f"<:green_tick:844165352610725898> | Cleared `{limit}` messages", color=0x00ff28)
        await ctx.send(embed=embed)

    @commands.command(help='Set\'s a member\'s nickname')
    @commands.has_permissions(manage_nicknames=True)
    async def setnick(self, ctx, user: discord.Member, nick):
      await user.edit(nick=nick)
      embed = discord.Embed(title='<:green_tick:844165352610725898> | Nickname Changed!', description=f'**New Nick:** {nick}\n**Moderator:** {ctx.author.mention}', color=0x00ff28)
      await ctx.send(embed=embed)

    


    @commands.command(help='Mutes a member for a specific amount of time.')
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx, member:discord.Member=None, time:TimeConverter = None, *, reason=None):
            if member is None:
                return await ctx.send('**<:red_cross:844165297538727956> | You have not provided a valid member to mute**')
            role = discord.utils.get(ctx.guild.roles, name="Muted")
            guild = ctx.guild
            
            if not role:
                embed = discord.Embed(description='The muted role doesnt seem to exist in this server, do you want to create one?', color=discord.Color.random())
                m = await ctx.send(embed=embed)
                reactions = ['✅', '❌']
                timeout = int(20.0)
                for reaction in reactions:
                  await m.add_reaction(reaction)
                
                def check(reaction, user):
                  return user == ctx.author and reaction.emoji in ['✅', '❌']
                
                try:
                  reaction, user = await self.bot.wait_for('reaction_add', timeout=timeout, check=check)
                  if reaction.emoji == '✅':
                     e = discord.Embed(description='<a:processing:857872778812325931> Creating Muted Role and setting permissions...', color=discord.Color.random())
                     await m.edit(embed=e)
                     await asyncio.sleep(1)
                     role = await guild.create_role(name="Muted", reason=f'Creation of muted role requested by {ctx.author}')
                     for channel in guild.channels:
                      await channel.set_permissions(role, speak=False, send_messages=False)
                  elif reaction.emoji == '❌':
                    emb = discord.Embed(title='Aborted', color=discord.Color.blurple())
                    await m.edit(embed=emb)
                    await asyncio.sleep(5)
                    await m.delete()
                    return await ctx.message.add_reaction('<a:incorrect:854800103193182249>')
                except asyncio.TimeoutError:
                  msg = ("**You timed out :stopwatch:**")
                  await ctx.send(msg)
                
            if time is None:
              embed=discord.Embed(title="<:green_tick:844165352610725898> | Member Muted", description=f"**Reason:** {reason}\n**Moderator:** {ctx.author.mention}", color=discord.Color.green())
              await ctx.send(embed=embed)
              await member.add_roles(role)
            else:
              embed=discord.Embed(title="<:green_tick:844165352610725898> | Member Muted", description=f"**Reason:** {reason}\n**Moderator:** {ctx.author.mention}\n**Duration: **{int(time)}s", color=discord.Color.green())
              await ctx.send(embed=embed)
              await member.add_roles(role)
              await asyncio.sleep(time)
              await member.remove_roles(role)

    
    
    @commands.command(help='Unmutes a member')
    @commands.has_permissions(manage_messages=True)
    async def unmute(self, ctx, member: discord.Member=None, *, reason="None"):
        if member is None:
            return await ctx.send('**<:red_cross:844165297538727956> | You have not provided a valid member to unmute**')
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.remove_roles(role, reason=reason)
        embed = discord.Embed(title=f"**<:green_tick:844165352610725898> | Member Unmuted**", description=f'**Reason:** {reason}\n**Moderator:** {ctx.author.mention}', color=discord.Color.green())
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Moderation(bot))

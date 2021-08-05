from discord.ext import commands
import asyncio
import traceback
import discord
import inspect
import textwrap
import importlib
from contextlib import redirect_stdout
import typing
import io
import os
# from discord_components import *
import re
import sys
import copy
import time
import importlib
from utilities.addons import checks
import aiohttp
import pathlib
import subprocess
from typing import Union, Optional
import datetime
from collections import Counter


class PerformanceMocker:

    def __init__(self):
        self.loop = asyncio.get_event_loop()

    def permissions_for(self, obj):
        perms = discord.Permissions.all()
        perms.administrator = False
        perms.embed_links = False
        perms.add_reactions = False
        return perms

    def __getattr__(self, attr):
        return self

    def __call__(self, *args, **kwargs):
        return self

    def __repr__(self):
        return '<PerformanceMocker>'

    def __await__(self):
        future = self.loop.create_future()
        future.set_result(self)
        return future.__await__()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return self

    def __len__(self):
        return 0

    def __bool__(self):
        return False

class GlobalChannel(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            return await commands.TextChannelConverter().convert(ctx, argument)
        except commands.BadArgument:
            try:
                channel_id = int(argument, base=10)
            except ValueError:
                raise commands.BadArgument(f'Could not find a channel by ID {argument!r}.')
            else:
                channel = ctx.bot.get_channel(channel_id)
                if channel is None:
                    raise commands.BadArgument(f'Could not find a channel by ID {argument!r}.')
                return channel


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None
        self.sessions = set()

    #Cleanup Functions
    async def _basic_cleanup_strategy(self, ctx, search):
        count = 0
        async for msg in ctx.history(limit=search, before=ctx.message):
            if msg.author == ctx.me and not (msg.mentions or msg.role_mentions):
                await msg.delete()
                count += 1
        return { 'Kyro': count }

    async def run_process(self, command):
        try:
            process = await asyncio.create_subprocess_shell(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result = await process.communicate()
        except NotImplementedError:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result = await self.bot.loop.run_in_executor(None, process.communicate)

        return [output.decode() for output in result]

    def cleanup_code(self, content):
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        return content.strip('` \n')

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    def get_syntax_error(self, e):
        if e.text is None:
            return f'```py\n{e.__class__.__name__}: {e}\n```'
        return f'```py\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```'
    
    @commands.command(pass_context=True, name='eval')
    @commands.is_owner()
    async def _eval(self, ctx, *, body: str):

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.trash(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.trash(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.trash(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.trash(f'```py\n{value}{ret}\n```')
                
    @commands.group(aliases=['dev'], invoke_without_command=True)
    @commands.is_owner()
    async def developer(self, ctx):
        pass
    

    @developer.command()
    @commands.is_owner()
    async def shutdown(self, ctx):
        embed = discord.Embed(title='Are you sure you want to shutdown this bot?', color=discord.Color.blurple())
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
            await m.delete()
            msg = await ctx.send("Okay, bot shutting down in **3** seconds!")
            await asyncio.sleep(0.5)
            await msg.edit(content = "Okay, bot shutting down in **2** seconds!")
            await asyncio.sleep(0.5)
            await msg.edit(content = "Okay, bot shutting down in **1** seconds!")
            await msg.edit(content="**:skull_crossbones: Bot is now off and will not respond!**")
            await self.bot.close()
          elif reaction.emoji == '❌':
            emb = discord.Embed(title='Aborted', color=discord.Color.blurple())
            await m.edit(embed=emb)
            await asyncio.sleep(5)
            await m.delete()
            await ctx.message.add_reaction('<a:incorrect:854800103193182249>')
        except asyncio.TimeoutError:
          msg = ("**You timed out :stopwatch:**")
          await ctx.send(msg)

    
    # @commands.command(aliases=['calc'])
    # @commands.is_owner()
    # async def calculator(self, ctx):
    #     components = [[
    #         Button(style=ButtonStyle.grey, label="1"),
    #         Button(style=ButtonStyle.grey, label="2"),
    #         Button(style=ButtonStyle.grey, label="3"),
    #         Button(style=ButtonStyle.blue, label="x"),
    #         Button(style=ButtonStyle.red, label="AC")
    #         ],[
    #         Button(style=ButtonStyle.grey, label="4"),
    #         Button(style=ButtonStyle.grey, label="5"),
    #         Button(style=ButtonStyle.grey, label="6"),
    #         Button(style=ButtonStyle.blue, label="÷"),
    #         Button(style=ButtonStyle.red, label="CE")
    #         ],[
    #         Button(style=ButtonStyle.grey, label="7"),
    #         Button(style=ButtonStyle.grey, label="8"),
    #         Button(style=ButtonStyle.grey, label="9"),
    #         Button(style=ButtonStyle.blue, label="-"),
    #         Button(style=ButtonStyle.red, label="Exit")
    #         ],[
    #         Button(style=ButtonStyle.grey, label='00'),
    #         Button(style=ButtonStyle.grey, label="0"),
    #         Button(style=ButtonStyle.grey, label="."),
    #         Button(style=ButtonStyle.blue, label="+"),
    #         Button(style=ButtonStyle.green, label="=")
    #         ]]
    #     dis_components = [[
    #         Button(style=ButtonStyle.grey, label="1", disabled=True),
    #         Button(style=ButtonStyle.grey, label="2", disabled=True),
    #         Button(style=ButtonStyle.grey, label="3", disabled=True),
    #         Button(style=ButtonStyle.blue, label="x", disabled=True),
    #         Button(style=ButtonStyle.red, label="AC", disabled=True)
    #         ],[
    #         Button(style=ButtonStyle.grey, label="4", disabled=True),
    #         Button(style=ButtonStyle.grey, label="5", disabled=True),
    #         Button(style=ButtonStyle.grey, label="6", disabled=True),
    #         Button(style=ButtonStyle.blue, label="÷", disabled=True),
    #         Button(style=ButtonStyle.red, label="CE", disabled=True)
    #         ],[
    #         Button(style=ButtonStyle.grey, label="7", disabled=True),
    #         Button(style=ButtonStyle.grey, label="8", disabled=True),
    #         Button(style=ButtonStyle.grey, label="9", disabled=True),
    #         Button(style=ButtonStyle.blue, label="-", disabled=True),
    #         Button(style=ButtonStyle.red, label="Exit", disabled=True)
    #         ],[
    #         Button(style=ButtonStyle.grey, label='00', disabled=True),
    #         Button(style=ButtonStyle.grey, label="0", disabled=True),
    #         Button(style=ButtonStyle.grey, label=".", disabled=True),
    #         Button(style=ButtonStyle.blue, label="+", disabled=True),
    #         Button(style=ButtonStyle.green, label="=", disabled=True)
    #         ]]
    #     gui1 = '0'
    #     evaldict = {"+":"+","-":"-","÷":"/","x":"*"}
    #     emb = discord.Embed(title=f"{ctx.author.name}'s Owner Calculator (epic)")
    #     emb.description = f"```{gui1}\n```"
    #     m = await ctx.send(embed=emb, components=components)

    #     while True:
    #         res = await self.bot.wait_for("button_click")
    #         emb2 = discord.Embed(title=f"{ctx.author.name}'s Onwer Calculator (epic)")
    #         await res.respond(type=InteractionType.UpdateMessage, embed=emb2)
    #         if res.user==ctx.author:
    #             if res.component.label in ['1','2','3','4','5','6','7','8','9','0','00',"."]:
    #                  if gui1=='0':
    #                     gui1 = res.component.label
    #                     emb2.description=f"```{gui1}\n```"
    #                     await m.edit(embed=emb2, components=components)
    #                  else:
    #                      gui1 = f"{gui1}{res.component.label}"
    #                      emb2.description=f"```{gui1}\n```"
    #                      await m.edit(embed=emb2, components=components)
    #             elif res.component.label in ["+","-","÷","x"]:
    #                   ev = evaldict[res.component.label]
    #                   gui1 = f"{gui1}{ev}"
    #                   emb2.description=f"```{gui1}\n```"
    #                   await m.edit(embed=emb2, components=components)
    #             elif res.component.label == "=":
    #                   d = eval(gui1)
    #                   gui1 = d
    #                   emb2.description=f"```{gui1}\n```"
    #                   await m.edit(embed=emb2, components=components)
    #             elif res.component.label=="AC":
    #                   gui1 = '0'
    #                   emb2.description=f"```{gui1}\n```"
    #                   await m.edit(embed=emb2, components=components)
    #             elif res.component.label=="CE":
    #                 if gui1[:-1] == "":
    #                   gui1='0'
    #                   emb2.description=f"```{gui1}\n```"
    #                   await m.edit(embed=emb2, components=components)
    #                 else:
    #                     gui1=gui1[:-1]
    #                     emb2.description=f"```{gui1}\n```"
    #                     await m.edit(embed=emb2, components=components)
    #             elif res.component.label=="Exit":
    #                   emb2.description=f"```diff\n- CLOSED\n```"
    #                   await m.edit(embed=emb2, components=dis_components)

    @developer.command()
    @commands.is_owner()
    async def force(self, ctx, channel: Optional[GlobalChannel], who: Union[discord.Member, discord.User], *, command: str):
        msg = copy.copy(ctx.message)
        channel = channel or ctx.channel
        msg.channel = channel
        msg.author = who
        msg.content = ctx.prefix + command
        new_ctx = await self.bot.get_context(msg, cls=type(ctx))
        await self.bot.invoke(new_ctx)

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, *, ext): 
        self.bot.load_extension(f'cogs.{ext}')
        await ctx.send(f"<:green_tick:844165352610725898> **|** Loaded Extension: **{ext}.py**")

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, *, ext):
        self.bot.unload_extension(f'cogs.{ext}')
        await ctx.send(f"<:green_tick:844165352610725898> **|** Unloaded Extension: **{ext}.py**")

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, *, ext):
        msg = await ctx.send(f"<:green_tick:844165352610725898> **|** Reloading Extension: **{ext}.py**.....")
        await asyncio.sleep(0.5)
        self.bot.reload_extension(f'cogs.{ext}')
        await msg.edit(f"<:green_tick:844165352610725898> **|** Reloaded Extension: **{ext}.py**")

    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx):
      embed = discord.Embed(title='<a:tick:854961738439983125> Syncing..', color=0x01CFA9)
      msg = await ctx.send(embed=embed)
      for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
         self.bot.reload_extension(f'cogs.{filename[:-3]}')
         await asyncio.sleep(0.3)
      e = discord.Embed(title='<a:tick:854961738439983125> Syncing..', description='Syncing Utility Extensions', color=0x01CFA9)
      await msg.edit(embed=e)
      self.bot.reload_extension('utilities.addons.context')
      await asyncio.sleep(1)
      emb = discord.Embed(title=f'<a:tick:854961738439983125> Synced\nReloaded all {len(self.bot.extensions)} cogs and extensions', description='\n'.join(self.bot.extensions), color=0x01CFA9)
      await msg.edit(embed=emb, delete_after=5)

    @commands.command()
    @commands.is_owner()
    async def noprefix(self, ctx):
     if ctx.author.id == 422854944857784322:
      self.bot.noPrefixSomeone = not self.bot.noPrefixSomeone
      if self.bot.noPrefixSomeone == True:
          embed = discord.Embed(description='No prefix is now enabled!', color=discord.Color.blurple())
      else:
          embed = discord.Embed(description='No prefix is now disabled!', color=discord.Color.blurple())
      await ctx.send(embed=embed)
      
     elif ctx.author.id == 812901193722363904:
      self.bot.noPrefixHiro = not self.bot.noPrefixHiro
      if self.bot.noPrefixHiro == True:
          embed = discord.Embed(description='No prefix is now enabled!', color=discord.Color.blurple())
      else:
          embed = discord.Embed(description='No prefix is now disabled!', color=discord.Color.blurple())
      await ctx.send(embed=embed)
    
    @developer.command(name='upload')
    @commands.is_owner()
    async def photoupload(self, ctx, *, url=None):
      async with ctx.typing():
        bytes = None
        if url:
            r =  await self.bot.session.get(url)
            if r.status == 200:
              bytes = await r.read()
              if bytes is None:
                if len(file := ctx.message.attachments) > 0:
                  bytes = await file[0].read()
                elif len(file := ctx.message.reference.resolved.attachments) > 0:
                  bytes = await file[0].read()
                else:
                  return await ctx.send("No attachment found.")
           
        r = await self.bot.session.post("https://someone4.nothing-to-see-he.re/upload", data={"image": bytes})
        if r.status == 200:
            json = await r.json()
            url = json.get("url", "None")
            embed = discord.Embed(description=url, color=0x2F3136)
            embed.set_image(url=url or '')
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"An error occurred. ({r.status})")

    @developer.command()
    @commands.is_owner()
    async def cleanup(self, ctx, search=10):
      await ctx.message.add_reaction("<a:loading:856812922320060416>")
      strategy = self._basic_cleanup_strategy
      spammers = await strategy(ctx, search)
      deleted = sum(spammers.values())
      messages = [f'{deleted} message{" was" if deleted == 1 else "s were"} removed.']
      if deleted:
            await ctx.message.remove_reaction('<a:loading:856812922320060416>', self.bot.user)
            messages.append('')
            spammers = sorted(spammers.items(), key=lambda t: t[1], reverse=True)
            messages.extend(f'- **{author}**: {count}' for author, count in spammers)

            embed = discord.Embed(description='\n'.join(messages), color=discord.Color.random())
            m = await ctx.send(embed=embed)
            await asyncio.sleep(5)
            await m.delete()

    @developer.command()
    @commands.is_owner()
    async def debugmode(self, ctx):
     self.bot.DebugMode = not self.bot.DebugMode
     if self.bot.DebugMode == True:
       embed = discord.Embed(description='Debug Mode has been enabled', color=discord.Color.blurple())
     else:
       embed = discord.Embed(description='Debug Mode has been disabled', color=discord.Color.blurple())
     await ctx.send(embed=embed)
        
    @commands.command()    
    @commands.is_owner()
    async def gitsync(self, ctx):
        proc = await asyncio.create_subprocess_shell("git pull https://github.com/someone782/Kyro.git", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        if stderr:
            shell = f"[stderr]\n{stderr.decode()}"
        if stdout:
            shell = f"[stdout]\n{stdout.decode()}"
        em=discord.Embed(description=f"```sh\n$git pull\n{shell}```\n", color=discord.Color.random())
        await ctx.reply(embed=em, mention_author=False)

               
    @developer.command()
    @commands.is_owner()
    async def restart(self, ctx):
        embed = discord.Embed(description='Are you sure you want to restart this bot?', color=discord.Color.blurple())
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
            e = discord.Embed(description='<a:processing:857872778812325931> Restarting..', color=discord.Color.random())
            await m.edit(embed=e)
            await asyncio.sleep(2)
            await m.delete()
            await ctx.message.add_reaction('✅')
            await self.bot.close()
          elif reaction.emoji == '❌':
            emb = discord.Embed(title='Aborted', color=discord.Color.blurple())
            await m.edit(embed=emb)
            await asyncio.sleep(5)
            await m.delete()
            await ctx.message.add_reaction('<a:incorrect:854800103193182249>')
        except asyncio.TimeoutError:
          msg = ("**You timed out :stopwatch:**")
          await ctx.send(msg)
            
    @developer.command()
    @commands.is_owner()
    async def blacklist(self, ctx, member:discord.User, reason):
        try:
            self.bot.cache.blacklisted[member.id]
            return await ctx.send("User Already in blacklist.")
        except KeyError:
            await self.bot.db.execute("INSERT INTO blacklisted (member_id, reason) VALUES ($1, $2)", member.id, reason)
            self.bot.cache.blacklisted[member.id] = reason
            await ctx.send(f"**<:green_tick:844165352610725898> | Successfully blacklisted `{member}` for {reason}**")

    @developer.command()
    @commands.is_owner()
    async def unblacklist(self, ctx, member:discord.User):
        try:
            self.bot.cache.blacklisted[member.id]
        except KeyError:
            return await ctx.send("User is not currently blacklisted.")
        await self.bot.db.execute("DELETE FROM blacklisted WHERE member_id = $1", member.id)
        self.bot.cache.blacklisted.pop(member.id)
        await ctx.send(f"**<:green_tick:844165352610725898> | Successfully unblacklisted `{member}`**")

    @developer.command(name='del')
    @commands.is_owner()
    async def msgdelete(self, ctx):
        if not ctx.message.reference:
            return await ctx.send('Reply to the message you want to delete!')
        reference = ctx.message.reference.resolved
        if reference.author != self.bot.user:
            return await ctx.send('I can only delete my own messages!')
        await reference.delete()

    @developer.command()
    @commands.is_owner()
    async def leaveguild(self, ctx, guild):
        embed = discord.Embed(description=f'Are you sure you want to make me leave {guild}', color=discord.Color.random())
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
              for guild in self.bot.guilds:
                  if guild.name == guild:
                      await guild.leave()
              await m.delete()
              await ctx.message.add_reaction('✅') 
          else:
              await m.delete()
        except asyncio.TimeoutError:
            await ctx.send("**You timed out :stopwatch:**") 


    @developer.command(name='as')
    @commands.is_owner()
    async def webho(self,ctx, member: typing.Union[discord.User, discord.Member], *, text):
        image = str(self.bot.user.avatar.url)
        async with aiohttp.ClientSession() as ses:
             async with ses.get(str(image)) as r:
                img = await r.read()
        webhooks = await ctx.channel.webhooks()
        kyro_webhook = discord.utils.get(webhooks, name="Kyro")
        if not kyro_webhook:
                    kyro_webhook = await ctx.channel.create_webhook(
                        name="Kyro", reason="Kyro dev-as command. Might be made public for server admins soon.",
                        
                        avatar=img)
        await kyro_webhook.send(
                    text, username=member.display_name,
                    avatar_url=member.avatar.with_format("png").url,
                    allowed_mentions=discord.AllowedMentions.none())



        

    

        
        
      
        
def setup(bot):
    bot.add_cog(Owner(bot))

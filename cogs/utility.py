from copy import deepcopy
import discord
from discord.ext import commands, menus
import typing
from discord.ext.commands.cooldowns import BucketType
import psutil
import os
from datetime import datetime
import pytz
import codecs
from io import BytesIO
from jishaku.functools import executor_function
from google_trans_new import google_translator
import googletrans
import asyncpg
import mystbin
import math
import io
import async_cse
from requests import get
import pathlib
import asyncio
from jishaku.codeblocks import codeblock_converter
import aiohttp
import async_tio
from discord.utils import get
import json
import re, humanize
import time
from aiohttp import ClientSession
from utilities.addons.webhook import Webhook, AsyncWebhookAdapter
from utilities.addons.paginator import Paginator


#Loading JSON Data
file = open("config.json", "r")
data = file.read()
objects = json.loads(data)


googlekey = objects['GOOGLE_KEY']
google = async_cse.Search(googlekey)
mystin_client = mystbin.Client()


#Math Functions
def add(x: float, y: float):
    return x + y

def minus(x: float, y: float):
    return x - y

def multiply(x: float, y: float):
    return x * y

def divide(x: float, y: float):
    return x / y

#Defining Remind Command
def converttime(time):
    pos = ['s','m','h']
    time_dict = {'s':1,'m':60,'h':60*60}
    unit = time[-1]
    if unit not in pos:
        return -1
  
    try:
        val = int(time[:-1])
    except:
        return -2
    
    return val*time_dict[unit]


def isImage(url):
    url = url.lower()
    if url.endswith("png") or url.endswith("jpg") or url.endswith("jpeg") or url.endswith("webp"):
        return True
    return False

class ArchFlag(commands.FlagConverter):
    remind: typing.Optional[int]


@executor_function
def do_translate(output, text):
    translator = googletrans.Translator()
    translation = translator.translate(str(text), dest=str(output))
    return translation


@executor_function
def getFile(text, end = "txt", filename="message"):
    f = io.StringIO()
    f.write(text)
    f.seek(0)
    return discord.File(f, filename=f"{filename}.{end}")

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_message(self, msg):
        pass
   

    @commands.command(help='Gets the bot\'s delay from discord.')
    @commands.cooldown(1,5,commands.BucketType.user)
    async def ping(self, ctx):
      start = time.perf_counter()
      em = discord.Embed(description="**🏓 Calculating Bot's Latency...**")
      msg = await ctx.reply(embed=em, mention_author=False)
      end = time.perf_counter()
      duration = (end - start) * 1000
      poststart = time.perf_counter()
      await self.bot.db.fetch("SELECT 1")
      postduration = (time.perf_counter()-poststart) * 1000
      db_ping = round(postduration, 2)
      embed = discord.Embed(title='**🏓 Pong**', color=0x2F3136)
      embed.add_field(name='**Websocket**', value=f'```py\n{round(self.bot.latency* 1000,2)} ms\n```', inline=True)
      embed.add_field(name='**Typing**', value="```py\n{:.2f} ms\n```".format(round(duration)), inline=True)
      embed.add_field(name='**Database**', value=f"```py\n{db_ping} ms\n```", inline=True)
      await msg.edit(embed=embed, allowed_mentions=discord.AllowedMentions.none())

    @commands.command(help="Get's the server's membercount")
    @commands.cooldown(1,5,commands.BucketType.user)
    async def membercount(self, ctx):
        embed1 = discord.Embed(description="**Getting the server's member count...**", color=0x0000ff)
        msg = await ctx.send(embed=embed1)
        await asyncio.sleep(0.8)
        embed2 = discord.Embed(description=f"**{ctx.guild.name} has total {ctx.guild.member_count} members**", color=0x0000ff)
        await msg.edit(embed=embed2)

    @commands.command(aliases=['about'], help="Get's information about this bot.")
    @commands.cooldown(1,5,commands.BucketType.user)
    async def stats(self, ctx):
        embed = discord.Embed(title="Kyro's Stats", description="```diff\n- Here are some stats and about Kyro```", color=0xfdfdfd)
        embed.add_field(name="<:python:843043042150580246> Py Version", value="3.9")
        embed.add_field(name="<:dpy:843043419911225364> Dpy Version", value="2.0.0")
        embed.add_field(name="<:godric:843043843493986325> Total Servers", value=f"{len(self.bot.guilds)}")
        embed.add_field(name="<:member:843044295396425759> Total Users", value=sum(1 for _ in self.bot.get_all_members()))
        embed.add_field(name="<a:dev:843045397949579295> Developers", value="[! Hiro ! \🖤#0069\nSomeone#5555](https://shortyy.ml/developers)")
        embed.add_field(name=":ping_pong: Ping", value=f"{round(self.bot.latency * 1000)}ms")
        embed.add_field(name="<:commands:843047772616917042> Total Commands", value=f"{len(self.bot.commands)}")
        embed.add_field(name="<:partyboi:843048569216172052> Created on", value="Tuesday, 18th May 2021", inline=True)
        embed.add_field(name="<:link:843049199834890260> Invite me", value="[Click here](https://discord.com/oauth2/authorize?client_id=844154929815748649&scope=bot&permissions=271887566)")
        embed.set_footer(text="Bot Version: v1.0.0 | Kyro")
        await ctx.send(embed=embed)
    
    @commands.command(help="Gets information about the current server")
    @commands.cooldown(1,5,commands.BucketType.user)
    async def serverstats(self, ctx):
        count = 0
        for member in ctx.guild.members:
            if not str(member.status) =="offline":
                count += 1
           
        if ctx.guild.banner and ctx.guild.splash is not None:   
            if ctx.guild.banner is None:
                banner = str(ctx.guild.splash.url)
            else:
                banner = str(ctx.guild.banner.url)
        else:
            banner = ctx.author.avatar.url
                
                
                
     
      
        if ctx.guild.icon is not None:
            icon = str(ctx.guild.icon.url)
        else:
            icon = ctx.author.avatar.url
        channels = len(ctx.guild.channels)
        roles = len(ctx.guild.roles)
        region = str(ctx.guild.region)
        verification = str(ctx.guild.verification_level)

        embed = discord.Embed(title=f"{ctx.guild.name}", color=discord.Color.random())
        embed.set_thumbnail(url=icon)
        embed.add_field(name="Server ID", value=f"{str(ctx.guild.id)}")
        embed.add_field(name="Description", value=f"{ctx.guild.description}", inline=False)
        embed.add_field(name="Member Count", value=f"<:status_online:845560221526130698> {count} <:BlankEmoji:845557569945993216> <:status_offline:845562287161868298> {ctx.guild.member_count}", inline=False)
        embed.add_field(name="Channels", value=f"<:TextChannel:845557685448867890> {len(ctx.guild.text_channels)} Text <:BlankEmoji:845557569945993216> <:VoiceChannel:845557617480433684> {len(ctx.guild.voice_channels)} Voice", inline=False)
        embed.add_field(name="Role Count", value=roles)
        embed.add_field(name="Emojis", value=f"{len(ctx.guild.emojis)}")
        embed.add_field(name="Region", value=f"{region.capitalize()}", inline=False)
        embed.add_field(name="Boosts", value=f"<:boost_count:845564904407957534> {ctx.guild.premium_subscription_count} (Level  {ctx.guild.premium_tier})")
        embed.add_field(name="Verification Level", value=f"{verification.capitalize()}", inline=False)
        embed.set_footer(text=f"Server created on: {(str(ctx.guild.created_at.strftime('%Y-%m-%d %H:%M')))}")
        embed.set_image(url=banner)
        await ctx.send(embed=embed)
        
        
    @commands.command(help="Give's the server's icon")
    @commands.cooldown(1,5,commands.BucketType.user)
    async def servericon(self, ctx):
      icon = str(ctx.guild.icon.url)
      embed = discord.Embed(title=f'Icon for {ctx.guild.name}', color=discord.Color.random())
      embed.set_image(url=icon)
      await ctx.send(embed=embed)
        
    @commands.command(name='clear-my-data', help="Deletes your data from our database")
    @commands.cooldown(1,5,commands.BucketType.user)
    async def deletemydata(self,ctx):
        e = discord.Embed(title='Data Removal', description='Are you sure you want to delete your data?\nThis will remove data from `economy` and `time`.', color=discord.Color.red())
        confirm = await ctx.confirm(embed=e)
#         reactions = ['✅', '❌']
#         for reaction in reactions:
#             await msg.add_reaction(reaction)
        
#         def check(reaction, user):
#             return user == ctx.author and reaction.emoji in ['✅', '❌']
#         try:
#             reaction, user = await self.bot.wait_for('reaction_add', timeout=30, check=check)
#         except asyncio.TimeoutError:
#             timeoutembed = discord.Embed(title='Data Removal', description='Timed Out.', color=discord.Color.red())
#             return await msg.edit(embed=timeoutembed)
            
#         if reaction.emoji == '✅':
        if confirm:
                removing_time = await self.bot.db.execute("DELETE FROM times WHERE user_id = $1", ctx.author.id)
                removing_economy = await self.bot.db.execute("DELETE FROM accounts WHERE user_id = $1", ctx.author.id)
                em = discord.Embed(title='Data Removal', description='Your data has been removed.', color=discord.Color.red())
                await ctx.send(embed=em)
        else:
                emb = discord.Embed(title='Data Removal', description='Aborted.', color=discord.Color.green())
                return await ctx.send(embed=emb)
        
        
    @commands.command(help="Set's the bot's prefix for this server")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def setprefix(self, ctx, prefix:str=None):
      if prefix == None:
        return await ctx.send("**<:red_cross:844165297538727956> | You have not specified a valid prefix for this command**")
      elif len(prefix) > 5:
        return await ctx.send("**<:red_cross:844165297538727956> | That prefix is too large! Make sure it's below 5 characters!**")
      await self.bot.db.execute("UPDATE prefixes SET prefix = $1 WHERE guild_id = $2", prefix, ctx.guild.id)
      await self.bot.cache.cache_all()
      await ctx.send(f"**<a:animated_tick:847447732623900672> | Server prefix changed to `{prefix}`**")      


    @setprefix.error
    async def setprefix_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(description="**<:red_cross:844165297538727956> | Cannot do that, You don't have the Permissions of `Manage Server`**", color=0xff0000)
            await ctx.send(embed=embed)



    @commands.command(help="Get's information on the current channel, or a channel mentioned")
    @commands.cooldown(1,5,commands.BucketType.user)
    async def channelstats(self, ctx, channel: discord.TextChannel=None):
        if channel == None:
            channel = ctx.channel

        embed = discord.Embed(
            title=f"Stats for **{channel.name}**",
            description=f"{'**Category:** {}'.format(channel.category.name) if channel.category else 'This channel is not in a category'}",
            color=discord.Colour.random(),
        )
        embed.add_field(name="Channel Guild", value=ctx.guild.name, inline=False)
        embed.add_field(name="Channel Id", value=channel.id, inline=False)
        embed.add_field(
            name="Channel Topic",
            value=f"{channel.topic if channel.topic else 'No topic.'}",
            inline=False,
        )
        embed.add_field(name="Channel Position", value=channel.position, inline=False)
        embed.add_field(
            name="Channel Slowmode Delay", value=channel.slowmode_delay, inline=False
        )
        embed.add_field(name="Channel is nsfw?", value=channel.is_nsfw(), inline=False)
        embed.add_field(name="Channel is news?", value=channel.is_news(), inline=False)
        embed.add_field(
            name="Channel Creation Time", value=f"{(str(channel.created_at.strftime('%Y-%m-%d %H:%M')))}", inline=False
        )
        embed.add_field(
            name="Channel Permissions Synced",
            value=channel.permissions_synced,
            inline=False,
        )
        await ctx.send(embed=embed)

    @commands.command(help="Give's you the bot's invite link as well as the bot's support server")
    @commands.cooldown(1,5,commands.BucketType.user)
    async def invite(self, ctx):
        embed = discord.Embed(
            title="<:link:843049199834890260> You can invite me by clicking here!",
            url="https://discord.com/oauth2/authorize?client_id=844154929815748649&scope=bot&permissions=271887566",
            description="**<:link:843049199834890260> [Clicking here will lead you to the support server!](https://discord.gg/hXFRM4Vxdv)**\n**<:link:843049199834890260> [Click here to vote!](https://top.gg/bot/844154929815748649/vote)**",
            color = discord.Color.random()
        )
        await ctx.send(embed=embed)

    @commands.command(help="Give's you the link to vote for Kyro")
    @commands.cooldown(1,5,commands.BucketType.user)
    async def vote(self, ctx):
        embed = discord.Embed(description='[Click to vote on top.gg](https://top.gg/bot/844154929815748649/vote)\n\n[Cick to vote on discordbotlist.com](https://discordbotlist.com/bots/kyro/upvote)' ,color=discord.Color.random())
        await ctx.send(embed=embed)
        
    @commands.command(help="Give's you the link to the source for Kyro")
    @commands.cooldown(1,5,commands.BucketType.user)
    async def source(self, ctx):
        embed = discord.Embed(description='To view my source, click [here](https://github.com/someone782/kyrosource)' ,color=discord.Color.random())
        await ctx.send(embed=embed)    
    
        
    @commands.command(help="Marks you as AFK, people mentioning you will get a message that you are AFK")
    @commands.cooldown(1,5,commands.BucketType.user)
    async def afk(self,ctx,*, reason:str=None):
         if reason is None:
             msg = f"**<:status_idle:847051644209332234>  {ctx.author.name} is now set to AFK**"
         else:
             msg = f'**<:status_idle:847051644209332234>  {ctx.author.name} is now set to Afk:** {reason}'
         await ctx.send(msg, allowed_mentions=discord.AllowedMentions.none())
         await asyncio.sleep(2)
         self.bot.afk[ctx.author.id] = {"reason": reason}
    
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id in list(self.bot.afk):
            self.bot.afk.pop(message.author.id)
            await message.channel.send(f'**<:status_online:845560221526130698>  Welcome back {message.author.name}, now you are no longer AFK**')                
       # for user in list(self.bot.afk):
           # data = self.bot.afk[user]
           # memberobject = await self.bot.fetch_user(user)
           # if memberobject in message.mentions:
                    #if data["reason"] is None:
                       #  msg = f" <:status_dnd:847051669811626024>  **{memberobject.name} is currently AFK**"
                    #else:
                       #  msg = f" <:status_dnd:847051669811626024>  **{memberobject.name} is currently AFK: {data['reason']}**"
                   # await message.channel.send(msg, allowed_mentions=discord.AllowedMentions.none())
                    
                    
 
    @commands.group(invoke_without_command=True, help="Does math equations")
    @commands.cooldown(1,5,commands.BucketType.user)
    async def math(self, ctx):
        await ctx.reply("**<:red_cross:844165297538727956> You have not provided a valid function, You can use:\n\nAdd\nSubtract\nMultiply\nDivide\nSquareroot\nPercentage\nFactorial**")

    @math.command()
    async def add(self, ctx, num1: float, num2: float):
        res = add(num1, num2)
        await ctx.reply(f"**The sum of `{num1}` and `{num2}` is `{res}`**", mention_author=False)

    @math.command()
    async def subtract(self, ctx, num1: float, num2: float):
        res = minus(num1, num2)
        await ctx.reply(f"**The difference of `{num1}` and `{num2}` is `{res}`**", mention_author=False)

    @math.command()
    async def multiply(self, ctx, num1: float, num2: float):
        res = multiply(num1, num2)
        await ctx.reply(f"**The product of `{num1}` and `{num2}` is `{res}`**", mention_author=False)

    @math.command()
    async def divide(self, ctx, num1: float, num2: float):
        res = divide(num1, num2)
        await ctx.reply(f"**When i divide `{num1}` with `{num2}`, i get `{res}` as the answer**", mention_author=False)

    @math.command()
    async def squareroot(self, ctx, num1: float):
        res = math.sqrt(num1)
        await ctx.reply(f"**The squareroot of `{num1}` is `{res}`**", mention_author=False)

    @math.command()
    async def percentage(self, ctx, num1: float, num2: float):
        res = num1 * num2/100
        await ctx.reply(f"**The `{num2}` percent of `{num1}` is `{res}`**", mention_author=False)

    @math.command()
    async def factorial(self, ctx, num: int):
        factorial = 1
        if num < 0:
            await ctx.send("**Sorry, factorial does not exist for negative numbers**")
        elif num == 0:
            await ctx.send("**Cannot find the factorial for `0`**")
        elif num > 100:
            return await ctx.send("**Discord will mark me as spam if i go above number 100 for Factorial :p**")
        else:
            for i in range(1,num + 1):
                factorial = factorial*i
            await ctx.reply(f"**The Factorial of `{num}` is `{factorial}`**")

    @commands.command(help="Upload's a emoji to the server")
    @commands.cooldown(1,5,commands.BucketType.user)
    @commands.has_permissions(manage_emojis=True)
    async def upload_emoji(self, ctx,  emoji: discord.PartialEmoji = None, name = None):
        if emoji == None:
          return await ctx.reply("**<:red_cross:844165297538727956> | You need to provide a valid emoji!**", mention_author=False)
        try:
            if name == None:
                name = emoji.name
            guild = ctx.guild
            async with aiohttp.ClientSession() as ses:
                async with ses.get(str(emoji.url)) as r:
                    img = BytesIO(await r.read())
                    value = img.getvalue()
                if r.status in range(200, 299):
                    embed = discord.Embed(title="Uploading Emoji...", color=discord.Color.random())
                    embed.set_image(url=emoji.url)
                    msg = await ctx.send(content="Are you sure you want to upload this emoji? React with ✅ to confirm ",embed=embed)
                    timeout = int(10.0)
                    reactions = ['✅', '❌']
                    for reaction in reactions:
                        await msg.add_reaction(reaction)
 
                    def check(reaction, user):
                        return user == ctx.author and str(reaction.emoji) in ['✅','❌']

                    try: 
                        reaction, user = await self.bot.wait_for('reaction_add', timeout=timeout, check=check)

                    except asyncio.TimeoutError:
                        await msg.delete()
                        msg1=("**You timed out :stopwatch:**") 
                        return await ctx.channel.send(msg1)
                    if reaction.emoji == '✅':
                        emoji1 = await guild.create_custom_emoji(image=value, name=name, reason=f'Uploaded by {ctx.author}')
                        await ctx.send(f'**<:green_tick:844165352610725898> | Created Emoji!**')
                        await ses.close()
                    elif reaction.emoji == '❌':
                        await msg.delete()
                        return await ctx.send("**Aborted**")
                else:
                    await ctx.send("**<:red_cross:844165297538727956> | There was an error while proccessing the command!")
                    await ses.close()
        except discord.HTTPException:
            await ctx.send("**Max Emoji's reached for the server!**")


    @upload_emoji.error
    async def upload_emoji_error(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(description="**<:red_cross:844165297538727956> | Cannot do that, I don't have the Permissions of `Manage Emojies`**", color=0xff0000)
            await ctx.send(embed=embed)
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(description="**<:red_cross:844165297538727956> | Cannot do that, You don't have the Permissions of `Manage Emojies`**", color=0xff0000)
            await ctx.send(embed=embed)
        elif isinstance(error, commands.PartialEmojiConversionFailure):
          embed = discord.Embed(description="**<:red_cross:844165297538727956> | Please Provide a valid emoji**", color=0xff0000)
          await ctx.send(embed=embed)
        else:
          raise error

    @commands.command(help="Translates a text using google translate")
    @commands.cooldown(1,5,commands.BucketType.user)
    async def translate(self, ctx, language="en", *, translateText="None"):
          translation = await do_translate(language, translateText)
          embed = discord.Embed(color=discord.Color.random())
          embed.add_field(name='Input', value=f'```{translateText}```', inline=True)
          embed.add_field(name='Output', value=f'```{translation.text}```', inline=True)
          embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url) 
          await ctx.send(embed=embed)
                          

    @commands.command(help="Reminds you in a specific amout of time for a reason you give, if you want the bot to DM you once the time for your reminder comes use the --DM flag at the end of your message.")
    @commands.cooldown(1,5,commands.BucketType.user)
    async def remind(self, ctx, duration, *, reason=None):
        if ctx.message.content.endswith('--DM'):
            dm = True
            reason = reason[:-4]
        else:
            dm = False
            reason = reason
        t = converttime(duration)
        if t == -1:
            await ctx.reply("**You need to provide the time in s, m, h (ex. 10s, 20m)** ||and make sure its not negative||", mention_author=False)
        elif t == -2:
            await ctx.reply("**You didnt enter a number properly... Try again next time with a number!**", mention_author=False)
        elif reason == None:
            await ctx.reply("**You need to provide a reason for your reminder after the time...**", mention_author=False)
        else:
            if dm is True:
                msg = await ctx.reply(f"**Okay!, I will remind you in {duration} for the reason you gave!**", mention_author=False)
                await asyncio.sleep(t)
                return await ctx.author.send(f"**Reminder!, I reminded you in time, woosh!**:\n> {reason}")
            else:
                msg = await ctx.send(f"Okay {ctx.author.mention} in {humanize.naturaldelta(t, minimum_unit='milliseconds')}, {reason}", allowed_mentions=discord.AllowedMentions(roles=False, users=True, everyone=False))
                start = time.perf_counter()
                await asyncio.sleep(t)
                end = time.perf_counter()
                ago = (end - start) * 1
                await ctx.send(f"{ctx.author.mention} {humanize.naturaltime(ago)}\n{reason}\n{ctx.message.jump_url}", allowed_mentions=discord.AllowedMentions(roles=False, users=True, everyone=False))


    @commands.command(name='bug-report', help="Report's a bug to Kyro's developer")
    @commands.cooldown(1,5,commands.BucketType.user)
    async def report(self, ctx, *, bug=None):
            if bug == None:
                return await ctx.send("**<:red_cross:844165297538727956> | Provide a bug to report!**")
            guild = ctx.guild
            channels = self.bot.get_all_channels()
            log_channel = get(channels, guild__name='Kyro Support', name="reports-log")
            embed = discord.Embed(title="Are you sure you want to report this bug?", description=f"{bug}", color=discord.Color.random())
            embed.set_footer(text=f" | Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
            msg = await ctx.send(embed=embed)
            timeout = int(15.0)
            await msg.add_reaction("✅")
            await msg.add_reaction("❌")
 
            def check(reaction, user):
               return user == ctx.author and str(reaction.emoji) == '✅'

            try: 
                reaction, user = await self.bot.wait_for('reaction_add', timeout=timeout, check=check)

            except asyncio.TimeoutError:
                 msg1=("**You timed out :stopwatch:**") 
                 return await ctx.channel.send(msg1)
                
            await ctx.send(f'**<:green_tick:844165352610725898> | Bug Reported to Kyro\'s developers!**')
            report = discord.Embed(title='New Bug Reported!', description=f'**{bug}**')
            report.add_field(name='Guild', value=f'{guild}')
            report.add_field(name='Reported By', value=f'{ctx.author.mention}')
            report.set_footer(text=f" | ID: {ctx.author.id}",icon_url=ctx.author.avatar.url)
            await log_channel.send(embed=report)

    @commands.group(aliases=['search'], invoke_without_command=True, help="Searches a given query to google")
    @commands.cooldown(1,5,commands.BucketType.user)
    async def google(self, ctx, *, search=None):
        if search is None:
            return await ctx.send("**Provide a something to search on google**")
        async with ctx.typing():
            if ctx.channel.is_nsfw():
                safe_search_setting=False
            else:
                safe_search_setting=True
            value=0
            results = await google.search(str(search), safesearch=safe_search_setting)
            embed=discord.Embed(
                title=f"Google Results for: **{search}**",
                color=discord.Color.random()
            )
            embed.set_footer(text=f"| Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
            for result in results:
                if not value > 4:
                    final = results[int(value)]
                    embed.add_field(
                        name=f" \uFEFF",
                        value=f"**[{str(final.title)}]({str(final.url)})**\n{str(final.description)}\n\n",
                        inline=False
                    )
                    value+=1
        await ctx.reply(embed=embed, mention_author=False)

    @google.command()
    @commands.cooldown(1,10,commands.BucketType.user)
    async def image(self,ctx,*, search):
        if search is None:
            return await ctx.send("**Provide a something to search on google**")
        if ctx.channel.is_nsfw():
            safe_search_setting=False
        else:
            safe_search_setting=True

        try:
            results = await google.search(search, safesearch=safe_search_setting, image_search=True)
        except async_cse.NoResults:
            return await ctx.send(f"I couldn't find any results for `{search}`")

        images = []
        for res in results:
            if isImage(res.image_url):
                images.append(res)
        if images != [] and len(images) != 0:
            embeds = []
            for res in images:
                em=discord.Embed(description=f"[{res.title}]({res.url})", color=discord.Color.random())
                em.set_footer(text=f"| Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
                em.set_image(url=res.image_url)
                embeds.append(em)
            pag = menus.MenuPages(Paginator(embeds, per_page=1))
            await pag.start(ctx)
        else:
            await ctx.send(f'No images found for `{search}`')

    @commands.command(aliases=['dictionary'], help="Searches the defenition of a word in urbandictionary")
    @commands.cooldown(1,5,commands.BucketType.user)
    async def urban(self, ctx, *, word):
       async with aiohttp.ClientSession() as ses:
         async with ses.get("http://api.urbandictionary.com/v0/define", params={"term": word}) as res:
           try: 
            res = await res.json()
            if res["list"] != [] and len(res["list"]) != 0:
              embeds = []
              for i in res["list"]:
                  if len(embeds) > 9:
                      break
                  res = i
                  definition = res["definition"].replace("[", "").replace("]", "")
                  permalink = res["permalink"]
                  author = res["author"]
                  example = res["example"].replace("[", "").replace("]", "")
                  word = res["word"]
                  em=discord.Embed(title=word, description=f"""
                  **Definition**:
  {definition}\n**Example**:
  {example}""", url=permalink, color=discord.Color.random())
                  em.set_footer(text=f"| Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
                  embeds.append(em)
              pag = menus.MenuPages(Paginator(embeds, per_page=1))
              await pag.start(ctx)
              await ses.close()
            else:
              await ses.close()
              await ctx.reply(f"**<:red_cross:844165297538727956> | No results for {word} found**", mention_author=False)

           except KeyError:
             await ctx.reply(f"**<:red_cross:844165297538727956> | No results for {word} found**",  mention_author=False)

  

    @commands.command(help="Give's you information on a emoji")
    @commands.cooldown(1,5,commands.BucketType.user)
    async def emojistats(self, ctx, emoji: discord.PartialEmoji = None):
        if not emoji:
          return await ctx.reply('**<:red_cross:844165297538727956> | Provide a valid emoji!**', mention_author=False)
        elif isinstance(emoji, discord.PartialEmoji):
            embed=discord.Embed(title=emoji.name, description=str(emoji.url), color=discord.Color.blurple())
            embed.add_field(
                name="Created At",
                value=f"{emoji.created_at.strftime('%d/%m/%Y at %H:%M:%S')}",
                inline=True
            )
            
            
            embed.set_thumbnail(url=str(emoji.url)+"?size=1024")
            embed.set_footer(text=f"| Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
            await ctx.reply(embed=embed, mention_author=False)


    @emojistats.error
    async def emojistats_error(self, ctx, error):
      if isinstance(error, commands.PartialEmojiConversionFailure):
            await ctx.reply(f"**<:red_cross:844165297538727956> | Emoji not found!**", mention_author=False)
      else:
        raise error



    @commands.command(help="Give's you a activity idea to do")
    @commands.cooldown(1,5,commands.BucketType.user)
    async def bored(self, ctx):
        async with aiohttp.ClientSession() as ses:
         async with ses.get("https://www.boredapi.com/api/activity") as res:
            res = await res.json()
            if res["link"] != "":
              embed=discord.Embed(title="Bored? Here is something you can do!", description=res["activity"], color=discord.Color.random(), url=res["link"])
              await ctx.send(embed=embed)
              await ses.close()
            else:
              embed=discord.Embed(title="Bored? Here is something you can do!", description=res["activity"], color=discord.Color.random())
              await ctx.send(embed=embed)
              await ses.close()


    @commands.command(help="Give's the bot's current uptime")
    @commands.cooldown(1,5,commands.BucketType.user)
    async def uptime(self, ctx):

      delta_uptime = datetime.utcnow() - self.bot.launch_time
      hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
      minutes, seconds = divmod(remainder, 60)
      days, hours = divmod(hours, 24)

      embed = discord.Embed(description=f'**Kyro has been up for**:\n{days}d {hours}h {minutes}m {seconds}s\nOnline since: {discord.utils.format_dt(self.bot.launch_time)}',  color=discord.Color.random())
      embed.set_author(name='Uptime of Kyro', icon_url=self.bot.user.avatar.url)
      embed.set_footer(text=f'| Requested by {ctx.author.name}', icon_url=ctx.author.avatar.url)
      await ctx.send(embed=embed)



    @commands.command(help="Searches discord.py docs for a given search")
    @commands.cooldown(1,5,commands.BucketType.user)
    async def rtfm(self, ctx, search=None):
      async with aiohttp.ClientSession() as ses:
        async with ses.get(f"https://idevision.net/api/public/rtfm?query={search}&location=https://discordpy.readthedocs.io/en/latest&show-labels=false&label-labels=false") as res:
          res = await res.json()
          nodes = res["nodes"]
        if nodes != {}:
            embed=discord.Embed(description="\n".join(f"[`{e}`]({nodes[e]})" for e in nodes), color=discord.Color.blurple())
            await ctx.send(embed=embed)
        else:
            await ctx.send(f'Couldn\'t find anything for {search}')
            
    @commands.command(help="Credit's the people who helped to build this bot")
    @commands.cooldown(1,5,commands.BucketType.user)
    async def credits(self,ctx):
        embed = discord.Embed(title='Credits for Kyro', description="""**People who helped build this bot and helped test it**\n\n**You can click on the names to get a invite for their bot/to access their GitHub account**
       
        MrArkon - Design of the help command - They own Liam Bot (currently cannot be invited)
        
        [Jotte](https://discord.com/oauth2/authorize?client_id=845720048668114977&permissions=8&scope=bot) - Their bot insipred me to make many commands - [They own Wakeful](https://discord.com/oauth2/authorize?client_id=845720048668114977&permissions=8&scope=bot)
        
        [</Rudransh Joshi>](https://github.com/FireHead90544) - Helped with many commands
        
        [AnshAg0007](https://github.com/AnshAg2007) - Helped with many commands """, color=discord.Color.random())
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        await ctx.reply(embed=embed, mention_author=False)
        
    @commands.command(help="Give's you information about this bot's code")
    @commands.cooldown(1,5,commands.BucketType.user)
    async def codestats(self, ctx):
            total = 0
            comments = 0
            classes = 0
            imports = 0
            file_amount = 0
            functions = 0
            for path, subdirs, files in os.walk('.'):
                for name in files:
                        if name.endswith('.py'):
                            file_amount += 1
                            with codecs.open('./' + str(pathlib.PurePath(path, name)), 'r', 'utf-8') as f:
                                for i, l in enumerate(f):
                                    if l.strip().startswith('#') or len(l.strip()) == 0:
                                        comments += 1
                                    elif l.strip().startswith(('import', 'from')) or len(l.strip()) == 0:
                                        imports += 1
                                    elif l.strip().startswith('class') or len(l.strip()) == 0:
                                        classes += 1
                                    elif l.strip().startswith(('def', 'async def')) or len(l.strip()) == 0:
                                        functions += 1
                                    else:
                                        total += 1
            linesofcode = total + functions + classes + imports
            embed = discord.Embed(description=f"**Lines of Code**: {linesofcode:,}\n**Commented Lines:** {comments:,}\n**Python Files:** {file_amount:,}\n**Imports:** {imports:,}\n**Classes:** {classes:,}\n**Functions:** {functions:,}\n\n**Python Version:** 3.8.9\n**Discord.py Version:** 2.0\n**Asyncpg Version:** 0.23.0 \n**Aiohttp Version:** 3.7.4", color=0x00FFB3)
            await ctx.send(embed=embed)
       
    @commands.command(help="Give's you weather info on a city")
    @commands.cooldown(1,5,commands.BucketType.user)
    async def weather(self, ctx,  *, city=None):
      if city == None:
        return await ctx.reply('**<:red_cross:844165297538727956> | You need to provide a city!**', mention_author=False)
      try: 
        key = objects["WEATHER_API_KEY"]
        async with aiohttp.ClientSession() as ses:
            async with ses.get(f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&APPID={key}") as r:
                data = await r.json()
                cleared_data = {
                      'Location:': data['name'],
                      'Weather:': f"{data['weather'][0]['main']} - {data['weather'][0]['description']}",
                      'Temperature:': f"{int((float(data['main']['temp']) * 1.8) + 32)}°F ({int((float(data['main']['temp'])))}°C)",
                      'Feels like:': f"{int((float(data['main']['feels_like']) * 1.8) + 32)}°F",
                      'Sunset:': datetime.utcfromtimestamp(data['sys']['sunset']).strftime('%H:%M:%S'),
                      'Sunrise:': datetime.utcfromtimestamp(data['sys']['sunrise']).strftime('%H:%M:%S'),
                  }
                embed = discord.Embed(title=f"Weather in: {cleared_data['Location:']}", color=discord.Color.random())
                for key, value in cleared_data.items():
                    embed.add_field(name=key, value=value, inline="True")
                await ctx.send(embed=embed)
      except KeyError:
        await ctx.reply(f'**<:red_cross:844165297538727956> | Location {city} Not Found**', mention_author=False)
 


    @commands.group(help="Give's you covid information on a country or continent")
    @commands.cooldown(1,5,commands.BucketType.user)
    async def covid(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.reply("**<:red_cross:844165297538727956> | Please use a valid Option `All`, `Country`, `Continent`**", mention_author=False)


    @covid.group(help= 'Gets information of Covid-19 stats of a country')
    async def country(self, ctx, country1=None):
       if country1 == None:
         return await ctx.reply('**<:red_cross:844165297538727956> | You need to Provide a valid country!`**')
       url = f'https://disease.sh/v3/covid-19/countries/{country1}'
       async with ClientSession() as session:
           async with session.get(url) as response:
                html = await response.json()
                data = [html]

                test = data[0]["countryInfo"]["flag"]
                population = data[0]["population"]
                population_format = format(population, ",")
                country = data[0]["country"]
                cases = data[0]["cases"]
                cases_format = format(cases, ",")
                deaths = data[0]["deaths"]
                deaths_format = format(deaths, ",")
                active = data[0]["active"]
                active_format = format(active, ",")
                recovered = data[0]["recovered"]
                recovered_format = format(recovered, ",")
                critical = data[0]["critical"]
                critical_format = format(critical, ",")
                tests = data[0]["tests"]
                tests_format = format(tests, ",")



                fatality = deaths/cases*100
                fatality_rounded_value = round(fatality, 4)
                fatality_rate_percent = "{}%".format(fatality_rounded_value)

                infected = cases/population*100
                infected_format = round(infected, 4)
                infected_rate_percent = "{}%".format(infected_format)

                critical_rate = critical/active*100
                critical_rate_round = round(critical_rate, 4)
                critical_rate_percent = "{}%".format(critical_rate_round)


                recovered_rate = recovered/cases*100
                recovered_rate_format = round(recovered_rate, 4)
                recovered_rate_percent = "{}%".format(recovered_rate_format)

                test_rate = tests/population*100
                test_rate_format = round(test_rate, 4)
                test_rate_percent = "{}%".format(test_rate_format)


                embed = discord.Embed(title=f'Covid Details: {country}', color = discord.Color.random())
                embed.set_thumbnail(url=test)
                embed.add_field(name='Total Cases', value=cases_format + '\u200b', inline=True)
                embed.add_field(name='Total Deaths', value=deaths_format, inline=True)
                embed.add_field(name='Active', value=active_format, inline=True)
                embed.add_field(name='Recovered', value=recovered_format, inline=True)
                embed.add_field(name='Critical', value=critical_format, inline=True)
                embed.add_field(name='Tests', value=tests_format, inline=True)
                embed.add_field(name='Population', value=population_format, inline=True)
                embed.add_field(name='Infection Rate', value=infected_rate_percent, inline=True)
                embed.add_field(name='Fatality Rate', value=fatality_rate_percent, inline=True)
                embed.add_field(name='Critical Rate', value=critical_rate_percent, inline=True)
                embed.add_field(name='Recovery Rate', value=recovered_rate_percent, inline=True)
                embed.add_field(name='Test Rate', value=test_rate_percent, inline=True)
                embed.set_footer(text=f" | Requested By {ctx.author.name}", icon_url=ctx.author.avatar.url)
                await ctx.send(embed=embed)

    @covid.group(help= 'Gets Summary of All countries with Covid-19')
    async def all(self, ctx):
        url = f'https://disease.sh/v3/covid-19/all'
        async with ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                case = data['cases']
                cases_format = format(case, ",")

                population = data["population"]
                population_format = format(population, ",")

                deaths = data["deaths"]
                deaths_format = format(deaths, ",")

                active = data["active"]
                active_format = format(active, ",")

                recovered = data["recovered"]
                recovered_format = format(recovered, ",")

                critical = data["critical"]
                critical_format = format(critical, ",")

                tests = data["tests"]
                tests_format = format(tests, ",")

                infected_countries = data['affectedCountries']

                fatality = deaths/case*100
                fatality_rounded_value = round(fatality, 4)
                fatality_rate_percent = "{}%".format(fatality_rounded_value)

                infected = case/population*100
                infected_format = round(infected, 4)
                infected_rate_percent = "{}%".format(infected_format)

                critical_rate = critical/active*100
                critical_rate_round = round(critical_rate, 4)
                critical_rate_percent = "{}%".format(critical_rate_round)


                recovered_rate = recovered/case*100
                recovered_rate_format = round(recovered_rate, 4)
                recovered_rate_percent = "{}%".format(recovered_rate_format)

                test_rate = tests/population*100
                test_rate_format = round(test_rate, 4)
                test_rate_percent = "{}%".format(test_rate_format)


                embed = discord.Embed(title=f'All Covid Details ', color = discord.Color.random())
                embed.set_thumbnail(url='https://i2x.ai/wp-content/uploads/2018/01/flag-global.jpg')
                embed.add_field(name='Total Cases', value=cases_format + '\u200b', inline=True)
                embed.add_field(name='Total Deaths', value=deaths_format, inline=True)
                embed.add_field(name='Active', value=active_format, inline=True)
                embed.add_field(name='Recovered', value=recovered_format, inline=True)
                embed.add_field(name='Critical', value=critical_format, inline=True)
                embed.add_field(name='Tests', value=tests_format, inline=True)
                embed.add_field(name='Population', value=population_format, inline=True)
                embed.add_field(name='Infection Rate', value=infected_rate_percent, inline=True)
                embed.add_field(name='Fatality Rate', value=fatality_rate_percent, inline=True)
                embed.add_field(name='Critical Rate', value=critical_rate_percent, inline=True)
                embed.add_field(name='Recovery Rate', value=recovered_rate_percent, inline=True)
                embed.add_field(name='Test Rate', value=test_rate_percent, inline=True)
                embed.add_field(name='Infected Countries', value=infected_countries, inline=True)
                embed.set_footer(text=f" | Requested By {ctx.author.name}", icon_url=ctx.author.avatar.url)
                await ctx.send(embed=embed)

    @covid.group(help= 'Gets Summary of a continent with Covid-19')
    async def continent(self, ctx, continent=None):
      if continent == None:
         return await ctx.reply('**<:red_cross:844165297538727956> | You need to provide a valid continent`**')
      url = f'https://disease.sh/v3/covid-19/continents/{continent}'
      async with ClientSession() as session:
          async with session.get(url) as response:
                data = await response.json()

                case = data['cases']
                cases_format = format(case, ",")

                population = data["population"]
                population_format = format(population, ",")

                deaths = data["deaths"]
                deaths_format = format(deaths, ",")

                active = data["active"]
                active_format = format(active, ",")

                recovered = data["recovered"]
                recovered_format = format(recovered, ",")

                critical = data["critical"]
                critical_format = format(critical, ",")

                tests = data["tests"]
                tests_format = format(tests, ",")

                countries = data['countries']


                fatality = deaths/case*100
                fatality_rounded_value = round(fatality, 4)
                fatality_rate_percent = "{}%".format(fatality_rounded_value)

                infected = case/population*100
                infected_format = round(infected, 4)
                infected_rate_percent = "{}%".format(infected_format)

                critical_rate = critical/active*100
                critical_rate_round = round(critical_rate, 4)
                critical_rate_percent = "{}%".format(critical_rate_round)


                recovered_rate = recovered/case*100
                recovered_rate_format = round(recovered_rate, 4)
                recovered_rate_percent = "{}%".format(recovered_rate_format)

                test_rate = tests/population*100
                test_rate_format = round(test_rate, 4)
                test_rate_percent = "{}%".format(test_rate_format)


                embed = discord.Embed(title=f'Covid Details of {continent}', color = discord.Color.random())
                embed.set_thumbnail(url='https://i2x.ai/wp-content/uploads/2018/01/flag-global.jpg')
                embed.add_field(name='Total Cases', value=cases_format + '\u200b', inline=True)
                embed.add_field(name='Total Deaths', value=deaths_format, inline=True)
                embed.add_field(name='Active', value=active_format, inline=True)
                embed.add_field(name='Recovered', value=recovered_format, inline=True)
                embed.add_field(name='Critical', value=critical_format, inline=True)
                embed.add_field(name='Tests', value=tests_format, inline=True)
                embed.add_field(name='Population', value=population_format, inline=True)
                embed.add_field(name='Infection Rate', value=infected_rate_percent, inline=True)
                embed.add_field(name='Fatality Rate', value=fatality_rate_percent, inline=True)
                embed.add_field(name='Critical Rate', value=critical_rate_percent, inline=True)
                embed.add_field(name='Recovery Rate', value=recovered_rate_percent, inline=True)
                embed.add_field(name='Test Rate', value=test_rate_percent, inline=True)
                embed.add_field(name='Countries', value=countries, inline=True)
                embed.set_footer(text=f" | Requested By {ctx.author.name}", icon_url=ctx.author.avatar.url)

                await ctx.send(embed=embed)

    @commands.command(help="Searches up a given package in PyPi")
    @commands.cooldown(1,5,commands.BucketType.user)
    async def pypi(self,ctx, *, package=None):
        arrow = "<a:botarrow:854681262610841621>"
        if package is None:
            return await ctx.send("**You need to provide a package to search up on pypi**")
        try:
            async with aiohttp.ClientSession() as ses:
                async with ses.get(f"https://pypi.org/pypi/{package}/json") as res:
                    r = await res.json()
                    name = r["info"]["name"] 
                    creator = r['info']["author"] or "Not Available"
                    url = r["info"]["project_url"] or "Not Available"
                    summary = r["info"]["summary"] or "Not Available"
                    usage_license = r["info"]["license"] or "Not Available"
                    key_words = r["info"]["keywords"] or "Not Available"
                    try:
                        docs = r["info"]["project_urls"]["Documentation"] or "Not Available"
                    except Exception:
                        docs = "Not Available"
                    try:
                        web = r["info"]["project_urls"]["Homepage"] or "Not Available"
                    except Exception:
                        web = "Not Available"
                    await ses.close()
                    embed = discord.Embed(title=name, description=f"""
                    {summary}
                    
                    {arrow} **Author**: {creator}
                    {arrow} **Website**: {web}
                    {arrow} **Docs**: {docs}
                    {arrow} **Keywords** {key_words}
                    {arrow} **Licence**: {usage_license}
                    """, url=web, color=discord.Color.random())
                    embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/381963689470984203/814267252437942272/pypi.png')
                    await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none())
        except:
            e = discord.Embed(description='**Cannot find this package**', color=discord.Color.red())
            return await ctx.send(embed=e)

    @commands.command(help="Suggets a given feature to be added into Kyro")
    @commands.cooldown(1,10, commands.BucketType.user)
    async def suggest(self, ctx):
        embed = discord.Embed(description='**Please send a message with your suggestion or type `cancel` to cancel**', color=discord.Color.random())
        msg = await ctx.send(embed=embed)
        try:
            suggestion = await self.bot.wait_for("message", check=lambda msg: msg.channel == ctx.channel and msg.author == ctx.author, timeout=40)
        except asyncio.TimeoutError:
            await ctx.send("**You took too long, timed out :stopwatch:**")
        else:
               if suggestion.content.lower() != 'cancel':
                       async with aiohttp.ClientSession() as ses:
                           webhook = Webhook.from_url(objects["LOGS_WEBHOOK"], adapter=AsyncWebhookAdapter(ses))
                           em = discord.Embed(title='New Suggestion', description=f"{suggestion.clean_content}", color=discord.Color.random())
                           em.add_field(name='Suggested by', value=f'{ctx.author.name} (ID: {ctx.author.id})')
                           em.add_field(name='Guild', value=ctx.guild)
                           await webhook.send(embed=em)
                           await ses.close()
                           await msg.delete()
                           await suggestion.add_reaction("<:green_tick:844165352610725898>")
               else:
                   await msg.delete()
                   await suggestion.add_reaction("<:red_cross:844165297538727956>")
                   




    @commands.command(help="Give's information about a given user or member", aliases=['whois'])
    @commands.cooldown(1,5,commands.BucketType.user)
    async def userinfo(self,ctx, member:typing.Union[discord.Member, discord.User]=None):
        if member is None:
            member = ctx.author 
        acc_created = discord.utils.format_dt(member.created_at)
        if isinstance(member, discord.User):
            embed = discord.Embed(description=f'**Information**\n**User ID**: {member.id}', color=discord.Color.random())
            embed.set_author(name=member, icon_url=member.avatar.url)
            embed.set_thumbnail(url = member.avatar.url)            
            embed.add_field(name='User Avatar', value=f'[Link]({member.avatar.url})')
            embed.add_field(name='Created At', value=humanize.naturaltime(acc_created), inline=False)
            embed.set_footer(text=f'Requested by {ctx.author.name}', icon_url=ctx.author.avatar.url)
            return await ctx.send(embed=embed)
        elif isinstance(member, discord.Member):
        

            if member.top_role.name == '@everyone':
                top_role = "Not Found"
            else:
                top_role = member.top_role.mention
        

#             badges = dict(member.public_flags)
#             user_badges = []
#             for x,y in badges.items():
#                 if y:
#                     user_badges.append(x)

#             em_badges = {
#                 "hypesquad_brilliance": "<:brilliance:866686255038070895>",
#                 "hypesquad_balance": "<:balance:866686365802823710>",
#                 "hypesquad_bravery": "<:bravery:866686455483859035>",
#                 "bug_hunter_level_2": "<:bughunter:866686616839651339>",
#                 "verified_bot_developer": "<:developer:866686546677596160> "
            
#             }
#             mem_badgets = []

            joined_guild = discord.utils.format_dt(member.joined_at)

#             for i in user_badges:
#                 if 'hypesquad_balance' in i:
#                     b = em_badges["hypesquad_balance"]
#                     mem_badgets.append(b)
#                 elif 'hypesquad_brilliance' in i:
#                     b = em_badges['hypesquad_brilliance']
#                     mem_badgets.append(b)
#                 elif 'hypesquad_bravery' in i:
#                     b = em_badges["hypesquad_bravery"]
#                     mem_badgets.append(b)
#                 elif "verified_bot_developer" in i:
#                     b = em_badges["verified_bot_developer"]
#                     mem_badgets.append(b)
            
#             try:
#                 u_badges = mem_badgets[0]
#             except IndexError:
#                 u_badges = "None"
                         
            
            embed = discord.Embed(description=f'**Information**\n**User ID**: {member.id}', color=member.top_role.color)
            embed.set_author(name=member, icon_url=member.avatar.url)
            embed.set_thumbnail(url = member.avatar.url)            
            embed.add_field(name='User Avatar', value=f'[Link]({member.avatar.url})')
            embed.add_field(name='Highest Role', value=top_role, inline=False)
            embed.add_field(name='Role(s)', value=len(member.roles), inline=False)
            embed.add_field(name='Created At', value=humanize.naturaltime(acc_created), inline=False)
            embed.add_field(name='Joined At', value=humanize.naturaltime(joined_guild))
            embed.set_footer(text=f'Requested by {ctx.author.name}', icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)

    @commands.command(help="Check's the time in a given timezone")
    @commands.cooldown(1,5,commands.BucketType.user)
    async def clock(self, ctx, *, timezone=None):
       try:
            tzs = pytz.timezone(timezone)
       except KeyError:
            return await ctx.send("An error occured, are you sure the timezone is valid? Valid Timezones are: <https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568>")
       t = datetime.now(tzs)
       ft = t.strftime("%A, %B %d • %I:%M %p")
       embed = discord.Embed(description=ft, color=discord.Color.random())
       embed.set_author(name=f'Time in {timezone}', icon_url=ctx.author.avatar.url)
       embed.set_footer(text=timezone)
       await ctx.reply(embed=embed)
    
    
    @commands.command(name='time', help="Give's your time or a member's time, given that they have set their time up first.")
    @commands.cooldown(1,5, commands.BucketType.user)
    async def tz(self, ctx, *, member:discord.Member=None):
        if member is None:
            member = ctx.author
        res = await self.bot.db.fetchrow("SELECT time FROM times WHERE user_id = $1", member.id)
        if res is None:
            if member is ctx.author:
                return await ctx.send(f"Looks like you dont have a timezone set up, you can set it up using `{ctx.prefix}set-time <timezone>`")
            else:
                return await ctx.send(f"Looks like that user doesnt have a timezone set up, you can set it up using `{ctx.prefix}set-time <timezone>`")
        t  = res["time"]
        timezone = pytz.timezone(t)
        tz = datetime.now(timezone)
        ft = tz.strftime("%A, %B %d • %I:%M %p")
        embed = discord.Embed(description=ft, color=discord.Color.random())
        embed.set_author(name=member.name, icon_url=member.avatar.url)
        embed.set_footer(text=timezone)
        await ctx.reply(embed=embed)
    
    @commands.command(name='set-time', help="Set's your timezone, people can now find it using the time command")
    @commands.cooldown(1,5,commands.BucketType.user)
    async def settime(self, ctx, *, timezone):
        if ctx.message.content.endswith('--help'):
            embed = discord.Embed(title='Finding your timezone.', description='To find your timezone, take a look in: <https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568>\nThose are the only available timezones in this command.', color=discord.Color.random())
            return await ctx.send(embed=embed)
        try:
            tzs = pytz.timezone(timezone)
        except KeyError:
            return await ctx.send("An error occured, are you sure the timezone is valid? Valid Timezones are: <https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568>")
        check = await self.bot.db.fetchrow("SELECT time FROM times WHERE user_id = $1", ctx.author.id)
        if check is None:
            await self.bot.db.execute("INSERT INTO times (time, user_id) VALUES ($1, $2)", timezone, ctx.author.id)
            return await ctx.send(f"Your timezone has been set to {tzs}")
        res = await self.bot.db.execute("UPDATE times SET time = $1 WHERE user_id = $2", timezone, ctx.author.id)
        await ctx.send(f"Your timezone has been set to {tzs}")
        
    @commands.command(help="Pins a message in your DMs, you can use the remind flag to be reminded about it in a given time, eg: remind:10, this will remind you in 10 seconds, make sure to put the flag at the end of the message or it will not work")
    @commands.cooldown(1,5,commands.BucketType.user)
    async def arch(self, ctx, message:typing.Optional[discord.Message], flag:ArchFlag=None):
        if message is None:
            if ctx.message.reference:
                message = ctx.message.reference.resolved
            else:
                return await ctx.send('Reply to a message or provide a message URL that you want to pin.')
        embed = discord.Embed(title='Pinned Message', description=f'{message.content}', color=discord.Color.random())
        embed.add_field(name='Message URL', value=f'[URL]({message.jump_url})')
        embed.add_field(name='Guild', value=message.guild.name, inline=False)
        embed.set_author(icon_url=message.author.avatar.url, name=message.author)
        await ctx.author.send(embed=embed)
        await ctx.send('👌 Done!')
        if flag:
            await asyncio.sleep(flag.remind)
            await ctx.author.send(f'👌 Reminding You.\n{ctx.message.jump_url}')


        

    @commands.command(help="Run's a given code.")
    @commands.cooldown(1,50,commands.BucketType.user)
    async def run(self, ctx, language=None, *, code: codeblock_converter=None):
        if language is None:
            return await ctx.send(F"**<:red_cross:844165297538727956> | You need to provide a coding language. | `{ctx.prefix}run (language) (code)` is the correct syntax**")
        if code is None:
            return await ctx.send(F"**<:red_cross:844165297538727956> | You need to provide code to run. | `{ctx.prefix}run (language) (code)` is the correct syntax**")
        res = (code.content
            .replace("{author.name}", ''.join(ctx.author.name if ctx.author.name is not None else "None"))
            .replace("{author.id}", ''.join(str(ctx.guild.id) if str(ctx.guild.id) is not None else "None"))
            .replace("{author.nick}", ''.join(ctx.author.nick if ctx.author.nick is not None else "None"))
            .replace("{server.name}", ''.join(ctx.guild.name if ctx.guild.name is not None else "None"))
            .replace("{server.members}", ''.join(str(ctx.guild.member_count) if str(ctx.guild.member_count) is not None else "None"))
            .replace("{channel.name}", ''.join(ctx.channel.name if ctx.channel.name is not None else "None"))
            .replace("{channel.topic}", ''.join(ctx.channel.topic if ctx.channel.topic is not None else "None"))
            .replace("{bot.http.token}", ''.join('a token'))
            .replace("{bot.token}", ''.join('a token')))
        m = await ctx.send('<a:processing:857872778812325931> | **Your code is being processed.**')
        tio = await async_tio.Tio()
        res = await tio.execute(res, language=language)
        await tio.close()
        if len(res.stdout) > 100:
            await ctx.message.add_reaction('<:green_tick:844165352610725898>')
            await asyncio.sleep(1)
            await m.delete()
            code = await mystin_client.post(res.stdout, syntax=language)
            link = str(code)
            await ctx.send(f'Output was too long to display, view it here: {link}', allowed_mentions=discord.AllowedMentions.none())
        else:
            await ctx.message.add_reaction('<:green_tick:844165352610725898>')
            await asyncio.sleep(1)
            await m.delete()
            await ctx.trash(f"```\n{res.stdout}\nExit Code: {res.exit_status}```",  allowed_mentions=discord.AllowedMentions.none())

    @commands.command(aliases=['sys'])
    @commands.cooldown(1,5,commands.BucketType.user)
    @commands.is_owner()
    async def system(self, ctx):
        proc = psutil.Process()
        with proc.oneshot():
                cpu = psutil.cpu_percent(interval=None)
                usage = f"{cpu}%"
                freq = psutil.cpu_freq(percpu=False)
                cores = psutil.cpu_count()
                vm = psutil.virtual_memory()
                ram = vm.percent
                r_used = humanize.naturalsize(vm.used)
                totalram = humanize.naturalsize(vm.total)
                available = humanize.naturalsize(vm.available)
        embed = discord.Embed(title='System Information', color=discord.Color.random())
        embed.add_field(name='CPU Info', value=f'```yaml\nCPU Usage: {usage}\nCPU Cores: {cores}\nFrequency: {freq.current} Mhz\n```')
        embed.add_field(name='Memory Info', value=f'```yaml\nRAM Used: {r_used} or {ram}%\nTotal RAM: {totalram}\nAvailable RAM: {available}\n```')
        await ctx.send(embed=embed)








def setup(bot):
    bot.add_cog(Utility(bot))

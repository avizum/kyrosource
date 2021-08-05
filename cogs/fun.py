from re import A
from typing import Optional
import discord
from discord.embeds import Embed
from discord.ext import commands
# from discord_components import *
import os
import json
from discord.ext.commands.cooldowns import BucketType
from requests import get 
from datetime import datetime
from aiohttp import ClientSession
from pathlib import Path
import typing
import io
from io import BytesIO
from requests.api import options
from jishaku.functools import executor_function
from cogs.image import dagpi as image_dagpi
import asyncio
import time
import io
import json
from typing import List
import random
from aiogtts import aiogTTS
import aiohttp
import asyncio
import pytz
from akinator.async_aki import Akinator

akin = Akinator()


snipe_message_author = {}
snipe_message_content = {}
edit_message_author = {}
edit_message_content_after = {}
edit_message_content_before = {}


class EmbedBuilder(commands.FlagConverter, case_insensitive=True):
    title: str
    description: str
    color: Optional[typing.Union[discord.Color, int]]
    author: Optional[str]
    field: Optional[str]
    value: Optional[str]


class PollBuilder(commands.FlagConverter, case_insensitive=True):
    title: str
    question: str
    question2: Optional[str]
    question3: Optional[str]
    question4: Optional[str]
    question5: Optional[str]

@executor_function
def getFile(text, end = "txt", filename="message"):
    f = io.StringIO()
    f.write(text)
    f.seek(0)
    return discord.File(f, filename=f"{filename}.{end}")

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, msg):
        pass

    @commands.command(help='Show\'s a minecraft death message')
    @commands.cooldown(1,5,commands.BucketType.user)
    async def mckill(self, ctx, member: discord.Member=None):

      if member == None:
        return await ctx.send("**<:red_cross:844165297538727956> | You need to provide a member to MC Kill**")

      choices = ['was pricked to death', 'drowned', 'experienced kinetic energy', 'hit the ground too hard', 'fell from a high place', 'fell off a ladder', ' was squashed by a falling anvil', 'went up in flames', 'burned to death', 'tried to swim in lava', 'discovered the floor was lava', 'was killed by magic', 'starved to death', 'suffocated in a wall', 'was poked to death by a sweet berry bush', 'fell out of the world', 'withered away', 'blew up', 'was killed by [Intentional Game Design]', f'didn\'t wanted to live in the same world as **{ctx.author.name}**']
      choice = random.choice(choices)
      await ctx.send(f'**{member}** {choice}')

    @mckill.error
    async def mckill_error(self, ctx, error):
      if isinstance(error, commands.MemberNotFound):
         await ctx.send("**<:red_cross:844165297538727956> | No valid member was provided!**")
      else:
        raise error

    @commands.command(help='Show\'s a member\'s avatar')
    @commands.cooldown(1,5,commands.BucketType.user)
    async def avatar(self, ctx, member: discord.Member = None):
        if member == None:
          member = ctx.author
        embed = discord.Embed(title=f"{member.name}'s avatar", color=0xff0000)
        embed.set_image(url=member.avatar.url)
        await ctx.send(embed=embed)
        
            

    @commands.command(help='Makes a emoji bigger')
    @commands.cooldown(1,5,commands.BucketType.user)
    async def bigmoji(self, ctx, emoji: discord.PartialEmoji = None):
      if emoji == None:
        return await ctx.send("**<:red_cross:844165297538727956> | You need to provide a valid emoji!**")
      url = str(emoji.url)
      await ctx.send(url)
    
    @bigmoji.error
    async def bigmoji_error(self, ctx, error):
      if isinstance(error, commands.PartialEmojiConversionFailure):
            embed = discord.Embed(description="**<:red_cross:844165297538727956> | Please Provide a valid emoji**", color=0xff0000)
            await ctx.send(embed=embed)
      else:
        raise error

      

    @commands.command(help='Tells a funny joke')
    @commands.cooldown(1,5,commands.BucketType.user)
    async def joke(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(
                    'https://official-joke-api.appspot.com/random_joke') as r:
                res = await r.json()

            arg1 = res['setup']
            arg2 = res['punchline']

            await ctx.reply(f"**{arg1}**\n\n||{arg2}||", mention_author=False)
            
    @commands.command(help='Writes text in ascii')
    @commands.cooldown(1,5,commands.BucketType.user)
    async def ascii(self, ctx, *, raw_text=None):
        if raw_text == None:
            return await ctx.reply("**Don't you need some text to ascii ||Hiro will be mad at you bruh||**")
        elif len(raw_text) > 13:
            return await ctx.reply("**The Text Cannot be above 13 characters coz its ascii bro!**")
        text = raw_text.replace(" ", "+")
        async with aiohttp.ClientSession() as cs:
            async with cs.get(
                    f'https://artii.herokuapp.com/make?text={text}') as r:
                res = await r.text()
            
            embed = discord.Embed(description=f"```\n{res}```", color=discord.Color.random())
            embed.set_footer(text=f"Requested by {ctx.author.name}"  ,icon_url=ctx.author.avatar.url)
            await ctx.reply(embed=embed, mention_author=False)
            
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def msgreq(self, ctx, message: discord.Message = None):
        choices = ['every message is formed with something like this', 'this is how developers can use new features before they are in libraries', 'this is how all the bot magic happens', 'this is behind all messages by bots/users', 'sending too much of this can cause you to get ratelimited! be careful!']
        choice = random.choice(choices)
        if ctx.message.reference:
            msg = await self.bot.http.get_message(int(ctx.message.reference.channel_id), int(ctx.message.reference.message_id))
        elif message:
            msg = await self.bot.http.get_message(int(message.channel.id), int(message.id))
        else:
            msg = await self.bot.http.get_message(int(ctx.channel.id), int(ctx.message.id))
        raw = json.dumps(msg, indent=4)
        embed=discord.Embed(
            description=f"```json\n{discord.utils.escape_markdown(raw)}```",
            color=discord.Color.random()) 
        embed.set_author(name=f"That message if decoded is...", icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f'Fun Fact about discord requests: {choice}')
        if len(embed.description) < 2048:
            await ctx.send(embed=embed)
        else:
            file = await getFile(raw, "json")
            await ctx.reply(file=file, mention_author=False)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
       try: 
        snipe_message_author[message.channel.id] = message.author
        snipe_message_content[message.channel.id] = message.content
        await asyncio.sleep(60)
        del snipe_message_author[message.channel.id]
        del snipe_message_content[message.channel.id]

       except KeyError:
         return

    @commands.command(help='Snipes the last deleted message from the channel')
    @commands.cooldown(1,5,commands.BucketType.user)
    async def snipe(self, ctx):
        channel = ctx.channel
        try:
            em = discord.Embed(
                title=f"From {snipe_message_author[channel.id]}",
                description=
                f"**Message:**\n{snipe_message_content[channel.id]}\n\n **Channel:** {channel.name}",
                color=0x00ffff)
            em.set_footer(text=f" | Message sniped by {ctx.author.name}", icon_url=ctx.author.avatar.url)
            await ctx.send(embed=em)
            del snipe_message_content[channel.id]
            del snipe_message_author[channel.id]
        except:
            await ctx.send(f"**There is nothing to snipe!**")

    @commands.Cog.listener()
    async def on_message_edit(self, after, before):
      try:
        edit_message_author[after.channel.id] = after.author
        edit_message_content_before[after.channel.id] = after.content
        edit_message_content_after[after.channel.id] = before.content
        await asyncio.sleep(60)
        del edit_message_author[after.channel.id]
        del edit_message_content_after[after.channel.id]
        del edit_message_content_before[after.channel.id]

      except KeyError:
        return
    
    @commands.command(help='Snipes the last edited message from a channel')
    @commands.cooldown(1,5,commands.BucketType.user)
    async def editsnipe(self, ctx):
      channel = ctx.channel
      try:
            em = discord.Embed(
                title=f"From {edit_message_author[channel.id]}",
                description=
                f"**Before:**\n{edit_message_content_before[channel.id]}\n\n **After:**\n{edit_message_content_after[channel.id]} \n\n **Channel:** {channel.name}",
                color=0x00ffff)
            em.set_footer(text=f" | Message editsniped by {ctx.author.name}", icon_url=ctx.author.avatar.url)
            await ctx.send(embed=em)
            del edit_message_content_after[channel.id]
            del edit_message_content_before[channel.id]
            del edit_message_author[channel.id]
      except:
            await ctx.send(f"**No edited message to snipe**")


    @commands.command(help='Makes a poll people can vote on', usage='<flags | title: | question: | question2: | question3: | question4: | question5:>')
    @commands.cooldown(1,5,commands.BucketType.user)
    async def poll(self, ctx, *, args:PollBuilder):
      if not PollBuilder:
        return await ctx.send("**<:red_cross:844165297538727956> | You need to provide a question!**")
      
      if not args.question2:
        embed = discord.Embed(title=f"{args.title}", description=f"**{args.question}**\n\n:thumbsup:- **Yes** \n\n:thumbsdown:- **No**", color=discord.Color.random())
        embed.set_footer(text=f" | Poll Created By {ctx.author.name}", icon_url=ctx.author.avatar.url)
        msg = await ctx.send(embed=embed)
        await msg.add_reaction('👍')
        await msg.add_reaction('👎') 

      elif args.question2 and not args.question3 and not args.question4 and not args.question5:
        embed = discord.Embed(title=args.title, description=f"**{args.question}** - **1️⃣** \n\n**{args.question2}** - **2️⃣**", color=discord.Color.random())
        embed.set_footer(text=f" | Poll Created By {ctx.author.name}", icon_url=ctx.author.avatar.url)
        msg = await ctx.send(embed=embed)
        await msg.add_reaction('1️⃣')
        await msg.add_reaction('2️⃣') 

      elif args.question2 and args.question3 and not args.question4 and not args.question5:
        embed = discord.Embed(title=args.title, description=f"**{args.question}** - **1️⃣** \n\n**{args.question2}** - **2️⃣**\n\n**{args.question3}** - **3️⃣**", color=discord.Color.random())
        embed.set_footer(text=f" | Poll Created By {ctx.author.name}", icon_url=ctx.author.avatar.url)
        msg = await ctx.send(embed=embed)
        await msg.add_reaction('1️⃣')
        await msg.add_reaction('2️⃣') 
        await msg.add_reaction("3️⃣")

      elif args.question2 and args.question3 and args.question4 and not args.question5:
        embed = discord.Embed(title=args.title, description=f"**{args.question}** - **1️⃣** \n\n**{args.question2}** - **2️⃣**\n\n**{args.question3}** - **3️⃣**\n\n**{args.question4}** -**4️⃣**", color=discord.Color.random())
        embed.set_footer(text=f" | Poll Created By {ctx.author.name}", icon_url=ctx.author.avatar.url)
        msg = await ctx.send(embed=embed)
        await msg.add_reaction('1️⃣')
        await msg.add_reaction('2️⃣') 
        await msg.add_reaction("3️⃣")
        await msg.add_reaction("4️⃣")

      elif args.question2 and args.question3 and args.question4 and args.question5:
        embed = discord.Embed(title=args.title, description=f"**{args.question}** - **1️⃣** \n\n**{args.question}** - **2️⃣**\n\n**{args.question3}** - **3️⃣**\n\n**{args.question4}** -**4️⃣**\n\n**{args.question5}** -**5️⃣**", color=discord.Color.random())
        embed.set_footer(text=f" | Poll Created By {ctx.author.name}", icon_url=ctx.author.avatar.url)
        msg = await ctx.send(embed=embed)
        await msg.add_reaction('1️⃣')
        await msg.add_reaction('2️⃣') 
        await msg.add_reaction("3️⃣")
        await msg.add_reaction("4️⃣")
        await msg.add_reaction("5️⃣")
    



    @commands.command(help='Makes a embed, to use this command use the following flags after the command like this: title:<title> description:<description> color:<color(can be a hex code or a normal color(eg. green))> author:<Author (this flag is optional)> field:<feild name (this flag is optional)> value: <value of the field (this flag is optional)> ')
    @commands.cooldown(1,5,commands.BucketType.user)
    async def embed(self, ctx, *, EmbedFlags: EmbedBuilder):
        if not EmbedFlags.title:
            return await ctx.send("**<:red_cross:844165297538727956> | You need to provide the title and description of the embed you want to send!**")
        if not EmbedFlags.description:
            return await ctx.send("**<:red_cross:844165297538727956> | Please also provide the description of the embed!**")
        if not EmbedFlags.color:
            color = discord.Color.random()
        else:
            color = EmbedFlags.color
        embed = discord.Embed(title=EmbedFlags.title, description=EmbedFlags.description, color=color)
        if EmbedFlags.author:
            embed.set_author(name=EmbedFlags.author)
        if EmbedFlags.field and EmbedFlags.value:
            embed.add_field(name=EmbedFlags.field, value=EmbedFlags.value)
        embed.set_footer(text=f" | Embed Created By {ctx.author.name}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    @commands.command(help='Shows Pokemon card stats.')
    @commands.cooldown(1,5,commands.BucketType.user)
    async def pokedex(self, ctx, *, title):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(
                    f'https://some-random-api.ml/pokedex?pokemon={title}') as r:
                data = await r.json()

                name = data['name']
                pokeid = data['id']
                desc = data['description']
                poketype = data['type'][0]
                species = data['species'][0]
                image = data['sprites']['animated']
                ability = data['abilities']
                stage = data['family']['evolutionStage']
                line = data['family']['evolutionLine']
                height = data['height']
                weight = data['weight']
                gender = data['gender']

                stats1 = data['stats']['hp']
                stats2 = data['stats']['attack']
                stats3 = data['stats']['defense']
                stats4 = data['stats']['speed']
                sp_stats1 = data['stats']['sp_atk']
                sp_stats2 = data['stats']['sp_def']

                generation = data['generation']

                embed = discord.Embed(title=f"{name} #{pokeid}",
                                      description=f"🤖: ** {desc} ** ",
                                      color=discord.Colour.random())
                embed.add_field(name="Types:", value=f"{poketype}")
                embed.add_field(name="Species:", value=f"{species}, Pokémon")
                embed.add_field(name="Ability:",
                                value=", ".join(pog for pog in ability))
                embed.add_field(name="Evolution Stage:",
                                value=f"The {stage} Evolution",
                                inline=False)
                embed.add_field(name="Evolution Line:", value = ", ".join(pog for pog in line), inline=False)
                embed.add_field(name="Height:", value=f"{height}")
                embed.add_field(name="Weight:", value=f"{weight}")
                embed.add_field(name="Gender:", value = ", ".join(pog for pog in gender))
                embed.add_field(
                    name="Stats:",
                    value=f"❤️: {stats1}\n⚔️: {stats2}\n🛡️: {stats3}\n💨: {stats4}")
                embed.add_field(name="Stats:",
                                value=f"Sp ⚔️: {sp_stats1}\nSp 🛡️: {sp_stats2}")
                embed.set_footer(
                    text=f"This Pokémon is from Generation {generation}")
                embed.set_thumbnail(url=image)

                await ctx.send(embed=embed)

    @commands.command(name="8ball", help='Lets the bot decide on something')
    @commands.cooldown(1,5,commands.BucketType.user)
    async def eightball(self, ctx, *, question=None):

      if question == None:
       return await ctx.send("**<:seriously_what:848469841534517248> You need to provide a question what are you doing right now!**")

      choices = ['Definitely' ,'Yes.', 'Most Likely', 'Of Course', 'Doubtful', 'I cannot tell you right now', 'Maybe', 'Not 100% Sure', 'Kinda..', 'Duh, no', 'Nope!', 'How did you think, yes?', 'nonononono']
      responce = random.choice(choices)
      await ctx.reply(f":8ball: {responce}", mention_author=False)

    @commands.command(help='Ship\'s two members, the second member argument is not required and will automaticly be yourself')
    @commands.cooldown(1,5,commands.BucketType.user)
    async def ship(self, ctx, member1: discord.Member = None, member2: discord.Member = None):

      if member1 == None:
        return await ctx.send("**<:red_cross:844165297538727956> | Please Provide any 2 or 1 member(s) to ship!**")

      elif member1 == member2:
        return await ctx.send("**<:red_cross:844165297538727956> | Member1 can't be Member2, Please Provide another member to ship!**")
      
      elif member2 == None:
        if member1 == ctx.author:
          return await ctx.send('**<:red_cross:844165297538727956> | You cannot ship yourself**')
        else:
            member2 = ctx.author

      hearts = [':sparkling_heart:', ':heart:', ':heart_decoration:', ':hearts:']
      heartchoice = random.choice(hearts)
      num = random.randint(1, 100)
      len1 = len(member1.name) // 2
      len2 = len(member2.name) // 2 
      half1 = member1.name[len1:]
      half2 = member2.name[0:len2]

      colors = [0xff00c1, 0xff7fe0, 0xff61b3, 0xd521ff]
      cchoice = random.choice(colors)

      options = ['Married', 'not Married', 'in a Relationship', 'Broken Up', 'Just Friends']
      optionchoice = random.choice(options)
      embed = discord.Embed(title=f"{heartchoice} Rate: {num}% ", description=f"**{member1.name}** and **{member2.name}** are __**{optionchoice}**__", color=cchoice)
      embed.set_author(name=f"{member2.name} + {member1.name} = {half2}{half1}")
      await ctx.send(embed=embed)
      

    @commands.command(help='Gets the first message from the channel')
    @commands.cooldown(1,15,commands.BucketType.guild)
    async def firstmessage(self, ctx):
      async for message in ctx.channel.history(oldest_first=True, limit=1):
        url = message.jump_url
        embed = discord.Embed(title=message.content, description=f"**Link: {url}**",color=discord.Color.random())
        embed.set_author(name=f"{message.author.name} said...", icon_url=message.author.avatar.url)
        embed.add_field(name='Sent at', value=discord.utils.format_dt(message.created_at))
        embed.set_footer(text=f'| Requested by {ctx.author}', icon_url=ctx.author.avatar.url)
        await message.reply(embed=embed, mention_author=False)

    @commands.command(help='Does a *very real* hack to a member')
    @commands.cooldown(1,5,commands.BucketType.user)
    async def hack(self, ctx, member:discord.Member):
     if member == None:
      return await ctx.send("**Srsly you need to provide the member to hack because you cant hack yourself right??**")
     elif member == ctx.author:
      return await ctx.send("**Done hacked you, who next?**")
     domains = ['@gmail.com', '@outlook.com', '@69mail.com', '@hotmail.com', '@kyrop.com']
     domain = random.choice(domains)
     words = ['oop', 'ye', 'bad', 'i hate you', 'whoops', 'il nuke you', 'thicc']
     word = random.choice(words)
     revenue = random.randint(1,90000)
     locations = ['Asia', 'Europe', 'Mars ||wait what||', 'Australia ||k!flip||']
     location = random.choice(locations)
     color = 0x16C60C 
     embed = discord.Embed(description='[▗] Hacking now..', color=color)
     m = await ctx.send(embed=embed)
     await asyncio.sleep(5)
     embed = discord.Embed(description='[▗] Getting Access...', color=color)
     await m.edit(embed=embed)
     await asyncio.sleep(5)
     embed = discord.Embed(description='[▗] Getting email and password..', color=color)
     await m.edit(embed=embed)
     await asyncio.sleep(5)
     embed = discord.Embed(description=f'Email: {member.name}{domain}', color=color)
     await m.edit(embed=embed)
     await asyncio.sleep(5)
     embed = discord.Embed(description='[▗] Gettings DM\'s', color=color)
     await m.edit(embed=embed)
     await asyncio.sleep(5)
     embed = discord.Embed(description=f'DM\'s Found.. Most common word: {word}', color=color)
     await m.edit(embed=embed)
     await asyncio.sleep(5)
     embed = discord.Embed(description='[▗] Getting IP Address', color=color)
     await m.edit(embed=embed)
     await asyncio.sleep(5)
     embed = discord.Embed(description=f'IP Address Location found: {location}', color=color)
     await m.edit(embed=embed)
     await asyncio.sleep(5)
     embed = discord.Embed(description='[▗] Selling data to 3rd parties', color=color)
     await m.edit(embed=embed)
     await asyncio.sleep(5)
     if revenue > 10000:
       embed = discord.Embed(description=f'Data sold and made **{revenue}$**, thats some good money', color=color)
       await m.edit(embed=embed)
     else:
       embed = discord.Embed(description=f'Data sold and made **{revenue}$**, smh thats not alot of money', color=color)
       await m.edit(embed=embed)
     await asyncio.sleep(5.9)
     embed = discord.Embed(description='[▗] Finalizing the hack...', color=color)
     await m.edit(embed=embed)
     await asyncio.sleep(5)
     embed = discord.Embed(description=f'This very *real* hack to {member.name} has finished!', color=color)
     await m.edit(embed=embed)
        
    # @commands.command()
    # @commands.cooldown(1,5,commands.BucketType.user)
    # async def rps(self, ctx):
    #     embed = discord.Embed(title="Rock Paper Scissors!", description=":rock:: Rock\n\n:roll_of_paper:: Paper\n\n:scissors:: Scissors", color=0xff0000)
    #     msg = await ctx.send(embed=embed, components=[
    #             Button(style=ButtonStyle.green, label="Rock"),
    #             Button(style=ButtonStyle.green, label="Paper"),
    #             Button(style=ButtonStyle.green, label="Scissors")
    #         ])
    #     dis_components=[
    #             Button(style=ButtonStyle.green, label="Rock", disabled=True),
    #             Button(style=ButtonStyle.green, label="Paper", disabled=True),
    #             Button(style=ButtonStyle.green, label="Scissors", disabled=True)
    #         ]

    #     choice = random.choice(["Rock", "Paper", "Scissors"])

    #     while True:
    #         res = await self.bot.wait_for("button_click")
    #         if res.user==ctx.author:
    #             if res.component.label == "Rock" and choice == "Paper":
    #                 await res.respond(content="You choose **Rock** and i choose **Paper**, I win!!")
    #                 await msg.edit(embed=embed, components=dis_components)
    #             elif res.component.label == "Rock" and choice == "Scissors":
    #                 await res.respond(content="You choose **Rock** and i choose **Paper**, i lose to you!")
    #                 await msg.edit(embed=embed, components=dis_components)
    #             elif res.component.label == "Rock" and choice == "Rock":
    #                 await res.respond(content="You choose **Rock** and i choose **Rock** too! This match is a tie ||but i'll defeat you next time!||")
    #                 await msg.edit(embed=embed, components=dis_components)
    #             elif res.component.label == "Paper" and choice == "Scissors":
    #                 await res.respond(content="You choose **Paper** and i choose **Scissors**! I win!!")
    #                 await msg.edit(embed=embed, components=dis_components)
    #             elif res.component.label == "Paper" and choice == "Rock":
    #                 await res.respond(content="You choose **Paper** and i choose **Rock**! I lose to you!")
    #                 await msg.edit(embed=embed, components=dis_components)
    #             elif res.component.label == "Paper" and choice == "Paper":
    #                 await res.respond(content="You choose **Paper** and i choose **Paper** too! This match is a tie ||but i'll defeat you next time!||")
    #                 await msg.edit(embed=embed, components=dis_components)
    #             elif res.component.label == "Scissors" and choice == "Rock":
    #                 await res.respond(content="You choose **Scissors** and i choose **Rock**! I win!!")
    #                 await msg.edit(embed=embed, components=dis_components)
    #             elif res.component.label == "Scissors" and choice == "Paper":
    #                 await res.respond(content="You choose **Scissors** and i choose **Rock**! i lose to you!")
    #                 await msg.edit(embed=embed, components=dis_components)
    #             elif res.component.label == "Scissors" and choice == "Scissors":
    #                 await res.respond(content="You choose **Scissors** and i choose **Scissors** too! This match is a tie ||but i'll defeat you next time!||")
    #                 await msg.edit(embed=embed, components=dis_components)
                    
    @commands.command(aliases=['aki'], help='Allows you to play akinator inside discord')
    @commands.cooldown(1,60, commands.BucketType.channel)
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def akinator(self, ctx):

        controls = {
            "yes": '✅',
            "no": '❌',
            "idk": '🤷‍♂️',
            "stop": "🛑"
        }

        emojis = [controls[e] for e in list(controls)]

        em=discord.Embed(description=f"**⚙️ Processing your game... Please wait!**", color=discord.Color.random())
        msg = await ctx.send(embed=em)

        game = await akin.start_game()


        questions = 1

        while akin.progression <= 80:
            if int(akin.progression) == 0:
                em=discord.Embed(title=f"Question {questions}", description=f"""
{game}""", color=discord.Color.random())
                await msg.edit(embed=em)

            for emoji in list(controls):
                await msg.add_reaction(str(controls[emoji]))

            try:
                done, pending = await asyncio.wait([
                        self.bot.wait_for("reaction_add", timeout=30, check=lambda reaction, user: user == ctx.author and str(reaction.emoji) in emojis and reaction.message == msg),
                        self.bot.wait_for("reaction_remove", timeout=30, check=lambda reaction, user: user == ctx.author and str(reaction.emoji) in emojis and reaction.message == msg)
                ], return_when=asyncio.FIRST_COMPLETED)
            except (asyncio.TimeoutError, asyncio.CancelledError):
                em=discord.Embed(description="No responce in 30 seconds, Timed out.", color=discord.Color.random())
                await msg.edit(embed=em)
                return

            try:
                reaction, user = done.pop().result()
            except (asyncio.TimeoutError, asyncio.CancelledError):
                em=discord.Embed(description="No responce in 30 seconds, Timed out.", color=discord.Color.random())
                await msg.edit(embed=em)
                return

            for future in pending:
                future.cancel()

            if str(reaction.emoji) == controls["yes"]:
                first_answer = "yes"
            elif str(reaction.emoji) == controls["no"]:
                first_answer = "no"
            elif str(reaction.emoji) == controls["idk"]:
                first_answer = "idk"
            elif str(reaction.emoji) == controls["stop"]:
                break

            question = await akin.answer(first_answer)

            questions += 1

            em=discord.Embed(title=f"Question {questions}", description=f"""
{question}""", color=discord.Color.random())
            await msg.edit(embed=em)
        await akin.win()


        if int(akin.progression) != 0:
            for reaction in list(controls):
                await msg.remove_reaction(controls[reaction], self.bot.user)

            em=discord.Embed(description=f"My guess is {akin.first_guess['name']}", color=discord.Color.random())
            em.set_image(url=akin.first_guess['absolute_picture_path'])
            await msg.edit(embed=em)
        else:
            emb = discord.Embed(description='Canceled your game.', color=discord.Color.random())
            await msg.edit(embed=emb)

            
    @commands.command(help='Makes the bot choose between 2 options, note: both options must be surrounded in "", eg: "first option" "second option"')
    @commands.cooldown(1,5,commands.BucketType.user)
    async def choose(self,ctx, option1,option2):
        choices = [option1, option2]
        choice = random.choice(choices)
        await ctx.reply(f'{choice}', allowed_mentions=discord.AllowedMentions.none())
            
    @commands.command(help='Play a game of guess the number with the bot')
    @commands.cooldown(1,5,commands.BucketType.user)
    async def guess(self,ctx, amount:int=15):
        if amount < 3:
            return await ctx.send('**<:red_cross:844165297538727956> | Cannot go below 3')
        elif amount > 1000:
            return await ctx.send('**<:red_cross:844165297538727956> | Cannot go above 1000')
        em = discord.Embed(description=f'Choose a number between **1** and **{amount}**', color=discord.Color.random())
        first = await ctx.send(embed=em)
        
        def check(m):
            return m.author == ctx.author and m.content.isdigit()
        
        correct = random.randint(1,amount)
        
        try:
            guess = await self.bot.wait_for('message', check=check, timeout=10.0)
        except asyncio.TimeoutError:
            await first.delete()
            await ctx.send(f'**You timed out :stopwatch:, the correct answer was {correct}**')
        if int(guess.content) == correct:
            embed = discord.Embed(description='**You are correct!**', color=discord.Color.random())
            await ctx.send(embed=embed)
        else:
            emb = discord.Embed(description=f'Nope! The correct asnwer is **{correct}**', color=discord.Color.random())
            await ctx.send(embed=emb)
    
    @commands.command(name='http')
    @commands.cooldown(1,5,commands.BucketType.user)
    async def cat_http(self, ctx, *, errcode=None):
        if not errcode:
            ercode = '100'
        else:
            if not errcode.isdigit():
                return await ctx.send("That is not a valid error code.")
            ercode = errcode
        
        url = f'https://http.cat/{ercode}'
        embed = discord.Embed(color=0x2F3136)
        embed.set_image(url=url)
        await ctx.send(embed=embed)
        
    
    @commands.command()
    async def snake(self,ctx):
        pass
    
    
    @commands.command(help='Uses the bot to echo whatever you say')
    @commands.cooldown(1,40, commands.BucketType.user)
    async def say(self, ctx, *, msg):
        if ctx.message.content.endswith('--owner'):
            if ctx.author.id in self.bot.owner_ids:
               return await ctx.send(msg[:-8], allowed_mentions=discord.AllowedMentions.none())
            else:
                e = discord.Embed(description=msg[:-8])
                e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
                return await ctx.send(embed=e, allowed_mentions=discord.AllowedMentions.none())
        embed = discord.Embed(description=msg)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed, allowed_mentions=discord.AllowedMentions.none())

    @commands.command(help='Play around with isometric code, note: in some cases, it might take a while to load the image')
    @commands.cooldown(1,10, commands.BucketType.user)
    async def iso(self, ctx, *, params=None):
        if params is None:
            params ={"iso_code": "11111 11111 11411 11411 11411 11411 31441 33144 23114 23314 22314- 0 0555 0505 0535- 0 0565 0606 0535- 0 0555 0555 0555"}
        else:
            params = {"iso_code": params}

        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get("https://jeyy-api.herokuapp.com/isometric", params=params) as response:
                    buf = io.BytesIO(await response.read())
                    await ctx.send(file=discord.File(buf, "isometric_draw.png"))

    @commands.command(help='Show\'s the randomly generated gay rate of a member')
    @commands.cooldown(1,5,commands.BucketType.user)
    async def gayrate(self, ctx, member:Optional[discord.Member]):
        if member is None:
            member = ctx.author
        rate = random.randint(1, 100)
        await ctx.send(f"**{member.name} is {rate}% gay :rainbow:**")

    @commands.command(help='Test-to-speech command', aliases=['text-to-speech'])
    @commands.cooldown(1,10,commands.BucketType.user)
    async def tts(self, ctx, *, text):
         start = time.perf_counter()
         aiogtts = aiogTTS()
         buffer = BytesIO()
         await aiogtts.write_to_fp(text, buffer, lang='en')
         buffer.seek(0)
         end = time.perf_counter()
         duration = (end - start) * 1
         number_id_for_tts = random.randint(1,6500)
         file = discord.File(buffer, f"{ctx.command.name}-{number_id_for_tts}.mp3")
         await ctx.send(file=file)

    @commands.command(name='roast', help='Roasts a member', aliases=['make-fun-of'])
    @commands.cooldown(1,10,commands.BucketType.user)
    async def roast_command(self, ctx, member:typing.Union[discord.Member, discord.User]):
        roa = await image_dagpi.roast()
        embed = discord.Embed(description=f'{member.mention},\n{roa}', color=discord.Color.random())
        await ctx.send(embed=embed)

    @commands.command(help='Check the pp size of someone', name='ppsize', aliases=['pp'])
    @commands.cooldown(1,5,commands.BucketType.user)
    async def pp_command(self, ctx, member:typing.Union[discord.Member, discord.User] = None):
        if member is None:
            member = ctx.author
        await ctx.send(f"{member.name}'s PP size: **8{'=' * random.randint(0, 12)}D**")
        


    

        
    
    




def setup(bot):
    bot.add_cog(Fun(bot))

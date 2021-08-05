import discord
from discord.ext import commands
from PIL import Image, ImageFilter, ImageDraw, ImageFont
import polaroid
import io, typing
from io import BytesIO
import time
import asyncio
import random
from jishaku.functools import executor_function
import urllib.request
import json
import typing
import os, asyncdagpi
import re
from urllib.request import urlretrieve 
import aiohttp

#Getting JSON Data
file = open("config.json", "r")
data = file.read()
objects = json.loads(data)

dagpi_key = objects['DAGPI_KEY']
dagpi = asyncdagpi.Client(dagpi_key)

def isImage(url):
    url = url.lower()
    if url.endswith("png") or url.endswith("jpg") or url.endswith("jpeg") or url.endswith("webp") or url.endswith("gif"):
        return True
    return False

async def getImage(ctx: commands.Context, url: typing.Union[discord.Member, discord.Emoji, discord.PartialEmoji, None] = None):

    if ctx.message.reference:
        ref = ctx.message.reference.resolved
        if ref.embeds:
            if ref.embeds[0].image.url != discord.Embed.Empty:
                if isImage(ref.embeds[0].image.url):
                    return ref.embeds[0].image.url

            if ref.embeds[0].thumbnail.url != discord.Embed.Empty:
                if isImage(ref.embeds[0].thumbnail.url):
                    return ref.embeds[0].thumbnail.url
                    
        elif ref.attachments:
            url = ref.attachments[0].url or ref.attachments[0].proxy_url
            if isImage(url):
                return url

    if isinstance(url, discord.Member):
        return str(url.avatar.with_size(1024).url)
    elif isinstance(url, str):
        if re.search(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", url):
            if isImage(url):
                return url

    if isinstance(url, discord.Emoji) or isinstance(url, discord.PartialEmoji):
        return url.url

    if ctx.message.attachments:

        url = ctx.message.attachments[0].url or ctx.message.attachments[0].proxy_url

        if isImage(url):
            return ctx.message.attachments[0].proxy_url or ctx.message.attachments[0].url

        elif isinstance(url, discord.Member):
            return str(url.avatar.with_size(1024).url)
        else:
            return str(ctx.author.avatar.with_size(1024).url)

    if url is None:
        return str(ctx.author.avatar.with_size(1024).url)

class Processing:
    __slots__ = {"ctx", "m"}

    def __init__(self, ctx):
        self.ctx = ctx
        self.m = None
    
    async def __aenter__(self, *args: typing.List[typing.Any], **kwargs):
        emb = discord.Embed(title='<a:loading:870021051017490463> Processing Image', color=discord.Color.random())
        self.m = await asyncio.wait_for(self.ctx.send(embed=emb), timeout=3)
        await asyncio.sleep(1)
        return self
    
    async def __aexit__(self, *args, **kwargs):
        try:
            await asyncio.wait_for(self.m.delete(), timeout=3)
        except discord.HTTPException:
            return
        


class Images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @executor_function
    def do_polaroid(self, image, method : str, args : list = [], kwargs : dict = {}):
        img = polaroid.Image(image)
        method = getattr(img, method)
        method(*args, **kwargs)
        bytes_ = io.BytesIO(img.save_bytes())
        return bytes_

    @commands.Cog.listener()
    async def on_message(self,msg):
        pass

    @commands.command(help='Sends a message a clyde')
    @commands.cooldown(1,5,commands.BucketType.user)
    async def clyde(self, ctx, *, text = None):
        if text == None:
            return await ctx.send("**You need to provide some text ||  E  ||**")
        async with aiohttp.ClientSession() as ses:
            async with ses.get(f'https://nekobot.xyz/api/imagegen?type=clyde&text={text}') as r:
                if r.status in range(200, 299):
                    data = await r.json()
                    urlimg = data['message']
                    embed = discord.Embed(description="Clyde Says:")
                    embed.set_image(url=urlimg)
                    await ctx.send(embed=embed)
                    await ses.close()
                else:
                    await ctx.reply('Hmmmm.... There was an error while sending the request. Maybe try again later :thinking:', mention_author=False)
                    await ses.close()

  
    @commands.command(help='Finds a random meme from the internet')
    @commands.cooldown(1,5,commands.BucketType.user)
    async def meme(self,ctx):
        async with aiohttp.ClientSession() as ses:
            async with ses.get("https://meme-api.herokuapp.com/gimme/dankmemes") as response:
                data = await response.json()
                img_url = data['url']   
                post_link = data['postLink']
                img_title = data['title']
                memebed = discord.Embed(title=img_title,url=img_url,color=discord.Color.random())
                memebed.set_image(url=img_url)
                await ctx.send(embed=memebed)

    @commands.command(help='Applies a fry effect on a profile picture')
    @commands.cooldown(1,5,commands.BucketType.user)
    async def fry(self, ctx, member: typing.Union[discord.Member, discord.PartialEmoji, discord.Emoji] = None):
        if member == None:
            member = ctx.author
        url = await getImage(ctx, member)
        async with Processing(ctx):
            img = await dagpi.image_process(asyncdagpi.ImageFeatures.deepfry(), url=url)
            file = discord.File(fp=img.image, filename=f'{ctx.command.name}.{img.format}')
            embed = discord.Embed(color=discord.Color.random())
            embed.set_image(url=f'attachment://{ctx.command.name}.{img.format}')
            embed.set_footer(text=f'| Requested by {ctx.author}', icon_url=ctx.author.avatar.url)
            await ctx.send(file=file, embed=embed)
                    
    @commands.command(help='Applies a blurpify effect on a profile picture')
    @commands.cooldown(1,5,commands.BucketType.user)
    async def blurpify(self, ctx, member: typing.Union[discord.Member, discord.PartialEmoji, discord.Emoji] = None):
        if member == None:
            member = ctx.author
        url = await getImage(ctx, member)
        async with Processing(ctx):
            async with aiohttp.ClientSession() as ses:
                async with ses.get(f'https://nekobot.xyz/api/imagegen?type=blurpify&image={url}') as r:
                    if r.status in range(200, 299):
                        data = await r.json()
                        urlimg = data['message']
                        embed = discord.Embed(title=f'Blurpified {member.name}', color = 0x42ebeb)
                        embed.set_image(url=urlimg)
                        await ctx.send(embed=embed)
                        await ses.close()
                    else:
                        await ctx.send(f'**Hmmmm.... There was an error while sending the request. Maybe try again later :thinking:** | {r.status}')
                        await ses.close()


    @commands.command(help='Shows the window\'s delete verification screen but with a profile picture')
    @commands.cooldown(1,15,commands.BucketType.user)
    async def delete(self,ctx,member:typing.Union[discord.Member, discord.PartialEmoji, discord.Emoji]=None):
        if member is None:
            member = ctx.author
        async with Processing(ctx):
            url = await getImage(ctx, member)
            img = await dagpi.image_process(asyncdagpi.ImageFeatures.delete(), url=url)
            file = discord.File(fp=img.image, filename=f'{ctx.command.name}.{img.format}')
            embed=discord.Embed(color=discord.Color.random())
            embed.set_image(url=f"attachment://{ctx.command.name}.{img.format}")
            embed.set_footer(text=f'| Requested by {ctx.author}', icon_url=ctx.author.avatar.url)
            await ctx.send(file=file, embed=embed)


    @commands.command()
    @commands.cooldown(1,5,commands.BucketType.user)
    async def ohno(self,ctx,* ,text="u need text"):
      img = Image.open("utilities/images/ohno.png")
      draw = ImageDraw.Draw(img)
      font = ImageFont.truetype("utilities/fonts/arial.ttf",18)

      draw.text((188,52),text, (0,0,0),font=font)

      img.save("ohnosaved.png")
      await ctx.send(file=discord.File("ohnosaved.png"))
      os.remove("ohnosaved.png")

    @commands.command(help='Slaps a member')
    @commands.cooldown(1,5,commands.BucketType.user)
    async def slap(self, ctx, member: discord.Member=None):
        if member == None:
            return await ctx.send("**Srsly u need to provide a member for slapping ||smol brain||**")
        img = Image.open("utilities/images/slap.png")
        asset = member.avatar.with_size(128).read()
        slapper = ctx.author.avatar.with_size(128).read()
        data = BytesIO(await asset)
        pfp = Image.open(data)
        slappper = BytesIO(await slapper)
        slapppper = Image.open(slappper)

        img.paste(pfp, (244,244))
        img.paste(slapppper, (567,109))

        img.save("test.png")
        await ctx.send(file = discord.File("test.png"))
        os.remove("test.png")

    @commands.command()
    @commands.cooldown(1,5,commands.BucketType.user)
    async def presentation(self, ctx, *, text):
        if len(text) > 18:
            return await ctx.reply("**Limit of letters in this command is 18 ||ok||**", mention_author=False)
        img = Image.open("utilities/images/presentation.png")
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("utilities/fonts/arial.ttf", 36)
      
        draw.text((139,184), text, (0, 0, 0), font=font)

        img.save("presentationsaved.png")
      
        await ctx.send(file = discord.File("presentationsaved.png"))
        os.remove("presentationsaved.png")

    @commands.command(pass_context=True)
    @commands.cooldown(1,5,commands.BucketType.user)
    async def location(self, ctx, *, text=None):
        if len(text) > 8:
            return await ctx.send("**Limit of letters in this command is 8 ||ok||**", mention_author=False)

        img = Image.open("utilities/images/location.png")
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("utilities/fonts/arial.ttf", 18)
      
        draw.text((36,22), text, (0, 0, 0), font=font)

        img.save("locationsaved.png")
      
        await ctx.send(file = discord.File("locationsaved.png"))
        os.remove("locationsaved.png")



    @commands.command()
    @commands.cooldown(1,5,commands.BucketType.user)
    async def explain(self, ctx, *, text):
        if len(text) > 26:
            return await ctx.reply("**Limit of letters in this command is 26 ||ok||**", mention_author=False)
        img = Image.open("utilities/images/explain.png")
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("utilities/fonts/impact.ttf", 64)
      
        draw.text((38,611), text, (255, 255, 255), font=font)

        img.save("explainsaved.png")
      
        await ctx.send(file = discord.File("explainsaved.png"))
        os.remove("explainsaved.png")

    @commands.command(help='Applies a flip effect to a profile picture')
    @commands.cooldown(1,5,commands.BucketType.user)
    async def flip(self, ctx, member: discord.Member=None):
        if member == None:
            member = ctx.author
        img = member.avatar.with_format('png').read()
        data = BytesIO(await img)
        pfp = Image.open(data)

        flippedImage = pfp.transpose(Image.FLIP_TOP_BOTTOM)
        flippedImage.save("flipped.png")
        await ctx.send(file = discord.File("flipped.png"))
        os.remove("flipped.png")

    @commands.command(help='Show\'s a wanted poster with a profile picture')
    @commands.cooldown(1,5,commands.BucketType.user)
    async def wanted(self, ctx, member: discord.Member = None):
      if member == None:
        member = ctx.author
      
      wanted = Image.open("utilities/images/wanted.png")
      asset = member.avatar.with_size(128).read()
      data = BytesIO(await asset)
      pfp = Image.open(data)

      pfp = pfp.resize((309,273))

      wanted.paste(pfp, (74,236))

      wanted.save("wantedsaved.png")

      await ctx.send(file = discord.File("wantedsaved.png"))
      os.remove("wantedsaved.png")



    @commands.command(help='Generates a stickbug video with your profile picture')
    @commands.cooldown(1,15,commands.BucketType.user)
    async def stickbug(self, ctx, member: discord.Member = None):
        if member == None:
            member = ctx.author
        url = member.avatar.with_format('png')
        async with Processing(ctx):
            start = time.perf_counter()
            async with aiohttp.ClientSession() as ses:
                async with ses.get(f'https://nekobot.xyz/api/imagegen?type=stickbug&url={url}') as r:
                    if r.status in range(200, 299):
                        end = time.perf_counter()
                        duration = (end - start) * 1
                        data = await r.json()
                        urlimg = data['message']
                        await ctx.send(f"Took: {round(duration)}s\n\n{urlimg}")
                        await ses.close()
                    else:
                        await ctx.send(f'**Hmmmm.... There was an error while sending the request. Maybe try again later :thinking:**')
                        await ses.close()

    @commands.command(help='Generates your profile picture within a iPhone')
    @commands.cooldown(1,5,commands.BucketType.user)
    async def iphone(self, ctx, member:discord.Member = None):
      if member == None:
        return await ctx.send("**<:red_cross:844165297538727956> | Please Provide a valid member**")
      url = await getImage(ctx, member)
      async with aiohttp.ClientSession() as ses:
        async with ses.get(f"https://nekobot.xyz/api/imagegen?type=iphonex&url={url}") as r:
          r = await r.json()
          image = r["message"]
          embed = discord.Embed(color=discord.Color.random(), title='Iphone')
          embed.set_image(url=image)
          embed.set_footer(text=f'|Requested by {ctx.author}', icon_url=ctx.author.avatar.url)
          await ses.close()
          await ctx.reply(embed=embed, mention_author=False)


    @commands.command(help='Applies a communism effect to a profile picture')
    @commands.cooldown(1,15,commands.BucketType.user)
    async def communism(self, ctx, member:typing.Union[discord.Member, discord.PartialEmoji, discord.Emoji] = None):
        if member == None:
         member = ctx.author
        async with Processing(ctx):
            try:
                url = await getImage(ctx, member)
                img = await dagpi.image_process(asyncdagpi.ImageFeatures.communism(), url=url)
                file=discord.File(img.image, f"{ctx.command.name}.gif")
                embed=discord.Embed(color=discord.Color.blurple())
                embed.set_image(url=f"attachment://{ctx.command.name}.gif")
                embed.set_footer(text=f'| Requested by {ctx.author}', icon_url=ctx.author.avatar.url)
                await ctx.send(file=file, embed=embed)
            except discord.HTTPException:
                await ctx.send('**An Error occured while uploading the image to discord.**')
   
    @commands.command(help='Applies a america effect to a profile picture')
    @commands.cooldown(1,15,commands.BucketType.user)
    async def america(self, ctx, member:typing.Union[discord.Member, discord.PartialEmoji, discord.Emoji] = None):
        if member == None:
         member = ctx.author
        async with Processing(ctx):
            url = await getImage(ctx, member)
            img = await dagpi.image_process(asyncdagpi.ImageFeatures.america(), url=str(url))
            file=discord.File(img.image, f"{ctx.command.name}.gif")
            embed=discord.Embed(color=discord.Color.blurple())
            embed.set_image(url=f"attachment://{ctx.command.name}.gif")
            embed.set_footer(text=f'| Requested by {ctx.author}', icon_url=ctx.author.avatar.url)
            await ctx.reply(file=file, embed=embed, mention_author=False)
  
    @commands.command(help='Applies a triggered effect to a profile picture')
    @commands.cooldown(1,15,commands.BucketType.user)
    async def triggered(self, ctx, member:typing.Union[discord.Member, discord.PartialEmoji, discord.Emoji] = None):
        if member == None:
         member = ctx.author
        async with Processing(ctx):
            url = await getImage(ctx, member)
            img = await dagpi.image_process(asyncdagpi.ImageFeatures.triggered(), url=str(url))
            file=discord.File(img.image, f"{ctx.command.name}.gif")
            embed=discord.Embed(color=discord.Color.blurple())
            embed.set_image(url=f"attachment://{ctx.command.name}.gif")
            embed.set_footer(text=f'| Requested by {ctx.author}', icon_url=ctx.author.avatar.url)
            await ctx.reply(embed=embed, file=file, mention_author=False)

    @commands.command(help='Applies a ultra-wide effect to a profile picture')
    @commands.cooldown(1,5,commands.BucketType.user)
    async def ultrawide(self, ctx, member :discord.Member=None):
        if member == None:
          member = ctx.author
        image = str(member.avatar.with_format('png'))
        async with aiohttp.ClientSession() as ses:
                async with ses.get(str(image)) as r:
                     img = await r.read()
                     res = await self.do_polaroid(img, method="resize", args=(4000,900,1))
                if r.status in range(200, 299):
                  embed=discord.Embed(color=discord.Color.blurple())
                  embed.set_image(url=f"attachment://{ctx.command.name}.png")
                  embed.set_footer(text=f'| Requested by {ctx.author}', icon_url=ctx.author.avatar.url)
                  await ctx.reply(embed=embed, file=discord.File(res, filename=f"{ctx.command.name}.png"), mention_author=False)
                  await ses.close()
    
    @commands.command(help='Applies a dramatical effect to a profile picture')
    @commands.cooldown(1,5,commands.BucketType.user)
    async def dramatical(self, ctx, member: discord.Member=None):
        if member == None:
          member = ctx.author
        image = str(member.avatar.with_format('png'))
        async with aiohttp.ClientSession() as ses:
                async with ses.get(str(image)) as r:
                     img = await r.read()
                     res = await self.do_polaroid(img, method="filter", args=["dramatic"])
                if r.status in range(200, 299):
                  embed=discord.Embed(color=discord.Color.blurple())
                  embed.set_image(url=f"attachment://{ctx.command.name}.png")
                  embed.set_footer(text=f'| Requested by {ctx.author}', icon_url=ctx.author.avatar.url)
                  await ctx.reply(embed=embed, file=discord.File(res, filename=f"{ctx.command.name}.png"), mention_author=False)
                  await ses.close()

    @commands.command(help='Applies a nuclear effect to a profile picture')
    @commands.cooldown(1,15,commands.BucketType.user)
    async def nuclear(self, ctx, member:typing.Union[discord.Member, discord.PartialEmoji, discord.Emoji]=None):
        if member is None:
            member = ctx.author
        async with Processing(ctx):
            url = await getImage(ctx, member)
            img = await dagpi.image_process(asyncdagpi.ImageFeatures.bomb(), url=url)
            file = discord.File(fp=img.image, filename=f'{ctx.command.name}.{img.format}')
            embed=discord.Embed(color=discord.Color.random())
            embed.set_image(url=f"attachment://{ctx.command.name}.{img.format}")
            embed.set_footer(text=f'| Requested by {ctx.author}', icon_url=ctx.author.avatar.url)
            await ctx.send(file=file, embed=embed)

    @commands.command(help='Applies a pixel effect to a profile picture')
    @commands.cooldown(1,15,commands.BucketType.user)
    async def pixel(self, ctx, member:typing.Union[discord.Member, discord.PartialEmoji, discord.Emoji]=None):
        if member is None:
            member = ctx.author
        async with Processing(ctx):
            url = await getImage(ctx, member)
            img = await dagpi.image_process(asyncdagpi.ImageFeatures.pixel(), url=url)
            file = discord.File(fp=img.image, filename=f'{ctx.command.name}.{img.format}')
            embed=discord.Embed(color=discord.Color.random())
            embed.set_image(url=f"attachment://{ctx.command.name}.{img.format}")
            embed.set_footer(text=f'| Requested by {ctx.author}', icon_url=ctx.author.avatar.url)
            await ctx.send(file=file, embed=embed)

    @commands.command(help='Applies a neon effect to a profile picture')
    @commands.cooldown(1,15,commands.BucketType.user)
    async def neon(self,ctx,member:typing.Union[discord.Member, discord.PartialEmoji, discord.Emoji]=None):
        if member is None:
            member = ctx.author
        async with Processing(ctx):
            url = await getImage(ctx, member)
            img = await dagpi.image_process(asyncdagpi.ImageFeatures.neon(), url=url)
            file = discord.File(fp=img.image, filename=f'{ctx.command.name}.{img.format}')
            embed=discord.Embed(color=discord.Color.random())
            embed.set_image(url=f"attachment://{ctx.command.name}.{img.format}")
            embed.set_footer(text=f'| Requested by {ctx.author}', icon_url=ctx.author.avatar.url)
            await ctx.send(file=file, embed=embed)

    @commands.command(help='Applies a dissolve effect to a profile picture')
    @commands.cooldown(1,15,commands.BucketType.user)
    async def dissolve(self, ctx, member:typing.Union[discord.Member, discord.PartialEmoji, discord.Emoji]=None):
        if member is None:
            member = ctx.author
        async with Processing(ctx):
            url = await getImage(ctx, member)
            img = await dagpi.image_process(asyncdagpi.ImageFeatures.dissolve(), url=url)
            file = discord.File(fp=img.image, filename=f'{ctx.command.name}.{img.format}')
            embed=discord.Embed(color=discord.Color.random())
            embed.set_image(url=f"attachment://{ctx.command.name}.{img.format}")
            embed.set_footer(text=f'| Requested by {ctx.author}', icon_url=ctx.author.avatar.url)
            await ctx.send(file=file, embed=embed)

    @commands.command(help='Applies a art effect to a profile picture')
    @commands.cooldown(1,15,commands.BucketType.user)
    async def art(self, ctx, member:typing.Union[discord.Member, discord.PartialEmoji, discord.Emoji]=None):
        if member is None:
            member = ctx.author
        async with Processing(ctx):
            url = await getImage(ctx, member)
            img = await dagpi.image_process(asyncdagpi.ImageFeatures.paint(), url=url)
            file = discord.File(fp=img.image, filename=f'{ctx.command.name}.{img.format}')
            embed=discord.Embed(color=discord.Color.random())
            embed.set_image(url=f"attachment://{ctx.command.name}.{img.format}")
            embed.set_footer(text=f'| Requested by {ctx.author}', icon_url=ctx.author.avatar.url)
            await ctx.send(file=file, embed=embed)

    @commands.command(help='Applies a spin effect to a profile picture')
    @commands.cooldown(1,15,commands.BucketType.user)
    async def spin(self, ctx, member:typing.Union[discord.Member, discord.PartialEmoji, discord.Emoji]=None):
        if member is None:
            member = ctx.author
        async with Processing(ctx):
            url = await getImage(ctx, member)
            img = await dagpi.image_process(asyncdagpi.ImageFeatures.spin(), url=url)
            file = discord.File(fp=img.image, filename=f'{ctx.command.name}.{img.format}')
            embed=discord.Embed(color=discord.Color.random())
            embed.set_image(url=f"attachment://{ctx.command.name}.{img.format}")
            embed.set_footer(text=f'| Requested by {ctx.author}', icon_url=ctx.author.avatar.url)
            await ctx.send(file=file, embed=embed)

    @commands.command(help='Applies a jail effect to a profile picture')
    @commands.cooldown(1,15,commands.BucketType.user)
    async def jail(self,ctx,member:typing.Union[discord.Member, discord.PartialEmoji, discord.Emoji]=None):
        if member is None:
            member = ctx.author
        async with Processing(ctx):
            url = await getImage(ctx, member)
            img = await dagpi.image_process(asyncdagpi.ImageFeatures.jail(), url=url)
            file = discord.File(fp=img.image, filename=f'{ctx.command.name}.{img.format}')
            embed=discord.Embed(color=discord.Color.random())
            embed.set_image(url=f"attachment://{ctx.command.name}.{img.format}")
            embed.set_footer(text=f'| Requested by {ctx.author}', icon_url=ctx.author.avatar.url)
            await ctx.send(file=file, embed=embed)

    @commands.command(help='A GTA V wasted screen with your profile picture as backround')
    @commands.cooldown(1,15,commands.BucketType.user)
    async def wasted(self,ctx,member:typing.Union[discord.Member, discord.PartialEmoji, discord.Emoji] = None):
        if member is None:
            member = ctx.author
        async with Processing(ctx):
            url = await getImage(ctx, member)
            img = await dagpi.image_process(asyncdagpi.ImageFeatures.wasted(), url=url)
            file = discord.File(fp=img.image, filename=f'{ctx.command.name}.{img.format}')
            embed=discord.Embed(color=discord.Color.random())
            embed.set_image(url=f"attachment://{ctx.command.name}.{img.format}")
            embed.set_footer(text=f'| Requested by {ctx.author}', icon_url=ctx.author.avatar.url)
            await ctx.send(file=file, embed=embed)
            
            
    @commands.command(help='Applies a swirl effect to a profile picture')
    @commands.cooldown(1,15,commands.BucketType.user)
    async def swirl(self, ctx, user: typing.Union[discord.Member, discord.PartialEmoji, discord.Emoji] = None):
        if user is None:
            user = ctx.author
        url = await getImage(ctx, user)
        async with Processing(ctx):
            img = await dagpi.image_process(asyncdagpi.ImageFeatures.swirl(), url=url)
            file = discord.File(fp=img.image, filename=f'{ctx.command.name}.{img.format}')
            embed = discord.Embed(color=discord.Color.random())
            embed.set_image(url=f'attachment://{ctx.command.name}.{img.format}')
            embed.set_footer(text=f'| Requested by {ctx.author}', icon_url=ctx.author.avatar.url)
            await ctx.send(file=file, embed=embed)
    
    @commands.command(help='Generates a captcha but with your text and profile picture on it')
    @commands.cooldown(1,15,commands.BucketType.user)
    async def captcha(self, ctx, text, user: typing.Union[discord.Member, discord.PartialEmoji, discord.Emoji] = None):
        if user is None:
            user = ctx.author
        url = await getImage(ctx, user)
        async with Processing(ctx):
            img = await dagpi.image_process(asyncdagpi.ImageFeatures.captcha(), url=url, text=text)
            file = discord.File(fp=img.image, filename=f'{ctx.command.name}.{img.format}')
            embed = discord.Embed(color=discord.Color.random())
            embed.set_image(url=f'attachment://{ctx.command.name}.{img.format}')
            embed.set_footer(text=f'| Requested by {ctx.author}', icon_url=ctx.author.avatar.url)
            await ctx.send(file=file, embed=embed)

    @commands.command(help='Applies a magikal effect to a profile picture')
    @commands.cooldown(1,15,commands.BucketType.user)
    async def magik(self, ctx, user: typing.Union[discord.Member, discord.PartialEmoji, discord.Emoji] = None):
        if user is None:
            user = ctx.author
        url = await getImage(ctx, user)
        async with Processing(ctx):
            img = await dagpi.image_process(asyncdagpi.ImageFeatures.magik(), url=url)
            file = discord.File(fp=img.image, filename=f'{ctx.command.name}.{img.format}')
            embed = discord.Embed(color=discord.Color.random())
            embed.set_image(url=f'attachment://{ctx.command.name}.{img.format}')
            embed.set_footer(text=f'| Requested by {ctx.author}', icon_url=ctx.author.avatar.url)
            await ctx.send(file=file, embed=embed)
    
    @commands.command(help='Applies a freezing effect to a profile picture')
    @commands.cooldown(1,15,commands.BucketType.user)
    async def freeze(self, ctx, user: typing.Union[discord.Member, discord.PartialEmoji, discord.Emoji] = None):
        if user is None:
            user = ctx.author
        url = await getImage(ctx, user)
        async with Processing(ctx):
            img = await dagpi.image_process(asyncdagpi.ImageFeatures.freeze(), url=url)
            file = discord.File(fp=img.image, filename=f'{ctx.command.name}.{img.format}')
            embed = discord.Embed(color=discord.Color.random())
            embed.set_image(url=f'attachment://{ctx.command.name}.{img.format}')
            embed.set_footer(text=f'| Requested by {ctx.author}', icon_url=ctx.author.avatar.url)
            await ctx.send(file=file, embed=embed)

    @commands.command(help='Applies a blur effect to a profile picture')
    @commands.cooldown(1,15,commands.BucketType.user)
    async def blur(self, ctx, user: typing.Union[discord.Member, discord.PartialEmoji, discord.Emoji] = None):
        if user is None:
            user = ctx.author
        url = await getImage(ctx, user)
        async with Processing(ctx):
            img = await dagpi.image_process(asyncdagpi.ImageFeatures.blur(), url=url)
            file = discord.File(fp=img.image, filename=f'{ctx.command.name}.{img.format}')
            embed = discord.Embed(color=discord.Color.random())
            embed.set_image(url=f'attachment://{ctx.command.name}.{img.format}')
            embed.set_footer(text=f'| Requested by {ctx.author}', icon_url=ctx.author.avatar.url)
            await ctx.send(file=file, embed=embed)
    
    @commands.command(help='Generates a fake discord message with a member and text of your choice')
    @commands.cooldown(1,15,commands.BucketType.user)
    async def mock(self, ctx, member:discord.Member, *, text):
        if ctx.message.content.endswith('--light'):
            mode = False
            text = text[:-7]
        else:
            mode = True
            text = text
        url = member.avatar.url
        img = await dagpi.image_process(asyncdagpi.ImageFeatures.discord(), url=url, username=member.name, text=text, dark=mode)
        file = discord.File(fp=img.image, filename=f'{ctx.command.name}.{img.format}')
        embed = discord.Embed(color=discord.Color.random())
        embed.set_image(url=f'attachment://{ctx.command.name}.{img.format}')
        await ctx.send(file=file, embed=embed)

    @commands.command(help='Generates a fake comment on youtube with a member and text of your choice')
    @commands.cooldown(1,15,commands.BucketType.user)
    async def comment(self, ctx, member:discord.Member, *, text):
        if ctx.message.content.endswith('--light'):
            mode = False
            text = text[:-7]
        else:
            mode = True
            text = text
        url = member.avatar.url
        img = await dagpi.image_process(asyncdagpi.ImageFeatures.youtube(), url=url, username=member.name, text=text, dark=mode)
        file = discord.File(fp=img.image, filename=f'{ctx.command.name}.{img.format}')
        embed = discord.Embed(color=discord.Color.random())
        embed.set_image(url=f'attachment://{ctx.command.name}.{img.format}')
        await ctx.send(file=file, embed=embed)
    
    @commands.command(help='Generates a fake tweet with a member and text of your choice')
    @commands.cooldown(1,15,commands.BucketType.user)
    async def tweet(self, ctx, member:discord.Member, *, text ):
        url = member.avatar.url
        img = await dagpi.image_process(asyncdagpi.ImageFeatures.tweet(), url=url, username=member.name, text=text)
        file = discord.File(fp=img.image, filename=f'{ctx.command.name}.{img.format}')
        embed = discord.Embed(color=discord.Color.random())
        embed.set_image(url=f'attachment://{ctx.command.name}.{img.format}')
        await ctx.send(file=file, embed=embed)

    @commands.command(help='Applies a invert effect to a profile picture')
    @commands.cooldown(1,15,commands.BucketType.user)
    async def invert(self, ctx, member:typing.Union[discord.Member, discord.PartialEmoji, discord.Emoji]=None):
        if member is None:
            member = ctx.author
        url = await getImage(ctx. member)
        async with Processing(ctx):
            img = await dagpi.image_process(asyncdagpi.ImageFeatures.invert(), url=url)
            file = discord.File(fp=img.image, filename=f'{ctx.command.name}.{img.format}')
            embed = discord.Embed(color=discord.Color.random())
            embed.set_image(url=f'attachment://{ctx.command.name}.{img.format}')
            await ctx.send(file=file, embed=embed)

    @commands.command(help='Applies a burn effect to a profile picture')
    @commands.cooldown(1,15,commands.BucketType.user)
    async def burn(self, ctx, member:typing.Union[discord.Member, discord.PartialEmoji, discord.Emoji]=None):
        if member is None:
            member = ctx.author
        url = await getImage(ctx, member)
        async with Processing(ctx):
            img = await dagpi.image_process(asyncdagpi.ImageFeatures.burn(), url=url)
            file = discord.File(fp=img.image, filename=f'{ctx.command.name}.{img.format}')
            embed = discord.Embed(color=discord.Color.random())
            embed.set_image(url=f'attachment://{ctx.command.name}.{img.format}')
            await ctx.send(file=file, embed=embed)


    @commands.command(help='Applies a charcoal effect to a profile picture')
    @commands.cooldown(1,15,commands.BucketType.user)
    async def charcoal(self, ctx, member:typing.Union[discord.Member, discord.PartialEmoji, discord.Emoji]=None):
        if member is None:
            member = ctx.author
        url = await getImage(ctx, member)
        async with Processing(ctx):
            img = await dagpi.image_process(asyncdagpi.ImageFeatures.charcoal(), url=url)
            file = discord.File(fp=img.image, filename=f'{ctx.command.name}.{img.format}')
            embed = discord.Embed(color=discord.Color.random())
            embed.set_image(url=f'attachment://{ctx.command.name}.{img.format}')
            await ctx.send(file=file, embed=embed)
    
    @commands.command(help='Applies a sepia effect to a profile picture')
    @commands.cooldown(1,15,commands.BucketType.user)
    async def sepia(self, ctx, member:typing.Union[discord.Member, discord.PartialEmoji, discord.Emoji]=None):
        if member is None:
            member = ctx.author
        url = await getImage(ctx, member)
        async with Processing(ctx):
            img = await dagpi.image_process(asyncdagpi.ImageFeatures.sepia(), url=url)
            file = discord.File(fp=img.image, filename=f'{ctx.command.name}.{img.format}')
            embed = discord.Embed(color=discord.Color.random())
            embed.set_image(url=f'attachment://{ctx.command.name}.{img.format}')
            await ctx.send(file=file, embed=embed)

    
    @commands.command(help='Applies a poster effect')
    @commands.cooldown(1,15,commands.BucketType.user)
    async def poster(self, ctx, member:typing.Union[discord.Member, discord.PartialEmoji, discord.Emoji]=None):
        if member is None:
            member = ctx.author
        url = await getImage(ctx, member)
        async with Processing(ctx):
            img = await dagpi.image_process(asyncdagpi.ImageFeatures.poster(), url=url)
            file = discord.File(fp=img.image, filename=f'{ctx.command.name}.{img.format}')
            embed = discord.Embed(color=discord.Color.random())
            embed.set_image(url=f'attachment://{ctx.command.name}.{img.format}')
            await ctx.send(file=file, embed=embed)


    @commands.command(help='Play a game of guess the flag with the bot')
    @commands.cooldown(1,15,commands.BucketType.user)
    async def guessthelogo(self, ctx):
        logo = await dagpi.logo()
        embed = discord.Embed(title='Guess The Logo', color=discord.Color.random())
        embed.set_image(url=logo.question)
        msg = await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author 
        
            
        try:
            guess = await self.bot.wait_for('message', check=check, timeout=70)
        except asyncio.TimeoutError:
            return await ctx.send("Stopped due to timeout.")

        if str(guess.content) == logo.brand:
            e = discord.Embed(title='Correct!', description=f'Brand Name: {logo.brand}', color=discord.Color.random())
            e.set_image(url=logo.answer)
            await msg.delete()
            await ctx.send(embed=e)            
        else:
            return await ctx.send(f"You failed! The correct answer was {logo.brand}")
    
    @commands.command(help='Among-us Eject', usage='[member|text] <color> <imposter: True/False>', name='amongus')
    @commands.cooldown(1,15,commands.BucketType.user)
    async def among_us_command(self, ctx, member: typing.Union[discord.Member, discord.User, str], color:typing.Optional[str], imposter:typing.Optional[bool]):
        if color is None:
             color = random.choice(['black', 'blue', 'brown', 'cyan', 'darkgreen', 'lime', 'orange', 'pink', 'purple', 'red', 'white', 'yellow'])
        if imposter is None:
            imposter = random.choice([True, False])
        
        async with Processing(ctx):
            res = await (await self.bot.session.get(f"https://vacefron.nl/api/ejected?name={''.join(member if isinstance(member, str) else member.name)}&impostor={imposter}&crewmate={color}")).read()
            file = discord.File(fp=io.BytesIO(res), filename=f'{ctx.command.name}.png')
            embed = discord.Embed(color=discord.Color.random(), timestamp=discord.utils.utcnow())
            embed.set_image(url=f'attachment://{ctx.command.name}.png')
            embed.set_footer(text=f'Requested by {ctx.author.name}', icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed, file=file)

    @commands.command(help='Random Anime Image', name='waifu')
    @commands.cooldown(1,30,commands.BucketType.user)
    async def command_waifu(self, ctx):
           url = 'https://api.hori.ovh:8036/sfw/waifu/?filter=3867126be8e260b5.jpeg,ca52928d43b30d6a&gif=False'  

           res = await self.bot.session.get(url)
           if res.status == 200 or res.status==404 or res.status==500 or res.status==502:
                data = await res.json()
           else:
               return await ctx.send("The API returned an error.")
           image_returned = data['url']
           embed = discord.Embed(color=0x2F3136)
           embed.set_image(url=image_returned)
           embed.set_footer(text=f'Requested by {ctx.author.name}', icon_url=ctx.author.avatar.url)
           await ctx.send(embed=embed)

    @commands.command(help='Applies a pixel effect to a profile picture')
    @commands.cooldown(1,15,commands.BucketType.user)
    async def pixelate(self, ctx, member:typing.Union[discord.Member, discord.PartialEmoji, discord.Emoji]=None):
        if member is None:
            member = ctx.author
        url = await getImage(ctx, member)
        async with Processing(ctx):
            img = await dagpi.image_process(asyncdagpi.ImageFeatures.mosiac(), url=url)
            file = discord.File(fp=img.image, filename=f'{ctx.command.name}.{img.format}')
            embed = discord.Embed(color=discord.Color.random())
            embed.set_image(url=f'attachment://{ctx.command.name}.{img.format}')
            await ctx.send(file=file, embed=embed)

    @commands.command(help='Applies a shatter effect to a profile picture')
    @commands.cooldown(1,15,commands.BucketType.user)
    async def shatter(self, ctx, member:typing.Union[discord.Member, discord.PartialEmoji, discord.Emoji]=None):
        if member is None:
            member = ctx.author
        url = await getImage(ctx, member)
        async with Processing(ctx):
            img = await dagpi.image_process(asyncdagpi.ImageFeatures.shatter(), url=url)
            file = discord.File(fp=img.image, filename=f'{ctx.command.name}.{img.format}')
            embed = discord.Embed(color=discord.Color.random())
            embed.set_image(url=f'attachment://{ctx.command.name}.{img.format}')
            await ctx.send(file=file, embed=embed)

    @commands.command(help='Applies a pride effect to a profile picture')
    @commands.cooldown(1,15,commands.BucketType.user)
    async def pride(self, ctx, member:typing.Union[discord.Member, discord.PartialEmoji, discord.Emoji]=None):
        if member is None:
            member = ctx.author
        url = await getImage(ctx, member)
        async with Processing(ctx):
            img = await dagpi.image_process(asyncdagpi.ImageFeatures.pride(), url=url, flag='gay')
            file = discord.File(fp=img.image, filename=f'{ctx.command.name}.{img.format}')
            embed = discord.Embed(color=discord.Color.random())
            embed.set_image(url=f'attachment://{ctx.command.name}.{img.format}')
            await ctx.send(file=file, embed=embed)

    @commands.command(help='Applies a trash effect to a profile picture')
    @commands.cooldown(1,15,commands.BucketType.user)
    async def trash(self, ctx, member:typing.Union[discord.Member, discord.PartialEmoji, discord.Emoji]=None):
        if member is None:
            member = ctx.author
        url = await getImage(ctx, member)
        async with Processing(ctx):
            img = await dagpi.image_process(asyncdagpi.ImageFeatures.trash(), url=url)
            file = discord.File(fp=img.image, filename=f'{ctx.command.name}.{img.format}')
            embed = discord.Embed(color=discord.Color.random())
            embed.set_image(url=f'attachment://{ctx.command.name}.{img.format}')
            await ctx.send(file=file, embed=embed)

    @commands.command(name='metrix', help='Applies a metrix effect to a profile picture')
    @commands.cooldown(1,15,commands.BucketType.user)
    async def command_metrix(self, ctx, member:typing.Union[discord.Member, discord.PartialEmoji, discord.Emoji]=None):
        if member is None:
            member = ctx.author
        url = await getImage(ctx, member)
        async with Processing(ctx):
            img = await dagpi.image_process(asyncdagpi.ImageFeatures.ascii(), url=url)
            file = discord.File(fp=img.image, filename=f'{ctx.command.name}.{img.format}')
            embed = discord.Embed(color=discord.Color.random())
            embed.set_image(url=f'attachment://{ctx.command.name}.{img.format}')
            await ctx.send(file=file, embed=embed)

    @commands.command(name='night', help='Applies a night effect to a profile picture ')
    @commands.cooldown(1,15,commands.BucketType.user)
    async def command_night(self, ctx, member:typing.Union[discord.Member, discord.PartialEmoji, discord.Emoji]=None):
        if member is None:
            member = ctx.author
        url = await getImage(ctx, member)
        async with Processing(ctx):
            img = await dagpi.image_process(asyncdagpi.ImageFeatures.night(), url=url)
            file = discord.File(fp=img.image, filename=f'{ctx.command.name}.{img.format}')
            embed = discord.Embed(color=discord.Color.random())
            embed.set_image(url=f'attachment://{ctx.command.name}.{img.format}')
            await ctx.send(file=file, embed=embed)
    

    

    
    

    

    
    


def setup(bot):
    bot.add_cog(Images(bot)) 

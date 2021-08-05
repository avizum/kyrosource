import discord
import sys
from discord.ext import commands
import aiosqlite
import traceback
from utilities.addons.checks import is_blacklisted
from discord.ext import tasks
import time
import aiohttp
from utilities.addons.webhook import Webhook, AsyncWebhookAdapter
import json
import logging
from utilities.addons.checks import Maintenace
import asyncio
import logging 

logging.basicConfig(level=logging.INFO)

owners = [422854944857784322, 812901193722363904]

#Loading JSON Data
file = open("config.json", "r")
data = file.read()
objects = json.loads(data)

class Events(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, msg):
      pass
    
    @commands.Cog.listener()
    async def on_message(self, message):
           if (message.author.bot):
                return
           if message.content == f"<@!{self.bot.user.id}>" or message.content == f"<@{self.bot.user.id}>":
                prefix = self.bot.cache.prefixes[message.guild.id]["prefix"]
                await message.channel.send(f"**<a:animated_tick:847447732623900672> Hey there! My prefix for this server is `{prefix}`!**")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        res = await self.bot.db.execute("""INSERT INTO prefixes (prefix, guild_id) VALUES ($1, $2)""", 'k!', guild.id)
        await self.bot.cache.check_for_cache()
        await self.bot.cache.cache_all()


    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        res = await self.bot.db.execute("DELETE FROM prefixes WHERE guild_id = $1", guild.id)
        await self.bot.cache.delete_guild_info(guild.id)



    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        if hasattr(ctx.command, 'on_error'):
            return

        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored = (commands.CommandNotFound, )

        error = getattr(error, 'original', error)

        if await self.bot.is_owner(ctx.author) and isinstance(error, Maintenace):
            try:
                return await ctx.reinvoke()
            except Exception:
                pass

        if isinstance(error, Maintenace):
            embed = discord.Embed(description='**This bot is currently on maintenance mode. You cannot use commands**', color=discord.Color.random())
            return await ctx.send(embed=embed)

        if isinstance(error, ignored):
            return

        elif isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(title="<:red_cross:844165297538727956> | No valid member was provided!")
            await ctx.send(embed=embed)
            
        elif isinstance(error, commands.BotMissingPermissions):
            permissions = ", ".join(perm.replace("_", " ").lower() for perm in error.missing_permissions)
            embed = discord.Embed(description=f"**<:red_cross:844165297538727956> | Cannot do that, I don't have the Permissions of `{permissions}`**", color=0xff0000)
            await ctx.send(embed=embed)
            
        elif isinstance(error, commands.MissingPermissions):
            permissions = ", ".join(perm.replace("_", " ").lower() for perm in error.missing_permissions)
            embed=discord.Embed(description=f"**<:red_cross:844165297538727956> | Cannot do that, You don't have the Permissions of `{permissions}`**")
            await ctx.send(embed=embed)
            
        elif isinstance(error, discord.Forbidden):
            embed = discord.Embed(description='I\'m not allowed to do that', color=discord.Color.red())
            await ctx.send(embed=embed)
            
        elif isinstance(error, commands.CheckFailure):
            embed = discord.Embed(description='You are not allowed to use this command', color=discord.Color.blurple())
            await ctx.send(embed=embed)
            
        elif isinstance(error, commands.CommandOnCooldown):
            if not ctx.author.id in owners:
                day = round(error.retry_after/86400)
                hour = round(error.retry_after/3600)
                minute = round(error.retry_after/60)
                if day > 0:
                    embed = discord.Embed(title="Command on Cooldown!", description=f"You need to wait {day} day(s) before using this command again!", color=discord.Color.blurple())
                    await ctx.send(embed=embed)
                elif hour > 0:
                    embed = discord.Embed(title="Command on Cooldown!", description=f"You need to wait {hour} hour(s) before using this command again!", color=discord.Color.blurple())
                    await ctx.send(embed=embed)
                elif minute > 0:
                    embed = discord.Embed(title="Command on Cooldown!", description=f"You need to wait {minute} minute(s) before using this command again!", color=discord.Color.blurple())
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(title="Command on Cooldown!", description=f"You need to wait {error.retry_after:.1f} second(s) before using this command again!", color=discord.Color.blurple())
                    await ctx.send(embed=embed)
            else:
                await ctx.reinvoke()

        elif isinstance(error, commands.MaxConcurrencyReached):
            concurrency = error.number
            embed = discord.Embed(title='Max Concurrency Reached', description=f'This command reached its max concurrency of {concurrency}', color=discord.Color.red())
            await ctx.send(embed=embed)

        elif isinstance(error, commands.MissingRequiredArgument):
            missing = error.param.name
            await ctx.send(f"<a:incorrect:854800103193182249> `{missing}` is a required argument that\'s missing, view `{ctx.prefix}help {ctx.command}` for more info.")

        elif isinstance(error, commands.MissingRequiredFlag):
            missing = error.flag.name
            await ctx.send(f'<a:incorrect:854800103193182249> `{missing}` is a required flag that\'s missing.')
    
        else:
            if ctx.author.id in owners:
                fullerr = "".join(traceback.format_exception(type(error), error, error.__traceback__))
                await ctx.reply(f'```py\n{fullerr}\n```', allowed_mentions=discord.AllowedMentions.none())
                print(f'Error occured in {ctx.guild.name} | ID: {ctx.guild.id}')
                print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
                traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
            else:
                errid = random.randint(1, 9000)
                embed = discord.Embed(title='⚠️ An Error has Occurred', description=f'An internal error has occured, it has been reported to my developers. The ID of this error is `{errid}`', color=discord.Color.red())
                embed.add_field(name='Error occured on', value=f'`{ctx.command}`', inline=False)
                embed.add_field(name='Traceback', value=f"```py\n{error}\n```")
                embed.set_footer(text=f'| Command invoked by {ctx.author}', icon_url=ctx.author.avatar.url)
                await ctx.reply(embed=embed, mention_author=False)
                async with aiohttp.ClientSession() as ses:
                        webhook = Webhook.from_url(objects["LOGS_WEBHOOK"], adapter=AsyncWebhookAdapter(ses))
                        em = discord.Embed(title='Error Occurred!', description=f"```py\n{error}\n```", color=discord.Color.red())
                        em.add_feild(name='Error ID', value=errid)
                        em.add_field(name='Command Invoked By', value=f'{ctx.author.name} (ID: {ctx.author.id})')
                        em.add_field(name='Command', value=ctx.command)
                        em.add_field(name='Guild', value=ctx.guild)
                        await webhook.send(embed=em)
                print(f'Error occured in {ctx.guild.name} | ID: {ctx.guild.id}')
                print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
                traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

def setup(bot):
    bot.add_cog(Events(bot))



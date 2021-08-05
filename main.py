#Importing Stuff
import discord
from discord.ext import commands
from discord.utils import get
import os
import time, datetime
import pwd
from discord.ext import tasks
from datetime import datetime
from utilities.addons.context import KyroContext
from utilities.addons.webhook import Webhook, AsyncWebhookAdapter
import codecs
import pathlib
import json
import asyncpg
import logging
import aiohttp
from aiohttp import ClientSession
import sqlite3, aiosqlite
import asyncio
from utilities.addons.checks import Maintenace, is_blacklisted
from utilities.addons.cache import KyroCache


os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["JISHAKU_HIDE"] = "True"

#Getting JSON Info
file = open("config.json", "r")
data = file.read()
objects = json.loads(data)
		


owners = [812901193722363904, 422854944857784322]
ownerprefix = ['k!', '']


async def get_prefix(bot,  message):
    if message.author.id == 422854944857784322 and bot.noPrefixSomeone == True:
        return ownerprefix
    elif message.author.id == 812901193722363904 and bot.noPrefixHiro == True:
        return ownerprefix
    try:
        
        pref = await bot.cache.get_prefix(message.guild.id)
        return commands.when_mentioned_or(pref)(bot, message)
    except KeyError:
        prefix = await bot.db.fetchrow("SELECT prefix FROM prefixes WHERE guild_id = $1", message.guild.id)
        return commands.when_mentioned_or(prefix["prefix"])(bot, message)

	
intents = discord.Intents.default()

class Kyro(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, 
        command_prefix=get_prefix,
        case_insensitive=True,
        intents=intents,
        allowed_mentions=discord.AllowedMentions(roles=False, users=True, everyone=False), 
        strip_after_prefix=True
        )
        self.owner_ids = [812901193722363904, 422854944857784322]
        self.loop.create_task(self.status())
        self.noPrefixSomeone = True
        self.noPrefixHiro = True
        self.afk = {}
        self._BotBase__cogs  = commands.core._CaseInsensitiveDict()
        self.cache = KyroCache(self)
        self.DebugMode = False
        self.session = aiohttp.ClientSession()
        self.launch_time = datetime.utcnow()
        self.loop.create_task(self.load_extensions())

        @self.check
        async def check(ctx):
          if ctx.bot.DebugMode is True:
            raise Maintenace()
          return True

    async def on_ready(self):
      print("Connected to discord.")
      print(f'Lantecy: {round(self.latency* 1000,2)}')

    async def load_extensions(self):
      await self.wait_until_ready()
      for extension in os.listdir('./cogs'):
        if extension.endswith('.py'):
          try:
            self.load_extension(f'cogs.{extension[:-3]}')
          except Exception as e:
            print(f"Failed to load {extension}: {e} ")
      self.load_extension('utilities.addons.context')

    async def status(self):
      await self.wait_until_ready()
      await self.change_presence(status=discord.Status.online
      , activity=discord.Activity(type=discord.ActivityType.watching, name=f"@Kyro Help | {len(self.guilds)} servers"))

    async def get_context(self, message, *, cls=None):
      return await super().get_context(message, cls=cls or self.context)

    async def on_message(self, message):
      if message.author.bot:
        return


      if message.guild is None:
        return 
        
      if await is_blacklisted(self, message.author):
        return

      prefix = await get_prefix(self, message)
    
      message.content = message.content[:len(prefix)].lower() + message.content[len(prefix):] 

      await self.process_commands(message)


    async def on_message_edit(self, before: discord.Message, after: discord.Message):
          if before.content == after.content:
              return
          if after.attachments:
              return
          await self.process_commands(after)

bot = Kyro()

#Running the Bot 
dbuser = objects['DBUSER']
dbpassword = objects['DBPASSWORD']
bot.db = bot.loop.run_until_complete(asyncpg.create_pool(host='...', port='...', user=dbuser, password=dbpassword, database='...'))
TOKEN = objects["TOKEN"]
if __name__ == "__main__" :
  bot.run(TOKEN) 

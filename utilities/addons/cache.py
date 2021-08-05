
import discord
from discord.ext import tasks

class KyroCache:
  def __init__(self, bot):
    self.bot = bot
    self.cache_loop.start()
    self.prefixes = {}
    self.blacklisted = {}


  @tasks.loop(minutes=5)
  async def cache_loop(self):
        await self.check_for_cache()
        await self.cache_all()

  @cache_loop.before_loop
  async def before_cache_loop(self):
        await self.bot.wait_until_ready()
  
  async def check_for_cache(self):
    cache_list = [
      self.prefixes,
    ]
    for guild in self.bot.guilds:
      for cache in cache_list:
        if guild.id not in cache:
          cache[guild.id] = {}
    
  async def delete_guild_info(self, guild_id:int):
      await self.bot.db.execute("DELETE FROM prefixes WHERE guild_id = $1", guild_id)
      self.prefixes.pop(guild_id)
    
  async def get_prefix(self, guild_id:int):
      guild = self.prefixes.get(guild_id)
      return guild.get('prefix')

    
    
  async def cache_all(self):
    pref = await self.bot.db.fetch("SELECT * FROM prefixes")
    blacklist = await self.bot.db.fetch("SELECT * FROM blacklisted")
    for entry in pref:
      pr = dict(entry)
      pr.pop("guild_id")
      self.prefixes[entry["guild_id"]] = pr
    
    for entry in blacklist:
      self.blacklisted[entry["member_id"]] = entry["reason"]
      
       
    

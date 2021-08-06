import discord
from discord.ext import commands

def convert(time):
    pos = ["s", "m", "h", "d"]
    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 3600 * 24}
    unit = time[-1]

    if unit not in pos:
        return -1
    try:
        val = int(time[:-1])
    except:
        return -2

    return val * time_dict[unit]

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def can_use_giveaways():
        async def predicate(ctx):
            if ctx.author.guild_permissions.manage_guild or "giveaways" in (
                role.name.lower() for role in ctx.author.roles
            ):
                return True
            await ctx.send("**You either need `giveaways` role or `manage server` permissions to use this command!**")
            return False

        return commands.check(predicate)

    @commands.Cog.listener()  # What is this for!?!?!!??
    async def on_message(self, message):
        return

def setup(bot):
    bot.add_cog(Giveaway(bot))

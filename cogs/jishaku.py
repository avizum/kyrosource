import discord
import jishaku
from discord.ext import commands
from jishaku.cog import STANDARD_FEATURES, OPTIONAL_FEATURES
from jishaku.features.baseclass import Feature
import humanize, datetime
import psutil
import sys



class Jishaku(*OPTIONAL_FEATURES, *STANDARD_FEATURES):
    @Feature.Command(name='jishaku', aliases=['jsk'], invoke_without_command=True)
    async def jsk(self, ctx: commands.Context):
        summary = [
            f"Jishaku v{jishaku.__version__}, discord.py v{discord.__version__}, "
            f"Python {sys.version} running on {sys.platform} ".replace("\n", ""),
            ""
        ]
        proc = psutil.Process()
        with proc.oneshot():
            try:
                mem = proc.memory_full_info()
                summary.append(
                    f"Using {humanize.naturalsize(mem.rss)} physical memory and "
                    f"{humanize.naturalsize(mem.vms)} virtual memory, "
                    f"{humanize.naturalsize(mem.uss)} of which is unique this this process."
                )
            except psutil.AccessDenied:
                pass
            try:
                name = proc.name()
                pid = proc.pid
                thread_count = proc.num_threads()
                summary.append(
                    f"Running on PID {pid} ({name}) with {thread_count} thread(s)")
            except psutil.AccessDenied:
                pass
            summary.append("")

        members = len([m for m in self.bot.users if not m.bot])

        cache_summary = f"{len(self.bot.guilds)} guilds and {members} users"

        if isinstance(self.bot, discord.AutoShardedClient):
            summary.append(f"This bot is automatically sharded and can see {cache_summary}")
        elif self.bot.shard_count:
            summary.append(f"This bot is manually sharded and can see {cache_summary}")
        else:
            summary.append(f"This bot is not sharded and can see {cache_summary}.")

        presence_intent = f"presences {'enabled' if self.bot.intents.presences else 'disabled'}"
        members_intent = f"members {'enabled' if self.bot.intents.members else 'disabled'}"
        summary.append(f"Intents: {presence_intent} and {members_intent}")
        summary.append("")

        embed = discord.Embed(description="\n".join(summary), color=0x2F3136)
        embed.set_author(name='Jishaku', icon_url=ctx.me.avatar.url)
        embed.set_footer(text=f"Websocket latency: {round(self.bot.latency * 1000)}ms", icon_url=ctx.author.avatar.url)
        await ctx.reply(embed=embed, mention_author=False)

def setup(bot: commands.Bot):
    bot.add_cog(Jishaku(bot=bot))

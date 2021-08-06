import discord
from discord.ext import commands


class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_ban(self, guild:discord.Guild, user:discord.User):
        chann = await self.bot.db.fetch("SELECT channel FROM logs WHERE guild_id = $1", guild.id)
        if not chann:
            return
        raw_channel_id = list(chann[0])
        channel_id = raw_channel_id[0]
        channel = self.bot.get_channel(channel_id)
        entry = (await guild.audit_logs(limit=1, action=discord.AuditLogAction.ban).flatten())[0]
        embed = discord.Embed(title='Member Banned', color=0x2F3136, timestamp=discord.utils.utcnow())
        embed.add_field(name='Member Banned', value=f'{entry.target} ({entry.target.id})', inline=False)
        embed.add_field(name='Moderator', value=entry.user.mention, inline=False)
        embed.add_field(name='Ban Reason', value=entry.reason or "N/A", inline=False)
        embed.set_thumbnail(url=user.avatar.url)
        await channel.send(embed=embed)


    @commands.command(name='set-logs')
    @commands.has_permissions(manage_guild=True)
    async def settinglogs(self, ctx, channel:discord.TextChannel):
        chann = await self.bot.db.fetch("SELECT channel FROM logs WHERE guild_id = $1", ctx.guild.id)
        if not chann:
            if not channel in ctx.guild.channels:
                embed = discord.Embed(description="<a:incorrect:854800103193182249> Cannot find this channel, make sure i have access to that channel.", color=discord.Color.red())
                return await ctx.send(embed=embed)
            else:
                adding = await self.bot.db.execute("INSERT INTO logs (channel, guild_id) VALUES ($1, $2)", int(channel.id), ctx.guild.id)
                embed = discord.Embed(description=f"**<:green_tick:844165352610725898> Set {channel} as the log's channel.**", color=discord.Color.green())
                return await ctx.send(embed=embed)
        else:
            if not channel in ctx.guild.channels:
                return await ctx.send('<a:incorrect:854800103193182249> Cannot find this channel.')
            else:
                adding = await self.bot.db.execute("UPDATE logs SET channel = $1 WHERE guild_id = $2", int(channel.id), ctx.guild.id)
                embed = discord.Embed(description=f"**<:green_tick:844165352610725898> Set {channel} as the log's channel.**", color=discord.Color.green())
                return await ctx.send(embed=embed)

    @commands.command(name='remove-logs')
    @commands.has_permissions(manage_guild=True)
    async def tologs(self, ctx):
        removing = await self.bot.db.execute("DELETE FROM logs WHERE guild_id = $1", ctx.guild.id)
        embed = discord.Embed(description="**<:green_tick:844165352610725898> Removed logs channel.**", color=discord.Color.green())
        await ctx.reply(embed=embed)


def setup(bot):
    bot.add_cog(Logging(bot))

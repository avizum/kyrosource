import discord
from discord.ext import commands
import asyncio
from jishaku.functools import executor_function
import io 
import asyncpg

owners = [422854944857784322, 812901193722363904]

async def get_tag(ctx, name):
    res = await ctx.bot.db.fetch('SELECT * FROM tags WHERE serverid = $1', ctx.guild.id)
    for tag in res:
        if dict(tag)["name"].lower() == name.lower():
            return tag

async def already_exists(ctx,name):
    res = await ctx.bot.db.fetch("SELECT * FROM tags WHERE serverid = $1", ctx.guild.id)
    tag = None
    for tag_ in res:
        if dict(tag_)["name"].lower() == name.lower():
            tag = tag_
    return tag is not None

async def tag_is_owner(ctx, name):
    res = await ctx.bot.db.fetchrow("SELECT * FROM tags WHERE serverid = $1 AND name = $2", ctx.guild.id, name)
    owner = int(res["authorid"])
    return bool(
        ctx.author.id == owner
        or ctx.author.guild_permissions.manage_guild
        or ctx.author.id in owners
    )

@executor_function
def getFile(text, end="txt", filename="message"):
    f = io.StringIO()
    f.write(text)
    f.seek(0)
    return discord.File(f, filename=f"{filename}.{end}")


class Tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @commands.cooldown(1,5,commands.BucketType.user)
    async def tag(self, ctx, *, tag: commands.clean_content):
        if not await already_exists(ctx, tag):
            return await ctx.send("** :label: Cannot find this tag in this server**")
        tag = await get_tag(ctx, tag)
        name = tag["name"]
        content = tag["content"]
        await ctx.send(content, allowed_mentions=discord.AllowedMentions.none())

    @tag.command()
    @commands.cooldown(1,5,commands.BucketType.user)
    async def create(self, ctx, name, *, content):
        names = ['edit', 'all', 'create', 'remove']
        if await already_exists(ctx, name):
            return await ctx.send("**A tag with that name already exists in this server!**")
        elif len(content) > 1000:
            return await ctx.send("**A tag can not be bigger than 1000 characters**")
        elif len(name) < 1:
            return await ctx.send("**The name of the tag must be atleast 1 characters long, and doesnt have any invisible characters**")
        elif name in names:
            return await ctx.send("**The name of the tag cannot be a command name**")
        else:
            await self.bot.db.execute("INSERT INTO tags (name, content, serverid, authorid) VALUES ($1, $2, $3, $4)", name, content, ctx.guild.id, ctx.author.id)
            await ctx.send(f":label: **Successfully Created your tag with name** \"`{name}`\"")

    @tag.command()
    @commands.cooldown(1,5,commands.BucketType.user)
    async def all(self, ctx):
        records = sorted(await self.bot.db.fetch("SELECT * FROM tags WHERE serverid = $1", ctx.guild.id))
        if records != [] and len(records) != 0:
            text = "\n".join(f"{text['name']}" for text in records)
            return await ctx.reply(file=await getFile(text, filename="tags"), mention_author=False)   

    @tag.command()
    @commands.cooldown(1,5,commands.BucketType.user)
    async def edit(self, ctx, name, *, new_desc):
        if not await already_exists(ctx, name):
            return await ctx.send("** :label: Cannot find this tag in this server**")
        elif not await tag_is_owner(ctx, name):
            return await ctx.send(":label: **You do not own that tag, means you cannot edit it!**") 
        else:
            await self.bot.db.execute("UPDATE tags SET content = $1 WHERE name = $2 AND serverid = $3", new_desc, name, ctx.guild.id)
            await ctx.send(f":label: **Edited your tag named** `{name}`")

    @tag.command()
    @commands.cooldown(1,5,commands.BucketType.user)
    async def remove(self, ctx, name):
        if not await already_exists(ctx, name):
            return await ctx.send("** :label: Cannot find this tag in this server**")
        elif not await tag_is_owner(ctx, name):
            return await ctx.send(":label: **You do not own that tag, means you cannot remove it!**") 
        else:
            await self.bot.db.execute("DELETE FROM tags WHERE name = $1 AND serverid = $2", name, ctx.guild.id)
            await ctx.send(f":label: **Removed your tag named** `{name}`")


def setup(bot):
    bot.add_cog(Tags(bot))

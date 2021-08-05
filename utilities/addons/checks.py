from discord.ext import commands

async def is_blacklisted(bot, user):
    if user.id in bot.cache.blacklisted:
        return True
    return False
    # res = await bot.db.fetchrow("SELECT * FROM blacklist WHERE member_id = $1", user.id)
    # if res is None:
    #     return False
    # else:
    #     raw_id = res["member_id"]
    #     if str(user.id) in str(raw_id):
    #         return True


class Maintenace(commands.CheckFailure):
    pass
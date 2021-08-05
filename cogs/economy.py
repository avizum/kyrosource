import discord
from discord.ext import commands
import random
import asyncio

class Economy(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.currency = "<a:moneh:867632385569587260>"
        self.welcome_economy_message = "**Welcome to Kyro's Economy system! I have made a account for you!**"

    @commands.Cog.listener()
    async def on_message(self, msg):
        pass
    
    @commands.command(aliases=['bal'], help='Checking your or someone else account balance')
    @commands.cooldown(1,5,commands.BucketType.user)
    async def balance(self, ctx, user:discord.Member=None):
        if user is None:
            user = ctx.author
        res1 = await self.bot.db.fetchrow("SELECT balance FROM accounts WHERE user_id = $1", user.id)
        res2 = await self.bot.db.fetchrow("SELECT wallet FROM accounts WHERE user_id = $1", user.id)
        if (res1 == None) or (res2 == None):
          if user is ctx.author:
            await self.bot.db.execute("INSERT INTO accounts (balance, wallet, user_id) VALUES ($1, $2, $3)", '500', '500', ctx.author.id)
            return await ctx.reply(self.welcome_economy_message)
          else:
            return await ctx.send(f"I couldnt find that user in the database, tell them to run `{ctx.prefix}bal` so i can add them!")   
        balance = res1["balance"]
        wallet = res2["wallet"] 
        moneysum = int(wallet) + int(balance)
        embed = discord.Embed(description = f"**{self.currency} Wallet Balance**: ${wallet}\n**{self.currency} Bank Balance:** ${balance}\n**{self.currency} Total Balance:** ${moneysum}",color=discord.Color.random(), timestamp=discord.utils.utcnow())
        embed.set_author(name=f'{user}\'s balance', icon_url=user.avatar.url)
        embed.set_footer(text="Kyro")
        await ctx.send(embed=embed)
    
    @commands.command(aliases=['dep'], help='Deposits money into your bank')
    @commands.cooldown(1,5,commands.BucketType.user)
    async def deposit(self, ctx, amount):
        res1 = await self.bot.db.fetchrow("SELECT wallet FROM accounts WHERE user_id = $1", ctx.author.id)
        res2 = await self.bot.db.fetchrow("SELECT balance FROM accounts WHERE user_id = $1", ctx.author.id)
        if (res1 == None) or (res2 == None):
            await self.bot.db.execute("INSERT INTO accounts (balance, wallet, user_id) VALUES ($1, $2, $3)", '500', '500', ctx.author.id)
            return await ctx.reply(self.welcome_economy_message)
        current_bank  = res2["balance"]
        current_wallet = res1["wallet"]
        if amount == 'all':
            amount = int(current_wallet)
        if int(amount) > int(current_wallet):
            return await ctx.reply("**😏 Nope you cant trick me, You do not have this amount of money in your wallet to deposit**")
        to_be_removed_from_w = str(int(current_wallet) - int(amount))
        to_be_added_to_b = str(int(current_bank) + int(amount))
        removing_from_w = await self.bot.db.execute("UPDATE accounts SET wallet = $1 WHERE user_id = $2", to_be_removed_from_w, ctx.author.id)
        adding_to_b = await self.bot.db.execute("UPDATE accounts SET balance = $1 WHERE user_id = $2", to_be_added_to_b, ctx.author.id)
        a = random.randint(1, 5000)
        if a < 4999:
            msg = f"**<a:moneh:867632385569587260> ${amount}** was sucessfully transferred to your bank balance"
        elif a == 5000:
            msg = f"**<a:moneh:867632385569587260> ${amount}** ∴ᔑᓭ ℸ ̣ ⍑∷𝙹∴リ ℸ ̣ 𝙹 ||𝙹⚍∷ ʖᔑリꖌ ʖᔑꖎᔑリᓵᒷ"
        await ctx.reply(msg, mention_author=False)
    
    @commands.command(aliases=["with"], help='Withdraws money from your bank')
    @commands.cooldown(1,5,commands.BucketType.user)
    async def withdraw(self, ctx, amount):
        res1 = await self.bot.db.fetchrow("SELECT wallet FROM accounts WHERE user_id = $1", ctx.author.id)
        res2 = await self.bot.db.fetchrow("SELECT balance FROM accounts WHERE user_id = $1", ctx.author.id)
        if (res1 == None) or (res2 == None):
            await self.bot.db.execute("INSERT INTO accounts (balance, wallet, user_id) VALUES ($1, $2, $3)", '500', '500', ctx.author.id)
            return await ctx.reply(self.welcome_economy_message)
        current_bank  = res2["balance"]
        current_wallet = res1["wallet"]
        if amount == 'all':
            amount = int(current_bank)
        if int(amount) > int(current_bank):
            return await ctx.reply("**You do not have this amount of money in your bank to withdraw, Go earn some money lol :joy:**", mention_author=False)
        to_be_removed_from_b = str(int(current_bank) - int(amount))
        to_be_added_to_w = str(int(current_wallet) + int(amount))
        removing_from_b = await self.bot.db.execute("UPDATE accounts SET balance = $1 WHERE user_id = $2", to_be_removed_from_b, ctx.author.id)
        adding_to_w = await self.bot.db.execute("UPDATE accounts SET wallet = $1 WHERE user_id = $2", to_be_added_to_w, ctx.author.id)
        await ctx.reply(f"<a:moneh:867632385569587260> **${amount}** was sucessfully withdrawn into your **wallet** from your **bank**", mention_author=False)
        
    @commands.command(help='Earn Money by working')
    @commands.cooldown(1,300,commands.BucketType.user)
    async def work(self, ctx):
        raw_current_bal = await self.bot.db.fetchrow("SELECT balance FROM accounts WHERE user_id = $1", ctx.author.id)
        if raw_current_bal is None:
            await self.bot.db.execute("INSERT INTO accounts (balance, wallet, user_id) VALUES ($1, $2, $3)", '500', '500', ctx.author.id)
            return await ctx.reply(self.welcome_economy_message)
        current_bal = raw_current_bal["balance"]
        earned = random.randint(150, 1000)
        to_be_added = str(int(current_bal) + earned)
        adding_bal = await self.bot.db.execute("UPDATE accounts SET balance = $1 WHERE user_id = $2", to_be_added, ctx.author.id)
        work_choices = ['policemen', 'firefighter', 'smartphone maker', 'teacher', 'Kyro\'s Epic Developer', 'youtuber', 'memer', 'bruhminati', 'car maker', 'stock marketer', 'lawyer', 'journalist', 'tourst agent', 'dictator', 'president', 'captain', 'pilot', 'doctor', 'military officer', 'developer']
        work_choice = random.choice(work_choices)
        await ctx.reply(f"You have worked as a **{work_choice}** and earned **{self.currency} {earned}**", mention_author=False)

    @commands.command(help='Begs for money')
    @commands.cooldown(1,60, commands.BucketType.user)
    async def beg(self, ctx):
        raw_current_bal = await self.bot.db.fetchrow("SELECT wallet FROM accounts WHERE user_id = $1", ctx.author.id)
        if raw_current_bal is None:
            await self.bot.db.execute("INSERT INTO accounts (balance, wallet, user_id) VALUES ($1, $2, $3)", '500', '500', ctx.author.id)
            return await ctx.reply(self.welcome_economy_message)
        str_current_bal = raw_current_bal["wallet"]
        current_bal = int(str_current_bal)
        earned = random.randint(50, 750)
        to_be_added = str(current_bal + earned)
        adding_bal = await self.bot.db.execute("UPDATE accounts SET wallet = $1 WHERE user_id = $2", to_be_added, ctx.author.id)
        people_choices = ['Elon Musk', 'Apple CEO', 'The President', 'Someone', 'Hiro', 'Discord', 'Facebook CEO', 'Microsoft', 'Epic Games', 'Elon Musc', 'Kyro\'s economy code', 'dababy lessss go', 'Doge', 'HOOOOG RAIIIDDEERRRR', 'DreamWasTaken', 'Da Micky Mouse', 'SoundDrout', 'Donor Name Here', 'THICCDANI', 'SpaceX']
        donated = random.choice(people_choices)
        await ctx.reply(f"**{donated}** has donated **{self.currency} {earned}** to **{ctx.author.name}**", mention_author=False)

    @commands.command(help='Robbing someone to get money')
    @commands.cooldown(1,600, commands.BucketType.user)
    async def rob(self, ctx, user:discord.Member):
        if user is ctx.author:
            return await ctx.send("**Uhh you cannot rob urself**")
        raw_authors_bal = await self.bot.db.fetchrow("SELECT wallet FROM accounts WHERE user_id = $1", ctx.author.id)
        if raw_authors_bal is None:
            await self.bot.db.execute("INSERT INTO accounts (balance, wallet, user_id) VALUES ($1, $2, $3)", '500', '500', ctx.author.id)
            return await ctx.reply(self.welcome_economy_message)
        authors_bal = raw_authors_bal["wallet"]
        raw_target_bal = await self.bot.db.fetchrow("SELECT wallet FROM accounts WHERE user_id = $1", user.id)
        target_bal = raw_target_bal["wallet"]
        if int(authors_bal) < 500:
            e = discord.Embed(description=f'**You need atleast {self.currency} 500 in your wallet to rob someone!**', color=discord.Color.red())
            return await ctx.send(embed=e)
        if int(target_bal) < 500:
            em = discord.Embed(description=f'**Not worth to rob them, they dont even have {self.currency} 500 in their wallet**', color=discord.Color.red())
            return await ctx.send(embed=em)
        got_choices = ['yes', 'no']
        got = random.choice(got_choices)
        if got == 'yes':
            taken = random.randint(50, int(target_bal))
            to_be_added = str(int(authors_bal) + taken)
            to_be_removed = str(int(target_bal) - taken)
            adding_bal = await self.bot.db.execute("UPDATE accounts SET wallet = $1 WHERE user_id = $2", to_be_added, ctx.author.id)
            removing_bal = await self.bot.db.execute("UPDATE accounts SET wallet = $1 WHERE user_id = $2", to_be_removed, user.id)
            embed = discord.Embed(description=f'**Your robbed {user.mention} and your payout was {self.currency} {taken}**', color=discord.Color.green(), timestamp=discord.utils.utcnow())
            embed.set_footer(text=f'{ctx.author.name} robbed {user.name}')
            await ctx.send(embed=embed)
        else:
            money_to_pay = random.choice(50, 450)
            payed = str(int(authors_bal) - money_to_pay)
            paying = await self.bot.db.execute("UPDATE accounts SET wallet = $1 WHERE user_id = $2", payed, ctx.author.id)
            embed = discord.Embed(description=f'**You got caught by the police and had to pay {self.currency} {payed} to them**', color=discord.Color.red(), timestamp=discord.utils.utcnow())
            await ctx.send(embed=embed)

    @commands.command(help='Bet a amount of money, and either earn dont get anything or lose')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def slots(self, ctx, amount):
      raw_authors_bal = await self.bot.db.fetchrow("SELECT wallet FROM accounts WHERE user_id = $1", ctx.author.id)
      if raw_authors_bal is None:
        await self.bot.db.execute("INSERT INTO accounts (balance, wallet, user_id) VALUES ($1, $2, $3)", '500', '500', ctx.author.id)
        return await ctx.send(self.welcome_economy_message)
      authors_bal = raw_authors_bal["wallet"]
      if amount == 'all':
          amount = int(authors_bal)
      elif int(amount) < 100:
        return await ctx.reply(f"**You need to bet at least {self.currency} 100 in this command to bet**")
      emojis = ["🍎", "🍊", "🍋", "🍉", "🍇", "🍓", "💎"]
      a = random.choice(emojis)
      b = random.choice(emojis)
      c = random.choice(emojis)
      slotmachine = f"`____SLOTS____`\n**[ {a} | {b} | {c} ]**"
      if (a == b == c):
        to_be_added = str(int(authors_bal) + int(amount))
        changing = await self.bot.db.execute("UPDATE accounts SET wallet = $1 WHERE user_id = $2", to_be_added, ctx.author.id)
        await ctx.send(f"{slotmachine}\n**{ctx.author.name} slots __{self.currency} {amount}__ and won the bet! 🎉 🎉**")
      elif (a == b) or (a == c) or (b == c):
        await ctx.send(f"{slotmachine}\n**{ctx.author.name} slots {self.currency} {amount} and got 2 in a row, So they didn't lose anything 🎉**")
      else:
        to_be_removed = str(int(authors_bal) - int(amount))
        changing = await self.bot.db.execute("UPDATE accounts SET wallet = $1 WHERE user_id = $2", to_be_removed, ctx.author.id)
        await ctx.send(f"{slotmachine}\n**{ctx.author.name} slots __{self.currency} {amount}__ but sadly lost the bet, :smiling_face_with_tear:**")
            
    @commands.command(help='Gets your daily money')
    @commands.cooldown(1,86400,commands.BucketType.user)
    async def daily(self, ctx):
        raw_current_bal = await self.bot.db.fetchrow("SELECT balance FROM accounts WHERE user_id = $1", ctx.author.id)
        if raw_current_bal is None:
            await self.bot.db.execute("INSERT INTO accounts (balance, wallet, user_id) VALUES ($1, $2, $3)", '500', '500', ctx.author.id)
            return await ctx.reply(self.welcome_economy_message)
        current_bal = raw_current_bal["balance"]
        daily = random.randint(1500, 4500)
        to_be_added = str(int(current_bal) + daily)
        adding_bal = await self.bot.db.execute("UPDATE accounts SET balance = $1 WHERE user_id = $2", to_be_added, ctx.author.id)
        name = ['Hiro', 'Someone', 'Kyro', 'Discord']
        embed = discord.Embed(title="Here's your daily cash", description=f'You have been given {self.currency} {daily} from **{random.choice(name)}**!', color=discord.Color.random(), timestamp=discord.utils.utcnow())
        embed.set_author(name=f'{ctx.author.name}', icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="add-money")
    @commands.is_owner()
    async def addmoney(self, ctx, user: discord.Member, moneh):
        raw_current_bal = await self.bot.db.fetchrow("SELECT balance FROM accounts WHERE user_id = $1", user.id)
        current_bal = raw_current_bal["balance"]
        to_be_added = str(int(current_bal) + int(moneh))
        adding_bal = await self.bot.db.execute("UPDATE accounts SET balance = $1 WHERE user_id = $2", to_be_added, user.id)
        await ctx.send(f"**Sucessfully added __{self.currency} {moneh}__ to {user.mention}'s Bank balance**")
    
    @commands.command(help='Mining to earn money')
    @commands.cooldown(1,60,commands.BucketType.user)
    async def mine(self, ctx):
        raw_current_bal = await self.bot.db.fetchrow("SELECT balance FROM accounts WHERE user_id = $1", ctx.author.id)
        if raw_current_bal is None:
            await self.bot.db.execute("INSERT INTO accounts (balance, wallet, user_id) VALUES ($1, $2, $3)", '500', '500', ctx.author.id)
            return await ctx.reply(self.welcome_economy_message)
        current_bal = raw_current_bal["balance"]
        pic = random.randint(1, 100)
        if pic > 50:
            amount = random.randint(400, 700)
        else:
            amount = random.randint(40,400)
        to_be_added = str(int(current_bal) + amount)
        adding_bal = await self.bot.db.execute("UPDATE accounts SET balance = $1 WHERE user_id = $2", to_be_added, ctx.author.id)
        embed = discord.Embed(description=f'**You have got {self.currency} {amount} and used {pic}% of your pickaxe**', color=discord.Color.random())
        await ctx.send(embed=embed)




        
def setup(bot):
    bot.add_cog(Economy(bot))

    

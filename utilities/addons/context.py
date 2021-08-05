import discord
from discord.ext import commands
import typing
import os
import asyncio
import json

file = open("config.json", "r")
data = file.read()
objects = json.loads(data)
webhooks = objects["LOGS_WEBHOOK"]

class View(discord.ui.View):
    def __init__(self, timeout, ctx):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        
    async def interaction_check(self, interaction):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message(content=f"<:red_cross:844165297538727956> | You are not the owner of this message", ephemeral=True)
        return True
            
    @discord.ui.button(label='🗑️', style=discord.ButtonStyle.grey, custom_id='Clear Message')
    async def callback(self, button, interaction:discord.Interaction):
        await interaction.message.delete()

class Confirm(discord.ui.View):
    def __init__(self, timeout: int, ctx):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.value = None


    async def interaction_check(self, interaction):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message('This is not your menu.', ephemeral=True)
        return True


    @discord.ui.button(label='Yes', style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = True
        self.stop()


    @discord.ui.button(label='No', style=discord.ButtonStyle.danger)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = False
        self.stop()
            
class KyroContext(commands.Context):
        
    async def reply(self, content=None, *args, **kwargs):
        if content is not None:
            content = (content
            .replace(self.bot.http.token, "[Token]")
            .replace(webhooks, "[Webhook]"))

        allowed_mentions = kwargs.pop("allowed_mentions", None)
        try:
            if allowed_mentions is None:
                return await self.reply(content=content, mention_author=False, allowed_mentions=discord.AllowedMentions.none(), *args, **kwargs)
            else:
                return await self.reply(content=content, mention_author=False *args, **kwargs)
        except Exception:
            return await super().reply(content=content, *args, **kwargs)
        

    
    async def trash(self, *args, **kwargs):
        view = View(timeout=30, ctx=self)
        await self.send(*args, **kwargs, view=view)
    
    async def confirm(self, *args, **kwargs):
        view = Confirm(timeout=60, ctx=self)
        send = await self.send(*args, **kwargs, view=view)
        await view.wait()
        return view.value




def setup(bot):
    bot.context = KyroContext

def teardown(bot):
    bot.context = commands.Context


import discord
from discord.ext import commands

class KyroHelp(commands.HelpCommand):

    def get_command_signature(self, command):
            return '%s%s %s' % (self.context.clean_prefix, command.qualified_name, command.signature)

    async def send_bot_help(self, mapping):
        embed = discord.Embed(description=f"<:guild_prefix:858288131269984256> **Prefix:** `{self.context.clean_prefix}` | **Commands:** {len(self.context.bot.commands)}", color=discord.Color.random())
        embed.set_author(name=str(self.context.author.name), icon_url=self.context.author.avatar.url)
        embed.add_field(name="<:module:858294096454746112> Modules:", value="•  **Fun**\n• **Images**\n• **Music**\n• **Utilities**\n• **Moderation**\n• **Tags**\n• **Economy**")
        embed.add_field(name=":newspaper:  Kyro | Latest", value="`+` Added `america` and `communism` command\n`+` Added `hack` and `flip` command\n`+` Added `suggest` and `pypi` command")
        embed.set_footer(text=f"Type \"{self.context.clean_prefix}help [Command | Module]\"for more information")
        channel = self.get_destination()
        view = discord.ui.View() 
        style = discord.ButtonStyle.gray  
        item = discord.ui.Button(style=style, label="Invite Me!", url="https://discord.com/oauth2/authorize?client_id=844154929815748649&scope=bot&permissions=271887566") 
        view.add_item(item=item) 
        await channel.send(embed=embed, view=view)

    async def send_command_help(self, command):
        signature = self.get_command_signature(command)
        embed = discord.Embed(title=signature, color=discord.Color.random(), description=command.help or 'No help found for this command.')
        embed.set_author(name=self.context.author.name, icon_url=self.context.author.avatar.url)
        if command._buckets and (cooldown := command._buckets._cooldown):
            embed.add_field(
                name="Cooldown",
                value=f"{cooldown.rate} per {cooldown.per:.0f} seconds")
        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_cog_help(self, cog):
        call = cog.qualified_name or "None"
        channel = self.get_destination()
        embed = discord.Embed(title=f'{str(call)} Module', description='   '.join(f"`{command.qualified_name}`" for command in cog.get_commands()), color=discord.Color.random())
        embed.set_author(name=self.context.author.name, icon_url=self.context.author.avatar.url)

        await channel.send(embed=embed)

    async def send_error_message(self, error):
        return


class Help(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        help_command = KyroHelp()
        help_command_cog = self
        bot.help_command = help_command

    def cog_unload(self):
        self.bot.help_command = commands.MinimalHelpCommand()

def setup(bot):
    bot.add_cog(Help(bot))

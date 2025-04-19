import discord
from discord.ext import commands
from module.Database import Database
from module.ChatAi import ChatAi
from module.Charactor import Charactor
import os
from dotenv import load_dotenv


class Nezumikun(commands.Bot):
    """
    botのコア
    参考：
        Cogs and Slash Commands [Discord.py v2.0+]
        https://youtu.be/U0Us5NHG-nY

        Discord dev portal
        https://discord.com/developers/applications/

        その他わからないことはDiscord.pyの公式Discordサーバーで探せばだいたい解決する
    """

    def __init__(self, application_id):

        super().__init__(
            command_prefix='/nezumi_debug',
            intents=discord.Intents.all(),
            self_bot=False,
            applicacation=application_id
        )
        self.database = Database()
        self.charactor = Charactor()
        self.chatAi = ChatAi(self.database, self.charactor)

    async def setup_hook(self) -> None:
        await self.load_extension('cogs.Basic')
        await self.load_extension('cogs.GameUpdate')
        await self.load_extension('cogs.Talk')
        await self.load_extension('cogs.SetStatus')

    async def on_ready(self) -> None:
        print('connected.')


load_dotenv()  # .env ファイルから環境変数を読み込む
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
APPLICATION_ID = os.getenv('APPLICATION_ID')

bot = Nezumikun(APPLICATION_ID)
bot.run(DISCORD_TOKEN)

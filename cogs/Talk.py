import discord
from discord import app_commands
from discord.ext import commands, tasks
import random


class Talk(commands.Cog):
    """
    トークCog
    ネズミくんの会話に関わる基本機能
    """
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.loop.start()

        self.message_probability = 0

    @tasks.loop(hours=1)
    async def loop(self):
        """
        自動発言用ループ
        一定時間ごとに発言させる
        """
        if random.random() < self.message_probability:
            habitat_channel_ids = self.bot.database.get_habitat_channel_ids()
            self.message_probability = 0
            for habitat_channel_id in habitat_channel_ids:
                channel = self.bot.get_channel(habitat_channel_id)
                if channel:
                    response_text = self.bot.chatAi.chat(
                        habitat_channel_id,
                        "[システムメッセージ] 今のあなたの様子・状態・生活などのロールプレイを自由にしてください。",
                        "朝は目覚めたり朝食を摂る、昼は自由に過ごしたり仕事をする、夜は就寝準備や眠りに落ちるなど、現在の時間帯に沿った生活感のあるロールプレイをしなさい。"
                        "ただし、自分の直近の行動に似た行動を取るな。"
                    )
                    await channel.send(response_text)
        self.message_probability = min(self.message_probability + 0.6, 1.0)

    @commands.Cog.listener("on_message")
    async def on_message(self, message) -> None:
        """
        on_messageイベント
        """
        # Botの発言には反応しない
        if message.author.bot:
            return

        # 隠しコマンド: コマンドツリーの同期
        if "必殺！コマンド同期！" in message.content:
            synced = await self.bot.tree.sync()

        # 生息地以外のメッセージには反応しない
        channel_id = message.channel.id
        habitat_channel_ids = self.bot.database.get_habitat_channel_ids()
        if channel_id not in habitat_channel_ids:
            return

        # 自分に向けたメンションならリアクション
        if self.bot.user.mentioned_in(message):
            reply = self.bot.chatAi.chat(channel_id, message.content)
            await message.channel.send(reply)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Talk(bot))

import discord
from discord.ext import commands, tasks
from discord import app_commands
import random


class Basic(commands.Cog):
    """
    Basic Cog
    生息チャンネルの追加など、discord botとしての基本機能を実装するファイル。
    新しい機能を追加する場合は、都度別のCogに切り分ける必要がないか考えること。
    """
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="ネズミくんを呼ぶ",
        description="このチャンネルにネズミくんが住み着くようになります。"
    )
    async def come_on(self, interaction: discord.Interaction):
        """
        ネズミくんを呼ぶコマンド
        生息チャンネルを追加
        """
        channel_id = interaction.channel.id
        habitat_channel_ids = self.bot.database.get_habitat_channel_ids()
        if channel_id not in habitat_channel_ids:
            await interaction.response.defer()  # 入力中...の表示
            self.bot.database.add_habitat_channel_id(channel_id)
            response_text = self.bot.chatAi.chat(channel_id, "[システムメッセージ]あなたはまっさらな新天地に来ました。感想を述べてください。")
            await interaction.followup.send(
                response_text,
                ephemeral=False
            )
        else:
            await interaction.response.send_message(
                f"```このチャンネルにはもうネズミくんがいるみたいです。```",
                ephemeral=False
            )

    @app_commands.command(
        name="さよならネズミくん",
        description="ネズミくんをこのチャンネルから追い出します。"
    )
    async def bye(self, interaction: discord.Interaction):
        """
        さよならネズミくんコマンド
        生息チャンネルを追加
        """
        channel_id = interaction.channel.id
        habitat_channel_ids = self.bot.database.get_habitat_channel_ids()
        if channel_id in habitat_channel_ids:
            await interaction.response.defer()  # 入力中...の表示
            response_text = self.bot.chatAi.chat(channel_id, "[システムメッセージ]あなたはこことは違う新しい場所へ冒険することになりました。旅立っていなくなるロールプレイをしてください。")
            await interaction.followup.send(
                response_text,
                ephemeral=False
            )
            self.bot.database.delete_habitat_channel_id(channel_id)
        else:
            await interaction.response.send_message(
                f"```このチャンネルにはネズミくんがいないみたいです。```",
                ephemeral=False
            )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Basic(bot))

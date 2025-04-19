import discord
from discord.ext import commands, tasks
from discord import app_commands
import random


class SetStatus(commands.Cog):
    """
    SetStatus Cog
    キャラクターの状態を管理するCog
    """
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="見つめる",
        description="ネズミをよく見てみます。"
    )
    async def look(self, interaction: discord.Interaction):
        """
        見つめるコマンド
        現在のステータスを表示する
        """
        channel_id = interaction.channel.id
        weapon = self.bot.database.get_weapon(channel_id)
        armor = self.bot.database.get_armor(channel_id)
        job = self.bot.database.get_job(channel_id)

        await interaction.response.send_message(
            f"```見た目：ネズミ\r\n名前：ネズミくん\r\n武器：{weapon}\r\n防具：{armor}\r\n職業：{job}```",
            ephemeral=False
        )


    @app_commands.command(
        name="武器を持たせる",
        description="ネズミに武器を持たせます。持てる武器は1つだけです。"
    )
    @app_commands.describe(weapon="持たせたい武器（最大30文字）")
    async def add_weapon(self, interaction: discord.Interaction, weapon:str):
        if len(weapon) > 30:
            await interaction.response.send_message(
                "武器の名前が長すぎます！30文字以内にしてください。",
                ephemeral=True
            )
        else:
            await interaction.response.defer()  # 入力中...の表示
            channel_id = interaction.channel.id
            before_weapon = self.bot.database.get_weapon(channel_id)  # 現在武器データをJSONから取得
            self.bot.database.set_weapon(channel_id, weapon) # 次にセットする武器
            reply = self.bot.chatAi.chat(channel_id, f"[システムメッセージ]貴方が持っている武器が「{before_weapon}」から「{weapon}」に変更されました。リアクションしてください。")
            reply = f"__**ネズミに{weapon}が与えられました**__\r\n\r\n" + reply

            await interaction.followup.send(
                reply,
                ephemeral=False
            )

    @app_commands.command(
        name="防具を持たせる",
        description="ネズミに防具を持たせます。持てる防具は1つだけです。"
    )
    @app_commands.describe(armor="持たせたい防具（最大30文字）")
    async def add_armor(self, interaction: discord.Interaction, armor: str):
        if len(armor) > 30:
            await interaction.response.send_message(
                "防具の名前が長すぎます！30文字以内にしてください。",
                ephemeral=True
            )
        else:
            await interaction.response.defer()
            channel_id = interaction.channel.id
            before_armor = self.bot.database.get_armor(channel_id)
            self.bot.database.set_armor(channel_id, armor)
            reply = self.bot.chatAi.chat(channel_id, f"[システムメッセージ]貴方が持っている防具が「{before_armor}」から「{armor}」に変更されました。リアクションしてください。")
            reply = f"__**ネズミに{armor}が与えられました**__\r\n\r\n" + reply

            await interaction.followup.send(
                reply,
                ephemeral=False
            )

    @app_commands.command(
        name="職業選択",
        description="ネズミに職業を与えます。持てる職業は1つだけです。"
    )
    @app_commands.describe(job="持たせたい職業（最大30文字）")
    async def add_job(self, interaction: discord.Interaction, job: str):
        if len(job) > 30:
            await interaction.response.send_message(
                "職業の名前が長すぎます！30文字以内にしてください。",
                ephemeral=True
            )
        else:
            await interaction.response.defer()
            channel_id = interaction.channel.id
            before_job = self.bot.database.get_job(channel_id)
            self.bot.database.set_job(channel_id, job)
            reply = self.bot.chatAi.chat(channel_id, f"[システムメッセージ]貴方の職業が「{before_job}」から「{job}」に変更されました。リアクションしてください。")
            reply = f"__**ネズミは{job}にジョブチェンジしました**__\r\n\r\n" + reply

            await interaction.followup.send(
                reply,
                ephemeral=False
            )

    @app_commands.command(
        name="食べ物を与える",
        description="ネズミに食べ物を与えます。"
    )
    @app_commands.describe(food="与える食べ物（最大30文字）")
    async def add_food(self, interaction: discord.Interaction, food: str):
        if len(food) > 30:
            await interaction.response.send_message(
                "食べ物の名前が長すぎます！30文字以内にしてください。",
                ephemeral=True
            )
        else:
            await interaction.response.defer()
            channel_id = interaction.channel.id
            before_fullness = self.bot.database.get_fullness(channel_id)
            self.bot.database.add_fullness(channel_id, 60)
            fullness = self.bot.database.get_fullness(channel_id)
            reply = self.bot.chatAi.chat(channel_id, f"[システムメッセージ]貴方に食事として「{food}」が与えられ、満腹度が{before_fullness}から{fullness}になりました。。リアクションしてください。")
            reply = f"__**ネズミに{food}が与えられました**__\r\n\r\n" + reply

            await interaction.followup.send(
                reply,
                ephemeral=False
            )

    @app_commands.command(
        name="夢オチ",
        description="最近の出来事を夢として忘れさせます（直近の会話履歴を削除します）"
    )
    async def reset_memory(self, interaction: discord.Interaction):
        await interaction.response.defer()
        channel_id = interaction.channel.id
        self.bot.database.reset_message_history(channel_id)
        reply = self.bot.chatAi.chat(
            channel_id,
            f"[システムメッセージ]あなたは悪い夢を見ていましたが、運良く忘れられました。リアクションしてください。")
        reply = f"__**ネズミくんは夢を見ていたようです。**__\r\n\r\n" + reply

        await interaction.followup.send(
            reply,
            ephemeral=False
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SetStatus(bot))

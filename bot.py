import discord
from discord import app_commands
from discord.ext import commands
import random
from dotenv import load_dotenv
import os

# 環境変数の読み込み
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# ボットの準備
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user.name} is ready!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(e)

@bot.tree.command(name="janken", description="じゃんけんをしましょう！")
async def janken(interaction: discord.Interaction):
    await interaction.response.send_message(
        "じゃんけんを開始します！以下の手から選んでください：\n1️⃣ グー\n2️⃣ チョキ\n3️⃣ パー\n選択肢をチャットで入力してください（例: 1）",
        ephemeral=True
    )

    # プレイヤーの選択を非公開で収集
    def check(message):
        return message.author == interaction.user and message.content in ["1", "2", "3"]

    try:
        reply = await bot.wait_for("message", timeout=30.0, check=check)
        user_choice_map = {"1": "グー", "2": "チョキ", "3": "パー"}
        user_choice = user_choice_map[reply.content]
    except asyncio.TimeoutError:
        await interaction.followup.send("時間切れです！もう一度お試しください。", ephemeral=True)
        return

    # ボットの手を選ぶ
    bot_choice = random.choice(["グー", "チョキ", "パー"])

    # 勝敗判定ロジック
    if user_choice == bot_choice:
        result = "引き分けです！"
    elif (user_choice == "グー" and bot_choice == "チョキ") or \
         (user_choice == "チョキ" and bot_choice == "パー") or \
         (user_choice == "パー" and bot_choice == "グー"):
        result = "あなたの勝ちです！"
    else:
        result = "あなたの負けです！"

    # 結果を非公開で送信
    await interaction.followup.send(
        f"あなたの手: {user_choice}\nボットの手: {bot_choice}\n結果: {result}",
        ephemeral=True
    )

# ボットを起動
bot.run(TOKEN)

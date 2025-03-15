import discord
from discord.ext import commands
import asyncio
import random
from dotenv import load_dotenv
import os

# 環境変数の読み込み
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# ボットの準備
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user.name} is ready!")

@bot.command()
async def janken(ctx):
    await ctx.send("じゃんけんを始めます！ボットがDMを送信しますので、そこでリアクションで手を選んでください！")

    # プレイヤー全員にDMを送信してリアクションを収集
    player_choices = {}
    reactions = ["👊", "✌️", "✋"]

    async def send_dm_and_wait(player):
        try:
            dm_message = await player.send(
                "じゃんけんの手をリアクションで選んでください！\n"
                "👊: グー\n"
                "✌️: チョキ\n"
                "✋: パー"
            )
            for reaction in reactions:
                await dm_message.add_reaction(reaction)

            def check(reaction, user):
                return user == player and str(reaction.emoji) in reactions

            reaction, user = await bot.wait_for("reaction_add", timeout=30.0, check=check)
            player_choices[player.id] = str(reaction.emoji)
            await player.send(f"あなたの選択: {reaction.emoji} を受け付けました！")
        except asyncio.TimeoutError:
            await player.send("時間切れです。手の選択ができませんでした。")

    # チャンネルの全メンバーにDMを送信
    tasks = []
    for member in ctx.guild.members:
        if not member.bot:
            tasks.append(send_dm_and_wait(member))

    await asyncio.gather(*tasks)

    # ボットの手をランダム選択
    bot_choice = random.choice(reactions)
    bot_hand_map = {"👊": "グー", "✌️": "チョキ", "✋": "パー"}
    await ctx.send(f"ボットの手は {bot_hand_map[bot_choice]} です！")

    # 勝敗判定ロジック
    win_table = {"👊": "✌️", "✌️": "✋", "✋": "👊"}
    results_message = ""

    for player_id, player_choice in player_choices.items():
        player = await bot.fetch_user(player_id)
        if player_choice == bot_choice:
            result = "引き分け"
        elif win_table[player_choice] == bot_choice:
            result = "勝利"
        else:
            result = "敗北"
        results_message += f"{player.display_name}: {result}（選んだ手: {bot_hand_map[player_choice]}）\n"

    # 結果を送信
    await ctx.send("結果:\n" + results_message)

# ボットを起動
bot.run(TOKEN)

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
    # メッセージ送信
    message = await ctx.send(
        "じゃんけんを始めます！リアクションで選んでください。\n"
        "👊: グー\n✌️: チョキ\n✋: パー"
    )

    # リアクションの追加
    reactions = ["👊", "✌️", "✋"]
    for reaction in reactions:
        await message.add_reaction(reaction)

    # リアクションの集計
    def check(reaction, user):
        return (
            reaction.message.id == message.id
            and str(reaction.emoji) in reactions
            and not user.bot
        )

    results = {}

    try:
        while True:
            # リアクションを待つ
            reaction, user = await bot.wait_for("reaction_add", timeout=30.0, check=check)
            if user.id not in results:
                results[user.id] = str(reaction.emoji)
                await ctx.send(f"{user.display_name} が選びました: {reaction.emoji}")
    except asyncio.TimeoutError:
        # ボットのじゃんけん選択
        bot_choice = random.choice(reactions)
        await ctx.send(f"ボットは {bot_choice} を選びました！\nじゃんけん終了！結果を確認しています...")

        # 勝敗判定の準備
        summary = {"👊": 0, "✌️": 0, "✋": 0}
        for choice in results.values():
            summary[choice] += 1

        # 最終結果の集計
        result_message = "結果:\n"
        for choice, count in summary.items():
            result_message += f"{choice}: {count}人\n"
        result_message += f"ボット: {bot_choice}\n"

        # プレイヤーごとの勝敗判定
        for user_id, user_choice in results.items():
            if user_choice == bot_choice:
                outcome = "引き分け"
            elif (user_choice == "👊" and bot_choice == "✌️") or \
                 (user_choice == "✌️" and bot_choice == "✋") or \
                 (user_choice == "✋" and bot_choice == "👊"):
                outcome = "勝ち"
            else:
                outcome = "負け"

            user = await bot.fetch_user(user_id)
            result_message += f"{user.display_name} の結果: {outcome}\n"

        await ctx.send(result_message)

# ボットを起動
bot.run(TOKEN)

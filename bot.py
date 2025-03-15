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
intents.guilds = True
intents.members = True  # メンバー情報を取得するため
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user.name} is ready!")

@bot.command()
async def janken(ctx):
    await ctx.send("じゃんけんを始めます！ボットがDMを送信しますので、リアクションで手を選んでください！")

    # プレイヤー全員にDMを送信し、リアクションで選択を受け取る
    player_choices = {}
    reactions = ["👊", "✌️", "✋"]
    hand_map = {"👊": "グー", "✌️": "チョキ", "✋": "パー"}

    async def send_dm_and_wait(player):
        try:
            # DM送信
            dm_message = await player.send(
                "じゃんけんの手をリアクションで選んでください！\n"
                "👊: グー\n"
                "✌️: チョキ\n"
                "✋: パー"
            )
            # リアクションを追加
            for reaction in reactions:
                await dm_message.add_reaction(reaction)

            # リアクションを待機
            def check(reaction, user):
                return user == player and str(reaction.emoji) in reactions

            reaction, user = await bot.wait_for("reaction_add", timeout=30.0, check=check)
            player_choices[player.id] = str(reaction.emoji)
            await player.send(f"あなたの選択: {reaction.emoji} ({hand_map[reaction.emoji]}) を受け付けました！")
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
    player_choices[bot.user.id] = bot_choice
    await ctx.send(f"ボットの手は {hand_map[bot_choice]} です！")

    # 勝敗判定ロジック
    win_table = {"👊": "✌️", "✌️": "✋", "✋": "👊"}
    all_hands = set(player_choices.values())
    strongest_hands = [
        hand for hand in all_hands if all(win_table[hand] != other for other in all_hands)
    ]

    results_message = ""
    if len(strongest_hands) == 1:
        # 勝利の手が1つの場合、勝者を判定
        winning_hand = strongest_hands[0]
        winners = [
            player_id
            for player_id, player_choice in player_choices.items()
            if player_choice == winning_hand
        ]
        results_message += f"勝利の手: {hand_map[winning_hand]}\n"
        results_message += "勝者:\n"
        for winner_id in winners:
            winner = await bot.fetch_user(winner_id)
            results_message += f"- {winner.display_name}\n"
    else:
        # 引き分けの場合
        results_message += "全員引き分けです！\n"

    # 結果を送信
    await ctx.send("結果:\n" + results_message)

# ボットを起動
bot.run(TOKEN)

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
                try:
                    await dm_message.add_reaction(reaction)
                except discord.HTTPException:
                    await player.send("リアクションの追加に失敗しました。もう一度お試しください。")
                    return

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
    all_hands = player_choices.values()

    # 各プレイヤーの結果を判定
    winners = []
    losers = []
    for player_id, player_choice in player_choices.items():
        is_winner = all(
            win_table[player_choice] == other_hand
            or player_choice == other_hand
            for other_hand in all_hands
        )
        if is_winner:
            winners.append(player_id)
        else:
            losers.append(player_id)

    # 結果メッセージの作成
    results_message = "各プレイヤーの選択:\n"
    for player_id, player_choice in player_choices.items():
        player = await bot.fetch_user(player_id)
        results_message += f"- {player.display_name}: {hand_map[player_choice]}\n"

    # 勝者と敗者の表示
    if winners:
        results_message += "\n**勝者:**\n"
        for winner_id in winners:
            winner = await bot.fetch_user(winner_id)
            results_message += f"- {winner.display_name}\n"
    if losers:
        results_message += "\n**敗者:**\n"
        for loser_id in losers:
            loser = await bot.fetch_user(loser_id)
            results_message += f"- {loser.display_name}\n"

    # 結果を送信
    await ctx.send("結果:\n" + results_message)

# ボットを起動
bot.run(TOKEN)

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
async def janken(ctx, *role_names):
    if not role_names:
        await ctx.send("少なくとも1つのロール名を指定してください。")
        return

    # 指定されたロールを取得
    target_roles = []
    for role_name in role_names:
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role:
            target_roles.append(role)
        else:
            await ctx.send(f"ロール '{role_name}' が見つかりませんでした。")

    if not target_roles:
        await ctx.send("指定されたロールが見つかりませんでした。")
        return

    await ctx.send(f"じゃんけんを始めます！指定されたロール: {', '.join([role.name for role in target_roles])} のメンバーにDMを送信します。")

    # 指定されたロールに属するメンバーにDMを送信し、リアクションで選択を受け取る
    player_choices = {}
    reactions = ["👊", "✌️", "✋"]

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
            await player.send(f"あなたの選択: {reaction.emoji} を受け付けました！")
        except asyncio.TimeoutError:
            await player.send("時間切れです。手の選択ができませんでした。")

    # 重複なくロール内の全メンバーにDMを送信
    tasks = []
    unique_members = set()
    for role in target_roles:
        for member in role.members:
            if not member.bot and member not in unique_members:
                unique_members.add(member)
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

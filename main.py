import os
import discord
import requests
import datetime
from discord.ext import commands, tasks
from flask import Flask
from threading import Thread

# === ENV VARIABLES ===
TOKEN = os.environ['DISCORD_TOKEN']
CHANNEL_ID = int(os.environ['CHANNEL_ID'])
PING_ROLE_ID = int(os.environ['PING_ROLE_ID'])

# === DISCORD BOT SETUP ===
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
notified_streams = set()

# === FLASK KEEP-ALIVE ===
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def keep_alive():
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()

# === CHECK STREAMS TASK ===
@tasks.loop(minutes=1)
async def check_streams():
    print("🔍 Checking Holodex for live streams...")
    try:
        headers = {
            "User-Agent": "HololiveBot/1.0 (contact: fexerzaza@gmail.com)"  # <-- put a real email if possible
        }
        url = "https://holodex.net/api/v2/live?org=Hololive&lang=en"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        streams = response.json()

        for stream in streams:
            video_id = stream.get("id")
            title = stream.get("title")
            channel_name = stream.get("channel", {}).get("name")
            start_time = datetime.datetime.fromisoformat(stream["start_actual"].replace("Z", "+00:00"))

            if video_id not in notified_streams:
                notified_streams.add(video_id)
                embed = get_embed_for_member(
                    name=channel_name,
                    title=title,
                    video_id=video_id,
                    channel_name=channel_name,
                    start_time=start_time
                )
                channel = bot.get_channel(CHANNEL_ID)
                if channel:
                    if PING_ROLE_ID:
                        await channel.send(content=f"<@&{PING_ROLE_ID}>", embed=embed)
                    else:
                        await channel.send(embed=embed)

    except Exception as e:
        print(f"❌ Error checking Holodex: {e}")

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user.name}")
    check_streams.start()

# === EMBED BUILDER ===
def get_embed_for_member(name, title, video_id, channel_name, start_time):
    styles = {
        "IRyS": {"title": "🌟 IRyS is live!", "desc": "💖 Nephilim time!", "color": 0xFF77AA},
        "Calliope Mori": {"title": "💀 Calli is streaming!", "desc": "🎤 Dead Beats rise!", "color": 0xFF0055},
        "Takanashi Kiara": {"title": "🔥 Kiara is on fire!", "desc": "🍗 Phoenix time!", "color": 0xFF8000},
        "Ninomae Ina'nis": {"title": "🎀 Ina is live!", "desc": "✨ Wahh~ comfy stream!", "color": 0x8A2BE2},
        "Hakos Baelz": {"title": "🧀 Chaos is here!", "desc": "🐭 Bae brings the storm!", "color": 0xFF2222},
        "Ouro Kronii": {"title": "🕰️ Kronii is live!", "desc": "⏳ Time for Kronii!", "color": 0x003366},
        "Shiori Novella": {"title": "📖 Shiori is streaming!", "desc": "💬 Story time chaos!", "color": 0xCC66FF},
        "Koseki Bijou": {"title": "💎 Bijou is live!", "desc": "🪨 Gem time begins!", "color": 0x00CCCC},
        "Nerissa Ravencroft": {"title": "🎶 Nerissa is singing!", "desc": "🪽 Angelic streams!", "color": 0x6600CC},
        "Fuwamoco": {"title": "🐶 FUWAMOCO are live!", "desc": "💞 Double fun!", "color": 0xFFB6C1},
        "Raora Panthera": {"title": "🐆 Raora is live!", "desc": "🔥 Let’s roar together!", "color": 0xFF4500},
        "Gigi Murin": {"title": "💡 Gigi is up to something!", "desc": "🔬 Genius chaos incoming!", "color": 0x00FFAA},
        "Cecilia Immergreen": {"title": "🌿 Cecilia is streaming!", "desc": "🍃 Calm vibes only~", "color": 0x228B22},
        "Elizabeth Rose Bloodflame": {"title": "🩸 Elizabeth awakens!", "desc": "🔥 Bloodflame rises!", "color": 0xB22222},
    }

    style = styles.get(name, {
        "title": f"🎥 {name} is now live!",
        "desc": "🔔 A Hololive EN stream has started!",
        "color": 0xFFFFFF
    })

    embed = discord.Embed(
        title=style["title"],
        description=f"{style['desc']}\n\n[🔴 Watch Now](https://youtube.com/watch?v={video_id})",
        color=style["color"]
    )
    embed.set_thumbnail(url=f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg")
    embed.add_field(name="📅 Stream Title", value=title, inline=False)
    embed.add_field(name="🕒 Started", value=f"<t:{int(start_time.timestamp())}:R>", inline=True)
    embed.add_field(name="📺 Channel", value=f"*{channel_name}*", inline=True)
    embed.set_footer(text="Hololive Stream Alert")
    return embed

# === STARTUP ===
keep_alive()
bot.run(TOKEN)

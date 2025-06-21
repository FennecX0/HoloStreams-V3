import os
import discord
import requests
import datetime
from discord.ext import commands, tasks
from flask import Flask
from threading import Thread

# ==== Config ====
TOKEN = os.environ['DISCORD_TOKEN']
CHANNEL_ID = int(os.environ['CHANNEL_ID'])
PING_ROLE_ID = int(os.environ['PING_ROLE_ID'])  # Or set to None
HOLODEX_API_KEY = os.getenv("HOLODEX_API_KEY")  # Optional but recommended

# ==== Channel Map ====
channel_map = {
    "IRyS": "UC8rcEBzJSleTkf_-agPM20g",
    "Calliope Mori": "UCL_qhgtOy0dy1Agp8vkySQg",
    "Takanashi Kiara": "UCHsx4Hqa-1ORjQTh9TYDhww",
    "Ninomae Ina’nis": "UCHOVbmmkV7tXxD9fQJz2A8g",
    "Hakos Baelz": "UCgmPnx-EEeOrZSg5Tiw7ZRQ",
    "Ouro Kronii": "UCmbs8T6MWqUHP1tIQvSgKrg",
    "Shiori Novella": "UCgnfPPb9JI3e9A4cXHnWbyg",
    "Koseki Bijou": "UC9p_lqQ0FEDz327Vgf5JwqA",
    "Nerissa Ravencroft": "UCtyWhCj3AqKh2dXctLkDt5Q",
    "Fuwamoco": "UCt9H_RpQzhxzlyBxFqrdHqA",
    "Raora Panthera": "UCy3ethBzZ1lOed7NmKx2bGQ",
    "Gigi Murin": "UCMGf5tU-vIMzh-BqRWE6gxQ",
    "Cecilia Immergreen": "UCbFWEJJPxvESx7hXKqz4AQQ",
    "Elizabeth Rose Bloodflame": "UCGpNHgrh78xvXKhxayXN9TQ",
}

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
notified_streams = {}

# ==== Flask Keep Alive ====
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def keep_alive():
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()

# ==== Holodex Stream Check ====
@tasks.loop(minutes=1)
async def check_streams():
    url = "https://holodex.net/api/v2/live?org=Hololive&lang=en"
    headers = {
        "User-Agent": "HololiveDiscordBot/1.0 (contact: fexerzaza@gmail.com)"  # Customize this
    }
    if HOLODEX_API_KEY:
        headers["X-API-Key"] = HOLODEX_API_KEY

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        streams = response.json()
        print(f"✅ Got {len(streams)} live streams from Holodex")

        for stream in streams:
            channel_id = stream["channel"]["id"]
            name = next((n for n, cid in channel_map.items() if cid == channel_id), None)

            if not name:
                print(f"⚠️ Skipping unknown channel: {channel_id}")
                continue

            video_id = stream["id"]
            title = stream["title"]

            if video_id not in notified_streams:
                print(f"🔔 New stream: {name} - {title}")
                notified_streams[video_id] = True
                start_time = datetime.datetime.fromisoformat(stream["start_actual"][:-1] + "+00:00")

                embed = get_embed_for_member(
                    name=name,
                    title=title,
                    video_id=video_id,
                    channel_name=stream["channel"]["name"],
                    start_time=start_time
                )

                channel = bot.get_channel(CHANNEL_ID)
                if channel:
                    if PING_ROLE_ID:
                        await channel.send(content=f"<@&{PING_ROLE_ID}>", embed=embed)
                    else:
                        await channel.send(embed=embed)
                else:
                    print(f"❌ Could not find channel ID {CHANNEL_ID}")

    except Exception as e:
        print(f"❌ Error checking Holodex: {e}")

@bot.event
async def on_ready():
    print(f"🤖 Logged in as {bot.user.name}")
    check_streams.start()

# ==== Embed Builder ====
def get_embed_for_member(name, title, video_id, channel_name, start_time):
    member_styles = {
        "IRyS": {"title": "🌟 IRyS is singing her heart out~!", "desc": "💖 Nephilim magic is live!", "color": 0xFF77AA},
        "Calliope Mori": {"title": "💀 Calli is dropping bars live!", "desc": "🎤 Join the Underworld concert!", "color": 0xFF0055},
        "Takanashi Kiara": {"title": "🔥 Kiara is cooking up content!", "desc": "🍗 Kikkeriki~ Time for Phoenix fun!", "color": 0xFF8000},
        "Ninomae Ina’nis": {"title": "🎀 Wah~! Ina is streaming!", "desc": "✨ Time for comfy tentacle vibes!", "color": 0x8A2BE2},
        "Hakos Baelz": {"title": "🧀 CHAOS TIME with Bae!!", "desc": "🐭 Let the madness begin!", "color": 0xFF2222},
        "Ouro Kronii": {"title": "🕰️ Kronii is live!", "desc": "🌌 Bend the timeline!", "color": 0x003366},
        "Shiori Novella": {"title": "📖 Shiori is telling stories!", "desc": "💬 Dive into her library~", "color": 0xCC66FF},
        "Koseki Bijou": {"title": "💎 Bijou is ROCKing out!", "desc": "🪨 Shiny gem time!", "color": 0x00CCCC},
        "Nerissa Ravencroft": {"title": "🎶 Nerissa is singing live!", "desc": "🪽 Angelic vocals await~", "color": 0x6600CC},
        "Fuwamoco": {"title": "🐶 FUWAMOCO are barking live!", "desc": "💞 Double the chaos~", "color": 0xFFB6C1},
        "Raora Panthera": {"title": "🐆 Raora is ROARING!", "desc": "🔥 Unleash the wild energy~", "color": 0xFF4500},
        "Gigi Murin": {"title": "💡 Gigi is up to something~", "desc": "🔬 Genius on stream!", "color": 0x00FFAA},
        "Cecilia Immergreen": {"title": "🌿 Cecilia is going green!", "desc": "🌱 Calm nature vibes~", "color": 0x228B22},
        "Elizabeth Rose Bloodflame": {"title": "🩸 Elizabeth rises!", "desc": "🔥 Embrace the Bloodflame!", "color": 0xB22222},
    }

    style = member_styles.get(name, {
        "title": f"🎥 {name} is now live!",
        "desc": "🔔 A new Hololive stream has started!",
        "color": 0xFFFFFF,
    })

    embed = discord.Embed(
        title=style["title"],
        description=f"{style['desc']}\n\n[🔴 Watch Stream](https://youtube.com/watch?v={video_id})",
        color=style["color"]
    )
    embed.set_thumbnail(url=f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg")
    embed.add_field(name="📅 Stream Title", value=title, inline=False)
    embed.add_field(name="🕒 Started", value=f"<t:{int(start_time.timestamp())}:R>", inline=True)
    embed.add_field(name="📺 Channel", value=f"*{channel_name}*", inline=True)
    embed.set_footer(text="Hololive Stream Alert")
    return embed

# ==== Start Bot ====
keep_alive()
bot.run(TOKEN)

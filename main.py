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
PING_ROLE_ID = int(os.environ['PING_ROLE_ID'])  # Or use None
YOUTUBE_API_KEY = os.environ['YOUTUBE_API_KEY']

# === CHANNEL MAP ===
channel_map = {
    # HoloEN
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

    # HoloID
    "Ayunda Risu": "UCOyYb1c43VlX9rc_lT6NKQw",
    "Moona Hoshinova": "UCP0BspO_AMEe3aQqqpo89Dg",
    "Airani Iofifteen": "UCAoy6rzhSf4ydcYjJw3WoVg",
    "Anya Melfissa": "UC727SQYUvx5pDDGQpTICNWg",
    "Pavolia Reine": "UChgTyjG-pdNvxxhdsXfHQ5Q",
    "Kaela Kovalskia": "UCZLZ8Jjx_RN2CXloOmgTHVg",
    "Kobo Kanaeru": "UCjLEmnpCNeisMxy134KPwWw",
    "Vestia Zeta": "UCTvHWSfBZgtxE4sILOaurIQ"
}

# === DISCORD BOT SETUP ===
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
notified_streams = {}

# === FLASK KEEP-ALIVE ===
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def keep_alive():
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()

# === CHECK STREAMS TASK ===
@tasks.loop(minutes=1)
async def check_streams():
    for name, channel_id in channel_map.items():
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&eventType=live&type=video&key={YOUTUBE_API_KEY}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if "items" in data and len(data["items"]) > 0:
                video = data["items"][0]
                video_id = video["id"]["videoId"]
                title = video["snippet"]["title"]

                if video_id not in notified_streams:
                    print(f"🔔 New stream: {name} — {title}")
                    notified_streams[video_id] = True
                    start_time = datetime.datetime.now(datetime.timezone.utc)

                    embed = get_embed_for_member(
                        name=name,
                        title=title,
                        video_id=video_id,
                        channel_name=video["snippet"]["channelTitle"],
                        start_time=start_time
                    )

                    channel = bot.get_channel(CHANNEL_ID)
                    if channel:
                        if PING_ROLE_ID:
                            await channel.send(content=f"<@&{PING_ROLE_ID}>", embed=embed)
                        else:
                            await channel.send(embed=embed)

        except Exception as e:
            print(f"❌ Error checking {name}: {e}")

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user.name}")
    check_streams.start()

# === EMBED BUILDER ===
def get_embed_for_member(name, title, video_id, channel_name, start_time):
    member_styles = {
        "IRyS": {"title": "🌟 IRyS is singing live!", "desc": "💖 Join the Nephilim vibes!", "color": 0xFF77AA},
        "Calliope Mori": {"title": "💀 Calli is rapping now!", "desc": "🎤 Dead Beats assemble!", "color": 0xFF0055},
        "Takanashi Kiara": {"title": "🔥 Kiara is live!", "desc": "🍗 Phoenix powers activate!", "color": 0xFF8000},
        "Ninomae Ina’nis": {"title": "🎀 Ina is streaming~", "desc": "✨ Grab your tentacles!", "color": 0x8A2BE2},
        "Hakos Baelz": {"title": "🧀 CHAOS is live!!", "desc": "🐭 Watch Bae go wild!", "color": 0xFF2222},
        "Ouro Kronii": {"title": "🕰️ Kronii controls time again", "desc": "🌌 It's clock time!", "color": 0x003366},
        "Shiori Novella": {"title": "📖 Shiori is live!", "desc": "💬 Dive into her book club!", "color": 0xCC66FF},
        "Koseki Bijou": {"title": "💎 Bijou is shining live!", "desc": "🪨 Rock hard, gem fans!", "color": 0x00CCCC},
        "Nerissa Ravencroft": {"title": "🎶 Nerissa is singing!", "desc": "🪽 Angelic streams await", "color": 0x6600CC},
        "Fuwamoco": {"title": "🐶 FUWAMOCO are live!!", "desc": "💞 Double trouble cuteness!", "color": 0xFFB6C1},
        "Raora Panthera": {"title": "🐆 Raora is roaring live!", "desc": "🔥 Wild stream energy!", "color": 0xFF4500},
        "Gigi Murin": {"title": "💡 Gigi is up to genius things!", "desc": "🔬 What is she building?!", "color": 0x00FFAA},
        "Cecilia Immergreen": {"title": "🌿 Cecilia is on!", "desc": "🌱 Peaceful plant time~", "color": 0x228B22},
        "Elizabeth Rose Bloodflame": {"title": "🩸 Elizabeth awakens!", "desc": "🔥 Bloodflame streams now!", "color": 0xB22222},

        # HoloID styles (optional)
        "Ayunda Risu": {"title": "🐿️ Risu is streaming!", "desc": "🌰 Nutty vibes~", "color": 0xD2691E},
        "Moona Hoshinova": {"title": "🌙 Moona shines live!", "desc": "💜 Moonlight chill!", "color": 0x4B0082},
        "Airani Iofifteen": {"title": "🎨 Iofi draws live!", "desc": "🖌️ Art and fun!", "color": 0xFF69B4},
        "Anya Melfissa": {"title": "📚 Anya is here!", "desc": "🔍 Mystery dagger energy~", "color": 0x8B4513},
        "Pavolia Reine": {"title": "🦚 Reine is streaming!", "desc": "👑 Royal tea time~", "color": 0x4682B4},
        "Kaela Kovalskia": {"title": "⛏️ Kaela keeps grinding!", "desc": "💪 Forge time!", "color": 0xFFD700},
        "Kobo Kanaeru": {"title": "💧 Kobo splashes live!", "desc": "🌧️ Rainy chaos incoming!", "color": 0x00BFFF},
        "Vestia Zeta": {"title": "🕵️ Zeta is on a mission!", "desc": "🎩 Agent stream live!", "color": 0x708090},
    }

    style = member_styles.get(name, {
        "title": f"🎥 {name} is now live!",
        "desc": "🔔 A new Hololive stream has started!",
        "color": 0xFFFFFF,
    })

    embed = discord.Embed(
        title=style["title"],
        description=f"{style['desc']}\n\n[🔴 Watch now](https://youtube.com/watch?v={video_id})",
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

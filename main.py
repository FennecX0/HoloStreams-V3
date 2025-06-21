import os
import discord
import requests
import datetime
from discord.ext import commands, tasks
from flask import Flask
from threading import Thread

TOKEN = os.environ['DISCORD_TOKEN']  # put your bot token in Secrets
CHANNEL_ID = int(os.environ['CHANNEL_ID'])  # stream alert channel ID
PING_ROLE_ID = int(os.environ['PING_ROLE_ID'])  # role to ping, or use None
YOUTUBE_API_KEY = os.environ['YOUTUBE_API_KEY']  # YouTube API Key

# YouTube Channel ID Map
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

    "Ayunda Risu": "UCOyYb1c43VlX9rc_lT6NKQw",
    "Moona Hoshinova": "UCP0BspO_AMEe3aQqqpo89Dg",
    "Airani Iofifteen": "UCAoy6rzhSf4ydcYjJw3WoVg",
    "Anya Melfissa": "UC727SQYUvx5pDDGQpTICNWg",
    "Pavolia Reine": "UChgTyjG-pdNvxxhdsXfHQ5Q",
    "Kaela Kovalskia": "UCZLZ8Jjx_RN2CXloOmgTHVg",
    "Kobo Kanaeru": "UCjLEmnpCNeisMxy134KPwWw",
    "Vestia Zeta": "UCTvHWSfBZgtxE4sILOaurIQ"
}

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
notified_streams = {}

# ========= FLASK KEEP-ALIVE ==========
app = Flask('')

@app.route('/')
def home():
    return "I'm alive!"

def keep_alive():
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()

# ========= YOUTUBE STREAM CHECK ==========
@tasks.loop(minutes=1)
async def check_streams():
    for name, channel_id in channel_map.items():
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&eventType=live&type=video&key={YOUTUBE_API_KEY}"
        response = requests.get(url).json()

        if "items" in response and len(response["items"]) > 0:
            video = response["items"][0]
            video_id = video["id"]["videoId"]
            title = video["snippet"]["title"]

            if video_id not in notified_streams:
                notified_streams[video_id] = True
                stream_start_time = datetime.datetime.utcnow()

                embed = get_embed_for_member(
                    name=name,
                    title=title,
                    video_id=video_id,
                    channel_name=video["snippet"]["channelTitle"],
                    start_time=stream_start_time
                )

                channel = bot.get_channel(CHANNEL_ID)
                if PING_ROLE_ID:
                    await channel.send(content=f"<@&{PING_ROLE_ID}>", embed=embed)
                else:
                    await channel.send(embed=embed)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    check_streams.start()

# ========= EMBED BUILDER ==========
def get_embed_for_member(name, title, video_id, channel_name, start_time):
    member_styles = {
        # --- Hololive EN ---
        "IRyS": {"title": "🌟 IRyS is singing her heart out~!", "desc": "💖 It's time for some Nephilim magic!", "color": 0xFF77AA},
        "Calliope Mori": {"title": "💀 Calli is dropping bars live!", "desc": "🎤 Join the Underworld concert now!", "color": 0xFF0055},
        "Takanashi Kiara": {"title": "🔥 Kiara is cooking up content!", "desc": "🍗 Kikkeriki~ It's time for some Phoenix fun!", "color": 0xFF8000},
        "Ninomae Ina’nis": {"title": "🎀 Wah~! Ina’nis is streaming now!", "desc": "✨ Grab your takodachis and join the comfy vibes!", "color": 0x8A2BE2},
        "Hakos Baelz": {"title": "🧀 CHAOS TIME with Bae!!", "desc": "🐭 Things are about to get wild!", "color": 0xFF2222},
        "Ouro Kronii": {"title": "🕰️ Kronii is bending time again~", "desc": "🌌 Step into the timeline with Kronii!", "color": 0x003366},
        "Shiori Novella": {"title": "📖 Shiori is telling stories again!", "desc": "💬 Let’s dive into her library of chaos~", "color": 0xCC66FF},
        "Koseki Bijou": {"title": "💎 Bijou is ROCKing out live!", "desc": "🪨 Shiny time with your favorite gem~", "color": 0x00CCCC},
        "Nerissa Ravencroft": {"title": "🎶 Nerissa's angelic voice is live!", "desc": "🪽 Tune in for heavenly vocals~", "color": 0x6600CC},
        "Fuwamoco": {"title": "🐶 FUWAMOCO are barking live!!", "desc": "💞 Double the chaos, double the fun~", "color": 0xFFB6C1},
        "Raora Panthera": {"title": "🐆 Raora is ROARING live!", "desc": "🔥 Unleash the wild energy~", "color": 0xFF4500},
        "Gigi Murin": {"title": "💡 Gigi is up to something interesting~", "desc": "🔬 Come see what this genius is doing live!", "color": 0x00FFAA},
        "Cecilia Immergreen": {"title": "🌿 Cecilia is going green on stream!", "desc": "🌱 Nature and calm with Cecilia~", "color": 0x228B22},
        "Elizabeth Rose Bloodflame": {"title": "🩸 Elizabeth is streaming from the shadows~", "desc": "🔥 Embrace the Bloodflame!", "color": 0xB22222},

        # --- Hololive ID ---
        "Ayunda Risu": {"title": "🐿️ Risu is being nutty live!", "desc": "🌰 Come vibe with the squirrel~", "color": 0xD2691E},
        "Moona Hoshinova": {"title": "🌙 Moona is shining live!", "desc": "💜 Chill space energy incoming~", "color": 0x4B0082},
        "Airani Iofifteen": {"title": "🎨 Iofi is creating cuteness!", "desc": "🖌️ Come join her art stream~", "color": 0xFF69B4},
        "Anya Melfissa": {"title": "📚 Anya is live with mystery~", "desc": "💬 Cozy time with the dagger!", "color": 0x8B4513},
        "Pavolia Reine": {"title": "🦚 Reine is cooking big brain things!", "desc": "👑 Join the royal tea time~", "color": 0x4682B4},
        "Kaela Kovalskia": {"title": "⛏️ Kaela never stops streaming!", "desc": "💪 Forge with the blacksmith queen~", "color": 0xFFD700},
        "Kobo Kanaeru": {"title": "💧 Kobo is splashing chaos!", "desc": "🌧️ Weather report: 100% Kobo!", "color": 0x00BFFF},
        "Vestia Zeta": {"title": "🕵️ Zeta is on a secret mission!", "desc": "🎩 The agent is live~", "color": 0x708090},
    }

    style = member_styles.get(name, {
        "title": f"🎥 {name} is now live!",
        "desc": "🔔 A new Hololive stream has started!",
        "color": 0xFFFFFF,
    })

    embed = discord.Embed(
        title=style["title"],
        description=f"{style['desc']}\n\n[🔴 Click to watch!](https://youtube.com/watch?v={video_id})",
        color=style["color"]
    )

    embed.set_thumbnail(url=f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg")
    embed.add_field(name="📅 Stream Title", value=title, inline=False)
    embed.add_field(name="🕒 Started", value=f"<t:{int(start_time.timestamp())}:R>", inline=True)
    embed.add_field(name="📺 Channel", value=f"*{channel_name}*", inline=True)
    embed.set_footer(text="Hololive Stream Alert")
    return embed

# ========= START ==========
keep_alive()
bot.run(TOKEN)

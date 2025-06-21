import discord
from discord.ext import commands, tasks
import requests
import os
from flask import Flask
from threading import Thread

# === Keep-Alive for Railway ===
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive~ ✨"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run).start()

# === Discord Bot Setup ===
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot is online as {bot.user}')
    check_streams.start()

# === Railway Secrets ===
YOUTUBE_API_KEY = os.environ['YOUTUBE_API_KEY']
CHANNEL_ID = os.environ['CHANNEL_ID']
PING_ROLE_ID = os.environ['PING_ROLE_ID']

# === Hololive EN & ID Members with Cute Messages ===
tracked_channels = {
    # --- Hololive English ---
    "Calliope Mori":        ["UCL_qhgtOy0dy1Agp8vkySQg", "🎤 Dead Beats assemble! Calli is spitting fire LIVE! 💀🔥"],
    "IRyS":                 ["UC8rcEBzJSleTkf_-agPM20g", "💎 Hope descends! IRyS is blessing us with her heavenly voice~ 🎶✨"],
    "Ninomae Ina’nis":      ["UCHsx4Hqa-1ORjQTh9TYDhww", "🐙 Wah~! Good morning, afternoon, evening! Hope you're having a WAHnderful day, because our cute, Ina is live! 🐙 💜"],
    "Takanashi Kiara":      ["UCE5k0-l0YKO6h7gR4lA1B5g", "🔥 Kikkeriki~ Your phoenix idol is blazing LIVE! 🐔✨"],
    "Ouro Kronii":          ["UCmbs8T6MWqUHP1tIQvSgKrg", "🕰️ The clock is ticking... Kronii is LIVE and in control! 💙⌛"],
    "Hakos Baelz":          ["UCgmPnx-EEeOrZSg5Tiw7ZRQ", "🐭 CHAO~S is LIVE! Bae is unleashing mayhem right now! 💥🎲"],
    "Fuwamoco Ch.":         ["UCt9H1n2lF8G0wlBKzZ4WAtw", "🐶 Double the barks, double the love! FUWAMOCO are LIVE! 🐾💕"],
    "Shiori Novella":       ["UCibY_L7rZHX0bh1ZwI_p8nQ", "📖 Gather round~ Shiori's mystery-filled stream begins~ 🕯️💌"],
    "Koseki Bijou":         ["UCmeyo5pRj_6PXG-CsGUuWWg", "💠 Our lil’ gemstone adventurer is LIVE! Let Bijou dazzle you~ 💎🌟"],
    "Nerissa Ravencroft":   ["UCg63a3lk6PNeWhVvMRMep7A", "🎼 Songbird of secrets is LIVE! Nerissa’s voice awaits~ 🖤🎤"],
    "Raora Panthera":       ["UCJ6zA3tR3dLkVfP1b5xzIzQ", "🦁 The jungle queen is roaring LIVE — Raora's on the prowl! 💛🔥"],
    "Cecilia Immergreen":   ["UCNZu3BBym8GJN3Af5EyuWdA", "🌿 Nature’s elegance blooms! Cecilia is LIVE and serene~ 🍃💫"],
    "Gigi Murin":           ["UClxw1GMxXTF-Gd2ez5K6F6g", "🌙 It's Gigi time! She's cooking up magical chaos~ ✨💭"],
    "Elizabeth Roseblood":  ["UCeB2JzPZ1sD1nQ5tDg6wxZQ", "🦇 Noble shadows stir... Elizabeth is streaming now~ 🌹🕯️"],

    # --- Hololive Indonesia ---
    "Ayunda Risu":          ["UCOyYb1c43VlX9rc_lT6NKQw", "🐿️ Risu’s nutty antics are LIVE! You *better* bring snacks~ 🌰🤣"],
    "Moona Hoshinova":      ["UCP0BspO_AMEe3aQqqpo89Dg", "🌕 MOONAAA POWER~ She’s LIVE with cosmic calm! 🛰️💜"],
    "Airani Iofifteen":     ["UCAoy6rzhSf4ydcYjJw3WoVg", "🎨 Iofi’s art and chaos energy are now LIVE~ Moe-tastic! 🖌️💖"],
    "Anya Melfissa":        ["UC727SQYUvx5pDDGQpTICNWg", "🔪 Beware~ Anya’s sleepy slashes are back! LIVE & sharp! 💢🗡️"],
    "Kureiji Ollie":        ["UCYz_5n-uDuChHtLo7My1HnQ", "🧟 CRAZY ZOMBIE ENERGY UNLEASHED! Ollie is LIVE! 🧠⚡"],
    "Kaela Kovalskia":      ["UCZLZ8Jjx_RN2CXloOmgTHVg", "⛏️ Kaela grind? Eternal. LIVE stream? Eternal-er. 🛠️😎"],
    "Kobo Kanaeru":         ["UCjLEmnpCNeisMxy134KPwWw", "💧 Your Indonesian rain shaman is LIVE~ Bring an umbrella ☔💙"]
}

announced_streams = []

@tasks.loop(minutes=2)
async def check_streams():
    for name, (channel_id, message) in tracked_channels.items():
        url = (
            f"https://www.googleapis.com/youtube/v3/search?"
            f"key={YOUTUBE_API_KEY}&channelId={channel_id}"
            f"&part=snippet&eventType=live&type=video"
        )
        try:
            res = requests.get(url)
            data = res.json()

            if "items" in data and data["items"]:
                stream = data["items"][0]
                video_id = stream["id"]["videoId"]

                if video_id not in announced_streams:
                    announced_streams.append(video_id)

                    embed = discord.Embed(
                        title=f"{name} is now LIVE!",
                        description="🎥 Click the link to join the fun!",
                        url=f"https://www.youtube.com/watch?v={video_id}",
                        color=discord.Color.purple()
                    )
                    embed.set_thumbnail(url=stream["snippet"]["thumbnails"]["high"]["url"])
                    embed.set_footer(text="💌 Powered by Hololive EN & ID Notifier Bot")

                    channel = bot.get_channel(int(CHANNEL_ID))
                    await channel.send(f"<@&{PING_ROLE_ID}> {message}", embed=embed)

        except Exception as e:
            print(f"[ERROR] Failed to check {name}: {e}")

# === Launch bot ===
keep_alive()
bot.run(os.environ['DISCORD_TOKEN'])

